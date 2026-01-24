from typing import TYPE_CHECKING

from construct import Bytes, Check, Int16ul, RawCopy, Struct, Switch, this

from .kdbx3 import Body as Body3
from .kdbx3 import DynamicHeader as DynamicHeader3
from .kdbx4 import Body as Body4
from .kdbx4 import DynamicHeader as DynamicHeader4

if TYPE_CHECKING:
    from construct import Context


# verify file signature
def check_signature(ctx: Context) -> bool:
    return ctx.sig1 == b"\x03\xd9\xa2\x9a" and ctx.sig2 == b"\x67\xfb\x4b\xb5"


KDBX = Struct(
    "header"
    / RawCopy(
        Struct(
            "sig1" / Bytes(4),
            "sig2" / Bytes(4),
            "sig_check" / Check(check_signature),
            "minor_version" / Int16ul,
            "major_version" / Int16ul,
            "dynamic_header"
            / Switch(this.major_version, {3: DynamicHeader3, 4: DynamicHeader4}),
        )
    ),
    "body" / Switch(this.header.value.major_version, {3: Body3, 4: Body4}),
)
