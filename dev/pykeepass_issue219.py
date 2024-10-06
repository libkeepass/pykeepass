from construct import (
    Struct, RawCopy, Checksum, this, Subconstruct, Prefixed,
    Bytes, GreedyBytes, Int8ul,
    stream_tell, stream_seek, stream_read, stream_write,
)
from Cryptodome.Random import get_random_bytes

# simple placeholder checksum function
def check_func(header_data, master_seed):
    return header_data + master_seed

def compute_header_hmac_hash(context):
    """Compute HMAC-SHA256 hash of header.
    Used to prevent header tampering."""
    print('----------------------')
    print('master_seed:', sum(context.header.master_seed))
    print("header_sha:", sum(context.header._data))
    print('----------------------')

    return context.header._data + context.header.master_seed


class RandomGreedyBytes(type(GreedyBytes)):
    """Same as GreedyBytes, but generate random bytes when building"""

    def _build(self, obj, stream, context, path):
        data = bytes(obj) if type(obj) is bytearray else obj
        data = get_random_bytes(len(data))
        stream_write(stream, data, len(data), path)
        return data

class Copy(Subconstruct):
    """Same as RawCopy, but don't create parent container when parsing.
    Instead store data in ._data attribute of subconstruct, and never rebuild from data
    """

    def _parse(self, stream, context, path):
        offset1 = stream_tell(stream, path)
        obj = self.subcon._parsereport(stream, context, path)
        offset2 = stream_tell(stream, path)
        stream_seek(stream, offset1, 0, path)
        obj._data = stream_read(stream, offset2-offset1, path)
        return obj

    def _build(self, obj, stream, context, path):
        offset1 = stream_tell(stream, path)
        obj = self.subcon._build(obj, stream, context, path)
        offset2 = stream_tell(stream, path)
        stream_seek(stream, offset1, 0, path)
        obj._data = stream_read(stream, offset2-offset1, path)
        return obj

# simple database format with header and checksum
s = Struct(
    "header" / Copy(Struct(
        "master_seed" / Prefixed(
            Int8ul,
            RandomGreedyBytes(),
        ),
        "more_data" / Bytes(8)
    )),
    # "hash" / Checksum(
    #     Bytes(25),
    #     lambda ctx: check_func(ctx.header._data, ctx.header.master_seed),
    #     this
    # )
    "hash" / Checksum(
        Bytes(25),
        compute_header_hmac_hash,
        this,
        # exception=CredentialsError,
    )
)

# synthesize a 'database'
master_seed = b'00000000'
length = int.to_bytes(len(master_seed), length=1, byteorder='big')
more_data = b'12345678'
header = length + master_seed + more_data
data1 = header + check_func(header, master_seed)

# parse the database
print('PARSING')
parsed1 = s.parse(data1)

# rebuild and try to reparse final result
print('SAVING')
data2 = s.build(parsed1)
parsed2 = s.parse(data2)
if parsed1.header.master_seed == parsed2.header.master_seed:
    Exception("Database unchanged")
