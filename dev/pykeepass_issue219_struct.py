#!/usr/bin/env python

from io import BytesIO
from Cryptodome.Random import get_random_bytes

# simple placeholder checksum function
def check_func(header_data, master_seed):
    return header_data + master_seed

# synthesize a 'database'
master_seed = b'00000000'
more_data = b'12345678'
header = master_seed + more_data
data = header + check_func(header, master_seed)

# %% struct parsing ---------------------------------

import struct

def unpack(fmt, stream):
    b = stream.read(struct.calcsize(fmt))
    return struct.unpack(fmt, b)[0]

def pack(fmt, data):
    return struct.pack(fmt, data)

def parse(stream):
    master_seed = unpack('<8s', stream)
    more_data = unpack('<8s', stream)
    checksum = unpack('<24s', stream)
    header = master_seed + more_data
    assert check_func(header, master_seed) == checksum, "Invalid checksum"

    return {
        'master_seed': master_seed,
        'more_data': more_data,
        'checksum': checksum
    }

def build(*, master_seed, more_data, **kwargs):
    master_seed = get_random_bytes(len(master_seed))
    header = master_seed + more_data
    checksum = check_func(header, master_seed)
    out = header
    out += checksum
    return BytesIO(out)

# parse the database
parsed = parse(BytesIO(data))

# change the master seed
parsed['master_seed'] = b'11111111'

# rebuild and try to reparse final result
data2 = build(**parsed)
parse(data2)
