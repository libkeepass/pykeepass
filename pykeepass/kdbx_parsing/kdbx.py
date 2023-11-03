from construct import Struct, Switch, Bytes, Int16ul, RawCopy, Check, this, stream_seek, stream_tell, stream_read, Subconstruct
from .kdbx3 import DynamicHeader as DynamicHeader3
from .kdbx3 import Body as Body3
from .kdbx4 import DynamicHeader as DynamicHeader4
from .kdbx4 import Body as Body4


class Copy(Subconstruct):
    """Same as RawCopy, but don't create parent container when parsing.
    Instead store data in ._data attribute of subconstruct, and never rebuild from data
    """

    def _parse(self, stream, context, path):
        offset1 = stream_tell(stream, path)
        obj = self.subcon._parsereport(stream, context, path)
        offset2 = stream_tell(stream, path)
        stream_seek(stream, offset1, 0, path)
        obj._data = stream_read(stream, offset2 - offset1, path)
        return obj

    def _build(self, obj, stream, context, path):
        offset1 = stream_tell(stream, path)
        obj = self.subcon._build(obj, stream, context, path)
        offset2 = stream_tell(stream, path)
        stream_seek(stream, offset1, 0, path)
        obj._data = stream_read(stream, offset2 - offset1, path)
        return obj


# verify file signature
def check_signature(ctx):
    return ctx.sig1 == b'\x03\xd9\xa2\x9a' and ctx.sig2 == b'\x67\xFB\x4B\xB5'

KDBX = Struct(
    "header" / Copy(
        Struct(
            "sig1" / Bytes(4),
            "sig2" / Bytes(4),
            "sig_check" / Check(check_signature),
            "minor_version" / Int16ul,
            "major_version" / Int16ul,
            "dynamic_header" / Switch(
                this.major_version,
                {3: DynamicHeader3,
                 4: DynamicHeader4
                 }
            )
        )
    ),
    "body" / Switch(
        this.header.major_version,
        {3: Body3,
         4: Body4
         }
    )
)
