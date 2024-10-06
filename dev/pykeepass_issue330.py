#!/usr/bin/env python3
#  ``

from construct import (
    Byte, Bytes, Int32ul, RepeatUntil, GreedyBytes, Struct, this, Mapping,
    Switch, Flag, Prefixed, Int64ul, Int32sl, Int64sl, GreedyString, Padding,
    Peek, Checksum, Computed, IfThenElse, Pointer, Tell
)
from pykeepass.kdbx_parsing.common import ProtectedStreamId

binary = Struct(
    "protected" / Byte,
)
InnerHeaderItem = Struct(
    "type" / Mapping(
        Byte,
        {'end': 0x00,
         'protected_stream_id': 0x01,
         'protected_stream_key': 0x02,
         'binary': 0x03
         }
    ),
    "data" / Prefixed(
        Int32ul,
        Switch(
            this.type,
            {'protected_stream_id': ProtectedStreamId},
            default=GreedyBytes
        )
    )
)

bites = b'\x03\x01\x00\x00\x00\x00'
result = InnerHeaderItem.parse(bites)

result.data = b''
print(InnerHeaderItem.build(result))
