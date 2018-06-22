#!/bin/env python3
# Evan Widloski - 2018-04-11
# keepass decrypt experimentation

import hashlib
from construct import (
    Byte, Bytes, Int16ul, Int32ul, RepeatUntil, GreedyBytes, Struct, this,
    Mapping, Switch, Prefixed, Padding, Checksum, Computed, IfThenElse,
    Pointer, Tell, len_
)
from .common import (
    aes_kdf, AES256Payload, ChaCha20Payload, TwoFishPayload, Concatenated,
    DynamicDict, compute_key_composite, Decompressed, Reparsed,
    compute_master, CompressionFlags, CredentialsError, PayloadChecksumError,
    XML, CipherId, ProtectedStreamId, Unprotect
)


# -------------------- Key Derivation --------------------

# https://github.com/keepassxreboot/keepassxc/blob/8324d03f0a015e62b6182843b4478226a5197090/src/format/KeePass2.cpp#L24-L26 
kdf_uuids = {
    'aes': b'\xc9\xd9\xf3\x9ab\x8aD`\xbft\r\x08\xc1\x8aO\xea',
    'twofish': b'\xadh\xf2\x9fWoK\xb9\xa3j\xd4z\xf9e4l',
    'chacha20': b'\xd6\x03\x8a+\x8boL\xb5\xa5$3\x9a1\xdb\xb5\x9a'
}


# -------------------- Dynamic Header --------------------

# https://github.com/dlech/KeePass2.x/blob/dbb9d60095ef39e6abc95d708fb7d03ce5ae865e/KeePassLib/Serialization/KdbxFile.cs#L234-L246
DynamicHeaderItem = Struct(
    "id" / Mapping(
        Byte,
        {'end': 0,
         'comment': 1,
         'cipher_id': 2,
         'compression_flags': 3,
         'master_seed': 4,
         'transform_seed': 5,
         'transform_rounds': 6,
         'encryption_iv': 7,
         'protected_stream_key': 8,
         'stream_start_bytes': 9,
         'protected_stream_id': 10,
        }
    ),
    "data" / Prefixed(
        Int16ul,
        Switch(
            this.id,
            {'compression_flags': CompressionFlags,
             'cipher_id': CipherId,
             'transform_rounds': Int32ul,
             'protected_stream_id': ProtectedStreamId
            },
            default=GreedyBytes
        )
    ),
)

DynamicHeader = DynamicDict(
    'id',
    RepeatUntil(
        lambda item, a, b: item.id == 'end',
        DynamicHeaderItem
    )
)

# -------------------- Payload Verification --------------------

# encrypted payload is split into multiple data blocks with hashes
PayloadBlock = Struct(
    "block_index" / Checksum(
        Int32ul,
        lambda this: this._index,
        this
    ),
    "block_hash_offset" / Tell,
    Padding(32),
    "block_data" / Prefixed(Int32ul, GreedyBytes),
    # block_hash has to be at the end with a pointer because it needs to
    # come after other fields
    "block_hash" / Pointer(
        this.block_hash_offset,
        IfThenElse(
            len_(this.block_data) == 0,
            Checksum(
                Bytes(32),
                lambda _: b'\x00' * 32,
                this
            ),
            Checksum(
                Bytes(32),
                lambda block_data: hashlib.sha256(block_data).digest(),
                this.block_data,
                # exception=PayloadChecksumError
            )
        )
    ),
)

PayloadBlocks = RepeatUntil(
    lambda item, a, b: len(item.block_data) == 0, # and item.block_hash == b'\x00' * 32,
    PayloadBlock
)


# -------------------- Payload Decryption/Decompression --------------------


# Compressed Bytes <---> Stream Start Bytes, Decompressed XML
UnpackedPayload = Reparsed(
    Struct(
        # validate payload decryption
        Checksum(
            Bytes(32),
            lambda this: this._._.header.value.dynamic_header.stream_start_bytes.data,
            this,
            # exception=CredentialsError
        ),
        "xml" / Unprotect(
            this._._.header.value.dynamic_header.protected_stream_id.data,
            this._._.header.value.dynamic_header.protected_stream_key.data,
            XML(
                IfThenElse(
                    this._._.header.value.dynamic_header.compression_flags.data.compression,
                    Decompressed(Concatenated(PayloadBlocks)),
                    Concatenated(PayloadBlocks)
                )
            )
        )
    )
)


# -------------------- Main KDBX Structure --------------------

Body = Struct(
    "transformed_key" / Computed(
        lambda this: aes_kdf(
            this._.header.value.dynamic_header.transform_seed.data,
            this._.header.value.dynamic_header.transform_rounds.data,
            password=this._._.password,
            keyfile=this._._.keyfile
        )
    ),
    "master_key" / Computed(lambda cont: compute_master(cont)),
    "payload" / UnpackedPayload(
        Switch(
            this._.header.value.dynamic_header.cipher_id.data,
            {'aes256': AES256Payload(GreedyBytes),
             'chacha20': ChaCha20Payload(GreedyBytes),
             'twofish': TwoFishPayload(GreedyBytes),
            }
        )
    ),
)
