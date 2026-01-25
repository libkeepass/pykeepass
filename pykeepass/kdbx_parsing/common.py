from __future__ import annotations

import base64
import codecs
import hashlib
import io
import logging
import re
import zlib
from binascii import Error as BinasciiError
from collections import OrderedDict
from copy import deepcopy
from typing import TYPE_CHECKING, Any, BinaryIO, Callable, cast

from construct import (
    Adapter,
    BitsSwapped,
    BitStruct,
    Container,
    Flag,
    GreedyBytes,
    Int32ul,
    ListContainer,
    Mapping,
    Padding,
    Switch,
)
from Cryptodome.Cipher import AES, ChaCha20, Salsa20
from Cryptodome.Util import Padding as CryptoPadding
from lxml import etree

from .twofish import Twofish, python_Twofish

if TYPE_CHECKING:
    from construct import Construct, Context

log = logging.getLogger(__name__)


class HeaderChecksumError(Exception):
    pass


class CredentialsError(Exception):
    pass


class PayloadChecksumError(Exception):
    pass


class DynamicDict(
    Adapter[ListContainer[Any], ListContainer[Any], Container[Any], Container[Any]]
    if TYPE_CHECKING
    else Adapter
):
    """ListContainer <---> Container
    Convenience mapping so we dont have to iterate ListContainer to find
    the right item

    FIXME: lump kwarg was added to get around the fact that InnerHeader is
    not truly a dict.  We lump all 'binary' InnerHeaderItems into a single list
    """

    def __init__(
        self,
        key: str,
        subcon: Construct[ListContainer[Any], ListContainer[Any]],
        lump: list[str] | None = None,
    ) -> None:
        super().__init__(subcon)
        self.key: str = key
        self.lump: list[str] = lump if lump is not None else []

    # map ListContainer to Container
    def _decode(
        self, obj: ListContainer[Any], context: Context, path: str
    ) -> Container[Any]:
        d: OrderedDict[str, Any] = OrderedDict()
        for item_key in self.lump:
            d[item_key] = ListContainer([])
        for item in obj:
            if item[self.key] in self.lump:
                d[item[self.key]].append(item)
            else:
                d[item[self.key]] = item

        return Container(d)

    # map Container to ListContainer
    def _encode(
        self, obj: Container[Any], context: Context, path: str
    ) -> ListContainer[Any]:
        items_list: list[Any] = []
        for key in obj:
            if key in self.lump:
                items_list += obj[key]
            else:
                items_list.append(obj[key])

        return ListContainer(items_list)


def Reparsed(
    subcon_out: Construct[Any, Any],
) -> type[Adapter[bytes, bytes, Any, Any]]:
    class Reparsed(Adapter[bytes, bytes, Any, Any] if TYPE_CHECKING else Adapter):
        """Bytes <---> Parsed subcon result
        Takes in bytes and reparses it with subcon_out"""

        def _decode(self, obj: bytes, context: Context, path: str) -> Any:
            return subcon_out.parse(obj, **context)

        def _encode(self, obj: Any, context: Context, path: str) -> bytes:
            return subcon_out.build(obj, **context)

    return Reparsed


# is the payload compressed?
CompressionFlags = BitsSwapped(BitStruct("compression" / Flag, Padding(8 * 4 - 1)))


# -------------------- Key Computation --------------------
def aes_kdf(key: bytes, rounds: int, key_composite: bytes) -> bytes:
    """Set up a context for AES128-ECB encryption to find transformed_key"""

    cipher = AES.new(key, AES.MODE_ECB)  # pyright: ignore[reportUnknownMemberType]
    # get the number of rounds from the header and transform the key_composite
    transformed_key = key_composite
    for _ in range(0, rounds):
        transformed_key = cipher.encrypt(transformed_key)
    return hashlib.sha256(transformed_key).digest()


def compute_key_composite(
    password: str | None = None, keyfile: str | BinaryIO | None = None
) -> bytes:
    """Compute composite key.
    Used in header verification and payload decryption."""

    # hash the password
    if password is not None:
        password_composite = hashlib.sha256(password.encode("utf-8")).digest()
    else:
        password_composite = b""
    # hash the keyfile
    if keyfile:
        if isinstance(keyfile, (str, bytes)) or hasattr(keyfile, "__fspath__"):
            # keyfile is a string path, bytes path, or PathLike object
            with open(cast(str, keyfile), "rb") as f:
                keyfile_bytes = f.read()
        else:
            # keyfile is a file-like object
            if hasattr(keyfile, "seekable") and keyfile.seekable():
                keyfile.seek(0)
            keyfile_bytes = keyfile.read()
        # try to read XML keyfile
        try:
            tree = etree.fromstring(keyfile_bytes)
            version_elem = tree.find("Meta/Version")
            data_element = tree.find("Key/Data")
            if version_elem is None or version_elem.text is None:
                raise AttributeError("Invalid version in keyfile")
            version = version_elem.text
            if version.startswith("1.0"):
                if data_element is None or data_element.text is None:
                    raise AttributeError("Invalid keyfile data")
                keyfile_composite = base64.b64decode(data_element.text)
            elif version.startswith("2.0"):
                # read keyfile data and convert to bytes
                if data_element is None or data_element.text is None:
                    raise AttributeError("Invalid keyfile data")
                keyfile_composite = bytes.fromhex(data_element.text.strip())
                # validate bytes against hash
                hash_str = data_element.attrib.get("Hash")
                if hash_str is None:
                    raise AttributeError("Missing hash attribute")
                hash = bytes.fromhex(hash_str)
                hash_computed = hashlib.sha256(keyfile_composite).digest()[:4]
                assert hash == hash_computed, "Keyfile has invalid hash"
            else:
                raise AttributeError("Invalid version in keyfile")
        # otherwise, try to read plain keyfile
        except (etree.XMLSyntaxError, UnicodeDecodeError, AttributeError):
            try:
                try:
                    int(keyfile_bytes, 16)
                    is_hex = True
                except ValueError:
                    is_hex = False
                # if the length is 32 bytes we assume it is the key
                if len(keyfile_bytes) == 32:
                    keyfile_composite = keyfile_bytes
                # if the length is 64 bytes we assume the key is hex encoded
                elif len(keyfile_bytes) == 64 and is_hex:
                    keyfile_composite = codecs.decode(keyfile_bytes, "hex")
                # anything else may be a file to hash for the key
                else:
                    keyfile_composite = hashlib.sha256(keyfile_bytes).digest()
            except Exception:
                raise IOError("Could not read keyfile")

    else:
        keyfile_composite = b""

    # create composite key from password and keyfile composites
    return hashlib.sha256(password_composite + keyfile_composite).digest()


def compute_master(context: Context) -> bytes:
    """Computes master key from transformed key and master seed.
    Used in payload decryption."""

    # combine the transformed key with the header master seed to find the master_key
    master_key = hashlib.sha256(
        context._.header.value.dynamic_header.master_seed.data + context.transformed_key
    ).digest()
    return master_key


# -------------------- XML Processing --------------------


class XML(
    Adapter[bytes, bytes, etree.ElementTree, etree.ElementTree]
    if TYPE_CHECKING
    else Adapter
):
    """Bytes <---> lxml etree"""

    def _decode(self, obj: bytes, context: Context, path: str) -> etree.ElementTree:
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(io.BytesIO(obj), parser)

    def _encode(self, obj: etree.ElementTree, context: Context, path: str) -> bytes:
        return etree.tostring(obj)


class UnprotectedStream(
    Adapter[etree.ElementTree, etree.ElementTree, etree.ElementTree, etree.ElementTree]
    if TYPE_CHECKING
    else Adapter
):
    """lxml etree <---> unprotected lxml etree
    Iterate etree for Protected elements and decrypt using cipher
    provided by get_cipher"""

    protected_xpath: str = "//Value[@Protected='True']"

    def __init__(
        self,
        protected_stream_key: Callable[[Context], bytes],
        subcon: Construct[Any, Any],
    ) -> None:
        super().__init__(subcon)
        self.protected_stream_key: Callable[[Context], bytes] = protected_stream_key

    def _decode(
        self, obj: etree.ElementTree, context: Context, path: str
    ) -> etree.ElementTree:
        cipher = self.get_cipher(self.protected_stream_key(context))
        for elem in obj.xpath(self.protected_xpath):
            if elem.text is not None:
                try:
                    result = cipher.decrypt(base64.b64decode(elem.text)).decode("utf-8")
                    # strip invalid XML characters - https://stackoverflow.com/questions/8733233
                    result = re.sub(
                        "[^\u0020-\ud7ff\u0009\u000a\u000d\ue000-\ufffd\U00010000-\U0010ffff]+",
                        "",
                        result,
                    )
                    elem.text = result
                except (UnicodeDecodeError, BinasciiError, ValueError):
                    # FIXME: this should be a warning eventually, need to fix all databases in tests/ first
                    log.error(
                        "Element at {} marked as protected, but could not unprotect".format(
                            obj.getpath(elem)
                        )
                    )
        return obj

    def _encode(
        self, obj: etree.ElementTree, context: Context, path: str
    ) -> etree.ElementTree:
        tree_copy = deepcopy(obj)
        cipher = self.get_cipher(self.protected_stream_key(context))
        for elem in tree_copy.xpath(self.protected_xpath):
            if elem.text is not None:
                elem.text = base64.b64encode(
                    cipher.encrypt(elem.text.encode("utf-8"))
                ).decode("ascii")
        return tree_copy

    def get_cipher(self, protected_stream_key: bytes) -> Any:
        raise NotImplementedError("Subclasses must implement get_cipher")


class ARCFourVariantStream(UnprotectedStream):
    def get_cipher(self, protected_stream_key: bytes) -> Any:
        raise Exception("ARCFourVariant not implemented")


# https://github.com/dlech/KeePass2.x/blob/97141c02733cd3abf8d4dce1187fa7959ded58a8/KeePassLib/Cryptography/CryptoRandomStream.cs#L115-L119
class Salsa20Stream(UnprotectedStream):
    def get_cipher(self, protected_stream_key: bytes) -> Salsa20.Salsa20Cipher:
        key = hashlib.sha256(protected_stream_key).digest()
        return Salsa20.new(key=key, nonce=b"\xe8\x30\x09\x4b\x97\x20\x5d\x2a")


# https://github.com/dlech/KeePass2.x/blob/97141c02733cd3abf8d4dce1187fa7959ded58a8/KeePassLib/Cryptography/CryptoRandomStream.cs#L103-L111
class ChaCha20Stream(UnprotectedStream):
    def get_cipher(self, protected_stream_key: bytes) -> ChaCha20.ChaCha20Cipher:
        key_hash = hashlib.sha512(protected_stream_key).digest()
        key = key_hash[:32]
        nonce = key_hash[32:44]
        return ChaCha20.new(key=key, nonce=nonce)


def Unprotect(
    protected_stream_id: Any,
    protected_stream_key: Callable[[Context], bytes],
    subcon: Construct[Any, Any],
) -> Construct[Any, Any]:
    """Select stream cipher based on protected_stream_id"""

    return Switch(
        protected_stream_id,
        {
            "arcfourvariant": ARCFourVariantStream(protected_stream_key, subcon),
            "salsa20": Salsa20Stream(protected_stream_key, subcon),
            "chacha20": ChaCha20Stream(protected_stream_key, subcon),
        },
        default=subcon,
    )


# -------------------- Payload Encryption/Decompression --------------------


class Concatenated(
    Adapter["list[Any]", "list[Any]", bytes, bytes] if TYPE_CHECKING else Adapter
):
    """Data Blocks <---> Bytes"""

    def _decode(self, obj: list[Any], context: Context, path: str) -> bytes:
        return b"".join([block.block_data for block in obj])

    def _encode(self, obj: bytes, context: Context, path: str) -> list[Any]:
        blocks: list[Any] = []
        # split obj into 1 MB blocks (spec default)
        i = 0
        while i < len(obj):
            blocks.append(Container(block_data=obj[i : i + 2**20]))
            i += 2**20
        blocks.append(Container(block_data=b""))

        return blocks


class DecryptedPayload(
    Adapter[bytes, bytes, bytes, bytes] if TYPE_CHECKING else Adapter
):
    """Encrypted Bytes <---> Decrypted Bytes"""

    def get_cipher(self, master_key: bytes, encryption_iv: bytes) -> Any:
        raise NotImplementedError("Subclasses must implement get_cipher")

    def pad(self, data: bytes) -> bytes:
        raise NotImplementedError("Subclasses must implement pad")

    def unpad(self, data: bytes) -> bytes:
        raise NotImplementedError("Subclasses must implement unpad")

    def _decode(self, obj: bytes, context: Context, path: str) -> bytes:
        cipher = self.get_cipher(
            context.master_key,
            context._.header.value.dynamic_header.encryption_iv.data,
        )
        obj = cipher.decrypt(obj)
        # FIXME: Construct ugliness.  Fixes #244.  First 32 bytes of decrypted kdbx3 payload
        # should be checked against stream_start_bytes for a CredentialsError.  Due to construct
        # limitations, we have to decrypt the whole payload in order to check the first 32 bytes.
        # However, when the credentials are wrong the invalid decrypted payload cannot
        # be unpadded correctly.  Instead, catch the unpad ValueError exception raised by unpad()
        # and allow kdbx3.py to raise a ChecksumError
        try:
            obj = self.unpad(obj)
        except ValueError:
            log.debug("Decryption unpadding failed")

        return obj

    def _encode(self, obj: bytes, context: Context, path: str) -> bytes:
        obj = self.pad(obj)
        cipher = self.get_cipher(
            context.master_key,
            context._.header.value.dynamic_header.encryption_iv.data,
        )
        obj = cipher.encrypt(obj)

        return obj


class AES256Payload(DecryptedPayload):
    def get_cipher(self, master_key: bytes, encryption_iv: bytes) -> Any:
        return AES.new(master_key, AES.MODE_CBC, encryption_iv)  # pyright: ignore[reportUnknownMemberType]

    def pad(self, data: bytes) -> bytes:
        return CryptoPadding.pad(data, 16)

    def unpad(self, data: bytes) -> bytes:
        return CryptoPadding.unpad(data, 16)


class ChaCha20Payload(DecryptedPayload):
    def get_cipher(
        self, master_key: bytes, encryption_iv: bytes
    ) -> ChaCha20.ChaCha20Cipher:
        return ChaCha20.new(key=master_key, nonce=encryption_iv)

    def pad(self, data: bytes) -> bytes:
        return data

    def unpad(self, data: bytes) -> bytes:
        return data


class TwoFishPayload(DecryptedPayload):
    def get_cipher(self, master_key: bytes, encryption_iv: bytes) -> python_Twofish:
        return Twofish.new(master_key, mode=Twofish.MODE_CBC, iv=encryption_iv)

    def pad(self, data: bytes) -> bytes:
        return CryptoPadding.pad(data, 16)

    def unpad(self, data: bytes) -> bytes:
        return CryptoPadding.unpad(data, 16)


class Decompressed(Adapter[bytes, bytes, bytes, bytes] if TYPE_CHECKING else Adapter):
    """Compressed Bytes <---> Decompressed Bytes"""

    def _decode(self, obj: bytes, context: Context, path: str) -> bytes:
        return zlib.decompress(obj, 16 + 15)

    def _encode(self, obj: bytes, context: Context, path: str) -> bytes:
        compressobj = zlib.compressobj(6, zlib.DEFLATED, 16 + 15, zlib.DEF_MEM_LEVEL, 0)
        obj = compressobj.compress(obj)
        obj += compressobj.flush()
        return obj


# -------------------- Cipher Enums --------------------

# payload encryption method
# https://github.com/keepassxreboot/keepassxc/blob/8324d03f0a015e62b6182843b4478226a5197090/src/format/KeePass2.cpp#L24-L26
CipherId = Mapping(
    GreedyBytes,
    {
        "aes256": b"1\xc1\xf2\xe6\xbfqCP\xbeX\x05!j\xfcZ\xff",
        "twofish": b"\xadh\xf2\x9fWoK\xb9\xa3j\xd4z\xf9e4l",
        "chacha20": b"\xd6\x03\x8a+\x8boL\xb5\xa5$3\x9a1\xdb\xb5\x9a",
    },
)

# protected entry encryption method
# https://github.com/dlech/KeePass2.x/blob/149ab342338ffade24b44aaa1fd89f14b64fda09/KeePassLib/Cryptography/CryptoRandomStream.cs#L35
ProtectedStreamId = Mapping(
    Int32ul,
    {
        "none": 0,
        "arcfourvariant": 1,
        "salsa20": 2,
        "chacha20": 3,
    },
)
