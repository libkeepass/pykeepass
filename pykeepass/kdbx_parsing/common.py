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

from .twofish import Twofish

log = logging.getLogger(__name__)


class HeaderChecksumError(Exception):
    pass


class CredentialsError(Exception):
    pass


class PayloadChecksumError(Exception):
    pass


class DynamicDict(Adapter):
    """ListContainer <---> Container
    Convenience mapping so we dont have to iterate ListContainer to find
    the right item

    FIXME: lump kwarg was added to get around the fact that InnerHeader is
    not truly a dict.  We lump all 'binary' InnerHeaderItems into a single list
    """

    def __init__(self, key, subcon, lump=[]):
        super().__init__(subcon)
        self.key = key
        self.lump = lump

    # map ListContainer to Container
    def _decode(self, obj, context, path):
        d = OrderedDict()
        for l in self.lump:
            d[l] = ListContainer([])
        for item in obj:
            if item[self.key] in self.lump:
                d[item[self.key]].append(item)
            else:
                d[item[self.key]] = item

        return Container(d)

    # map Container to ListContainer
    def _encode(self, obj, context, path):
        l = []
        for key in obj:
            if key in self.lump:
                l += obj[key]
            else:
                l.append(obj[key])

        return ListContainer(l)


def Reparsed(subcon_out):
    class Reparsed(Adapter):
        """Bytes <---> Parsed subcon result
        Takes in bytes and reparses it with subcon_out"""

        def _decode(self, data, con, path):
            return subcon_out.parse(data, **con)

        def _encode(self, obj, con, path):
            return subcon_out.build(obj, **con)

    return Reparsed


# is the payload compressed?
CompressionFlags = BitsSwapped(
    BitStruct("compression" / Flag, Padding(8 * 4 - 1))
)


# -------------------- Key Computation --------------------
def aes_kdf(key, rounds, key_composite):
    """Set up a context for AES128-ECB encryption to find transformed_key"""

    cipher = AES.new(key, AES.MODE_ECB)

    # get the number of rounds from the header and transform the key_composite
    transformed_key = key_composite
    for _ in range(0, rounds):
        transformed_key = cipher.encrypt(transformed_key)

    return hashlib.sha256(transformed_key).digest()


def compute_keyfile_part_of_composite(keyfile):
    """Compute just a keyfile's contribution to a database composite key."""
    if hasattr(keyfile, "read"):
        if hasattr(keyfile, "seekable") and keyfile.seekable():
            keyfile.seek(0)
        keyfile_bytes = keyfile.read()
    else:
        with open(keyfile, 'rb') as f:
            keyfile_bytes = f.read()
    # try to read XML keyfile
    try:
        tree = etree.fromstring(keyfile_bytes)
        version = tree.find('Meta/Version').text
        data_element = tree.find('Key/Data')
        if version.startswith('1.0'):
            return base64.b64decode(data_element.text)
        elif version.startswith('2.0'):
            # read keyfile data and convert to bytes
            keyfile_composite = bytes.fromhex(data_element.text.strip())
            # validate bytes against hash
            hash = bytes.fromhex(data_element.attrib['Hash'])
            hash_computed = hashlib.sha256(keyfile_composite).digest()[:4]
            assert hash == hash_computed, "Keyfile has invalid hash"
            return keyfile_composite
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
                return keyfile_bytes
            # if the length is 64 bytes we assume the key is hex encoded
            elif len(keyfile_bytes) == 64 and is_hex:
                return codecs.decode(keyfile_bytes, 'hex')
            # anything else may be a file to hash for the key
            else:
                return hashlib.sha256(keyfile_bytes).digest()
        except:
            raise IOError('Could not read keyfile')


def compute_key_composite(password=None, keyfile=None, additional_parts=None):
    """Compute composite key.
    Used in header verification and payload decryption."""

    # hash the password
    if password:
        password_composite = hashlib.sha256(password.encode('utf-8')).digest()
    else:
        password_composite = b''
    # hash the keyfile
    keyfile_composite = compute_keyfile_part_of_composite(keyfile) if keyfile else b''

    # create composite key from password, keyfile, and other composites
    overall_composite = password_composite + keyfile_composite
    if additional_parts is not None:
        for part in additional_parts:
            overall_composite += part

    return hashlib.sha256(overall_composite).digest()


def compute_master(context):
    """Computes master key from transformed key and master seed.
    Used in payload decryption."""

    # combine the transformed key with the header master seed to find the master_key
    master_key = hashlib.sha256(
        context._.header.value.dynamic_header.master_seed.data +
        context.transformed_key).digest()
    return master_key


def populate_custom_data(kdbx, d):
    if len(d.keys()) > 0:
        vd = Container(
            version=b'\x00\x01',
            dict=d,
        )
        kdbx.header.value.dynamic_header.update(
            {
                "public_custom_data":
                    Container(
                        id='public_custom_data',
                        data=vd,
                        next_byte=0xFF,
                    )
            }
        )
    else:
        # Removing header entirely
        if "public_custom_data" in kdbx.header.value.dynamic_header:
            del kdbx.header.value.dynamic_header["public_custom_data"]

    # Beyond Python 3.7, construct makes the base class of a Container be `dict` instead of `OrderedDict`
    # So emulate move_to_end by removing and re-inserting the element
    end_el = kdbx.header.value.dynamic_header["end"]
    del kdbx.header.value.dynamic_header["end"]
    kdbx.header.value.dynamic_header["end"] = end_el


# -------------------- XML Processing --------------------


class XML(Adapter):
    """Bytes <---> lxml etree"""

    def _decode(self, data, con, path):
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(io.BytesIO(data), parser)

    def _encode(self, tree, con, path):
        return etree.tostring(tree)


class UnprotectedStream(Adapter):
    """lxml etree <---> unprotected lxml etree
    Iterate etree for Protected elements and decrypt using cipher
    provided by get_cipher"""

    protected_xpath = '//Value[@Protected=\'True\']'

    def __init__(self, protected_stream_key, subcon):
        super().__init__(subcon)
        self.protected_stream_key = protected_stream_key

    def _decode(self, tree, con, path):
        cipher = self.get_cipher(self.protected_stream_key(con))
        for elem in tree.xpath(self.protected_xpath):
            if elem.text is not None:
                try:
                    result = cipher.decrypt(base64.b64decode(elem.text)).decode('utf-8')
                    # strip invalid XML characters - https://stackoverflow.com/questions/8733233
                    result = re.sub(
                        '[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+',
                        '',
                        result
                    )
                    elem.text = result
                except (UnicodeDecodeError, BinasciiError, ValueError):
                    # FIXME: this should be a warning eventually, need to fix all databases in tests/ first
                    log.error(
                        "Element at {} marked as protected, but could not unprotect".format(tree.getpath(elem))
                    )
        return tree

    def _encode(self, tree, con, path):
        tree_copy = deepcopy(tree)
        cipher = self.get_cipher(self.protected_stream_key(con))
        for elem in tree_copy.xpath(self.protected_xpath):
            if elem.text is not None:
                elem.text = base64.b64encode(
                    cipher.encrypt(
                        elem.text.encode('utf-8')
                    )
                )
        return tree_copy


class ARCFourVariantStream(UnprotectedStream):
    def get_cipher(self, protected_stream_key):
        raise Exception("ARCFourVariant not implemented")


# https://github.com/dlech/KeePass2.x/blob/97141c02733cd3abf8d4dce1187fa7959ded58a8/KeePassLib/Cryptography/CryptoRandomStream.cs#L115-L119
class Salsa20Stream(UnprotectedStream):
    def get_cipher(self, protected_stream_key):
        key = hashlib.sha256(protected_stream_key).digest()
        return Salsa20.new(
            key=key,
            nonce=b'\xE8\x30\x09\x4B\x97\x20\x5D\x2A'
        )


# https://github.com/dlech/KeePass2.x/blob/97141c02733cd3abf8d4dce1187fa7959ded58a8/KeePassLib/Cryptography/CryptoRandomStream.cs#L103-L111
class ChaCha20Stream(UnprotectedStream):
    def get_cipher(self, protected_stream_key):
        key_hash = hashlib.sha512(protected_stream_key).digest()
        key = key_hash[:32]
        nonce = key_hash[32:44]
        return ChaCha20.new(
            key=key,
            nonce=nonce
        )


def Unprotect(protected_stream_id, protected_stream_key, subcon):
    """Select stream cipher based on protected_stream_id"""

    return Switch(
        protected_stream_id,
        {'arcfourvariant': ARCFourVariantStream(protected_stream_key, subcon),
         'salsa20': Salsa20Stream(protected_stream_key, subcon),
         'chacha20': ChaCha20Stream(protected_stream_key, subcon),
         },
        default=subcon
    )


# -------------------- Payload Encryption/Decompression --------------------

class Concatenated(Adapter):
    """Data Blocks <---> Bytes"""

    def _decode(self, blocks, con, path):
        return b''.join([block.block_data for block in blocks])

    def _encode(self, payload_data, con, path):
        blocks = []
        # split payload_data into 1 MB blocks (spec default)
        i = 0
        while i < len(payload_data):
            blocks.append(Container(block_data=payload_data[i:i + 2**20]))
            i += 2**20
        blocks.append(Container(block_data=b''))

        return blocks


class DecryptedPayload(Adapter):
    """Encrypted Bytes <---> Decrypted Bytes"""

    def _decode(self, payload_data, con, path):
        cipher = self.get_cipher(
            con.master_key,
            con._.header.value.dynamic_header.encryption_iv.data
        )
        payload_data = cipher.decrypt(payload_data)
        # FIXME: Construct ugliness.  Fixes #244.  First 32 bytes of decrypted kdbx3 payload
        # should be checked against stream_start_bytes for a CredentialsError.  Due to construct
        # limitations, we have to decrypt the whole payload in order to check the first 32 bytes.
        # However, when the credentials are wrong the invalid decrypted payload cannot
        # be unpadded correctly.  Instead, catch the unpad ValueError exception raised by unpad()
        # and allow kdbx3.py to raise a ChecksumError
        try:
            payload_data = self.unpad(payload_data)
        except ValueError:
            log.debug("Decryption unpadding failed")

        return payload_data

    def _encode(self, payload_data, con, path):
        payload_data = self.pad(payload_data)
        cipher = self.get_cipher(
            con.master_key,
            con._.header.value.dynamic_header.encryption_iv.data
        )
        payload_data = cipher.encrypt(payload_data)

        return payload_data


class AES256Payload(DecryptedPayload):
    def get_cipher(self, master_key, encryption_iv):
        return AES.new(master_key, AES.MODE_CBC, encryption_iv)
    def pad(self, data):
        return CryptoPadding.pad(data, 16)
    def unpad(self, data):
        return CryptoPadding.unpad(data, 16)


class ChaCha20Payload(DecryptedPayload):
    def get_cipher(self, master_key, encryption_iv):
        return ChaCha20.new(key=master_key, nonce=encryption_iv)
    def pad(self, data):
        return data
    def unpad(self, data):
        return data


class TwoFishPayload(DecryptedPayload):
    def get_cipher(self, master_key, encryption_iv):
        return Twofish.new(master_key, mode=Twofish.MODE_CBC, IV=encryption_iv)
    def pad(self, data):
        return CryptoPadding.pad(data, 16)
    def unpad(self, data):
        return CryptoPadding.unpad(data, 16)


class Decompressed(Adapter):
    """Compressed Bytes <---> Decompressed Bytes"""

    def _decode(self, data, con, path):
        return zlib.decompress(data, 16 + 15)

    def _encode(self, data, con, path):
        compressobj = zlib.compressobj(
            6,
            zlib.DEFLATED,
            16 + 15,
            zlib.DEF_MEM_LEVEL,
            0
        )
        data = compressobj.compress(data)
        data += compressobj.flush()
        return data


# -------------------- Cipher Enums --------------------

# payload encryption method
# https://github.com/keepassxreboot/keepassxc/blob/8324d03f0a015e62b6182843b4478226a5197090/src/format/KeePass2.cpp#L24-L26
CipherId = Mapping(
    GreedyBytes,
    {'aes256': b'1\xc1\xf2\xe6\xbfqCP\xbeX\x05!j\xfcZ\xff',
     'twofish': b'\xadh\xf2\x9fWoK\xb9\xa3j\xd4z\xf9e4l',
     'chacha20': b'\xd6\x03\x8a+\x8boL\xb5\xa5$3\x9a1\xdb\xb5\x9a'
     }
)

# protected entry encryption method
# https://github.com/dlech/KeePass2.x/blob/149ab342338ffade24b44aaa1fd89f14b64fda09/KeePassLib/Cryptography/CryptoRandomStream.cs#L35
ProtectedStreamId = Mapping(
    Int32ul,
    {'none': 0,
     'arcfourvariant': 1,
     'salsa20': 2,
     'chacha20': 3,
     }
)
