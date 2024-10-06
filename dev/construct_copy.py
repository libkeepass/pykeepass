#!/usr/bin/env python

from construct import Struct, Bytes
from construct import RawCopy as Copy

from construct import Subconstruct, stream_tell, stream_seek, stream_read, stream_write, Container
from Cryptodome.Random import get_random_bytes

class RandomBytes(Bytes):
    """Same as Bytes, but generate random bytes when building"""

    def _build(self, obj, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        data = get_random_bytes(length)
        stream_write(stream, data, length, path)
        return data

class Copy(Subconstruct):

    def _parse(self, stream, context, path):
        offset1 = stream_tell(stream, path)
        obj = self.subcon._parsereport(stream, context, path)
        offset2 = stream_tell(stream, path)
        stream_seek(stream, offset1, 0, path)
        data = stream_read(stream, offset2-offset1, path)
        return Container(data=data, value=obj, offset1=offset1, offset2=offset2, length=(offset2-offset1))

    def _build(self, obj, stream, context, path):
        if obj is None and self.subcon.flagbuildnone:
            obj = dict(value=None)
        if 'value' in obj:
            value = obj['value']
            offset1 = stream_tell(stream, path)
            buildret = self.subcon._build(value, stream, context, path)
            value = value if buildret is None else buildret
            offset2 = stream_tell(stream, path)
            stream_seek(stream, offset1, 0, path)
            data = stream_read(stream, offset2-offset1, path)
            return Container(obj, data=data, value=value, offset1=offset1, offset2=offset2, length=(offset2-offset1))
        raise RawCopyError('RawCopy cannot build, both data and value keys are missing', path=path)

s = Struct(
    "header" / Copy(Struct(
        "seed" / RandomBytes(8)
    ))
)

parsed = s.parse(b'\x00' * 8)

print(s.build(parsed))
print(s.build(parsed))
