#!/usr/bin/env python

from io import BytesIO
#
# simple placeholder checksum function
def check_func(header_data, master_seed):
    return header_data + master_seed

# synthesize a 'database'
master_seed = b'00000000'
more_data = b'12345678'
header = master_seed + more_data
data = header + check_func(header, master_seed)

# %% construct2 parsing ---------------------------------

from construct import Struct, RawCopy, Bytes, Checksum, this, Subconstruct
from construct import stream_tell, stream_seek, stream_read, stream_write
from Cryptodome.Random import get_random_bytes

class RandomBytes(Bytes):
    """Same as Bytes, but randomized when building"""

    def _build(self, obj, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        data = get_random_bytes(length)
        stream_write(stream, data, length, path)
        return data

class Copy(Subconstruct):
    """Same as RawCopy, but don't create additional container.
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


s = Struct(
    "header" / Copy(Struct(
        "master_seed" / RandomBytes(8),
        "more_data" / Bytes(8)
    )),
    "hash" / Checksum(
        Bytes(24),
        lambda ctx: check_func(ctx.header._data, ctx.header.master_seed),
        this
    )
)

# parse the database
parsed = s.parse(data)

# rebuild and try to reparse final result
data2 = s.build(parsed)
s.parse(data2)
assert data != data2, "Database unchanged"
