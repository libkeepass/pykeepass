import argon2

from construct import (
    Byte, Bytes, Checksum, Computed, Flag, GreedyBytes, GreedyString, If,
    IfThenElse, Int32sl, Int32ul, Int64sl, Int64ul, Mapping, Padding, Peek,
    Pointer, Prefixed, RepeatUntil, Struct, Switch, Tell, this,
)
from construct import Check, Int16ul, RawCopy, Switch, stream_write, ChecksumError, Adapter, Container, ListContainer
from collections import OrderedDict
from Cryptodome.Random import get_random_bytes

from pykeepass.kdbx_parsing.kdbx4 import compute_transformed, CompressionFlags, VariantDictionary, CipherId
from pykeepass.kdbx_parsing.common import compute_master
import hmac
import hashlib


def compute_header_hmac_hash(context):
    """Compute HMAC-SHA256 hash of header.
    Used to prevent header tampering."""

    print('-------------------------------')
    print('master_seed:', sum(context._.header.value.dynamic_header.master_seed.data))
    # print('transformed_key:', sum(context.transformed_key))
    # print("header_sha:", sum(context._.header.data))
    print('-------------------------------')

    return hmac.new(
        hashlib.sha512(
            b'\xff' * 8 +
            hashlib.sha512(
                context._.header.value.dynamic_header.master_seed.data +
                context.transformed_key +
                b'\x01'
            ).digest()
        ).digest(),
        context._.header.data,
        hashlib.sha256
    ).digest()

# verify file signature
def check_signature(ctx):
    return ctx.sig1 == b'\x03\xd9\xa2\x9a' and ctx.sig2 == b'\x67\xFB\x4B\xB5'

class RandomBytes(Bytes):
    """Same as Bytes, but generate random bytes when building"""

    def _build(self, obj, stream, context, path):
        print('generating random bytes...')
        length = self.length(context) if callable(self.length) else self.length
        data = get_random_bytes(length)
        print('old:', sum(context.data))
        print('new:', sum(data))
        stream_write(stream, data, length, path)
        return data


DynamicHeaderItem = Struct(
    "id" / Mapping(
        Byte,
        {'end': 0,
         'comment': 1,
         'cipher_id': 2,
         'compression_flags': 3,
         'master_seed': 4,
         'encryption_iv': 7,
         'kdf_parameters': 11,
         'public_custom_data': 12
         }
    ),
    "data" / Prefixed(
        Int32ul,
        Switch(
            this.id,
            {'compression_flags': CompressionFlags,
             'kdf_parameters': VariantDictionary,
             'cipher_id': CipherId,
             'master_seed': RandomBytes(32),
             },
            default=GreedyBytes
        )
    )
)


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
            if key == 'master_seed':
                print('key:', key, sum(obj[key].data))
            if key in self.lump:
                l += obj[key]
            else:
                l.append(obj[key])

        return ListContainer(l)

DynamicHeader4 = DynamicDict(
    'id',
    RepeatUntil(
        lambda item, a, b: item.id == 'end',
        DynamicHeaderItem
    )
)
# from issue219_adaptertest_deleteme import DynamicHeader4

Body4 = Struct(
    "transformed_key" / Computed(compute_transformed),
    "master_key" / Computed(compute_master),
    "sha256" / Checksum(
        Bytes(32),
        lambda data: hashlib.sha256(data).digest(),
        this._.header.data,
        # exception=HeaderChecksumError,
    ),
    "cred_check" / If(this._._.decrypt,
        Checksum(
            Bytes(32),
            compute_header_hmac_hash,
            this,
            # exception=CredentialsError,
        )
    ),
    "Payload" / GreedyBytes
)

KDBX = Struct(
    "header" / RawCopy(
        Struct(
            "sig1" / Bytes(4),
            "sig2" / Bytes(4),
            "sig_check" / Check(check_signature),
            "minor_version" / Int16ul,
            "major_version" / Int16ul,
            "dynamic_header" / Switch(
                this.major_version,
                {
                 4: DynamicHeader4
                 }
            )
        )
    ),
    "body" / Switch(
        this.header.value.major_version,
        {
         4: Body4
         }
    )
)

if __name__ == '__main__':
    # parse the database
    opts = dict(password='password', keyfile='test4.key', decrypt=True, transformed_key=None)
    print('PARSING')
    parsed1 = KDBX.parse_file('test4.kdbx', **opts)
    # rebuild and try to reparse final result
    print('SAVING')
    del parsed1.header.data
    KDBX.build_file(parsed1, '/tmp/test4.kdbx', **opts)
    # parse the database
    print('PARSING')
    try:
        parsed2 = KDBX.parse_file('/tmp/test4.kdbx', **opts)
    except ChecksumError:
        pass