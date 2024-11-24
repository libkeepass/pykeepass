#!/usr/bin/env python3

from construct import (
    Byte, Bytes, Checksum, Computed, Flag, GreedyBytes, GreedyString, If,
    IfThenElse, Int32sl, Int32ul, Int64sl, Int64ul, Mapping, Padding, Peek,
    Pointer, Prefixed, RepeatUntil, Struct, Switch, Tell, this,
)
from construct import Check, Int16ul, RawCopy, Switch, stream_write, ChecksumError, Adapter, Container, ListContainer
from collections import OrderedDict
from Cryptodome.Random import get_random_bytes

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

# DynamicHeaderItem = Struct(
#     "id" / Mapping(
#         Byte,
#         {
#             'end': 0,
#             'master_seed': 4,
#         }
#     ),
#     "data" / Prefixed(
#         Int32ul,
#         Switch(
#             this.id,
#             {
#                 'master_seed': RandomBytes(32),
#             },
#             default=GreedyBytes
#         )
#     )
# )
from pykeepass_issue219_deleteme import DynamicHeaderItem

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

# master_seed header item
master_dyn_item_data = (
    # id, length
    b'\x04' + b'\x20\x00\x00\x00' +
    # seed
    b'\xfe\xb9\xbecy\xd1\xe48\xf3\xf0T\xf5\x89\xa2(\xeeS\xd8\xd9BZ\t\xb7n\xc9j"\x12\xc3\x82\xd6\x83'
)
end_dyn_item_data = (
    # id, length
    b'\x00' + b'\x02\x00\x00\x00' +
    # value
    b'\r\n'
)

dynamic_dict = master_dyn_item_data + end_dyn_item_data

if __name__ == '__main__':

    print('PARSE')
    header = DynamicHeader4.parse(dynamic_dict)
    print('-------------------------------')
    print('master_seed:', sum(header.master_seed.data))
    print('-------------------------------')

    print('BUILD')
    header_data = DynamicHeader4.build(header)

    print('PARSE')
    header = DynamicHeader4.parse(header_data)
    print('-------------------------------')
    print('master_seed:', sum(header.master_seed.data))
    print('-------------------------------')