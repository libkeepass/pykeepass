from pykeepass import PyKeePass

# parse the database
print('PARSING')
parsed1 = PyKeePass('test4.kdbx', 'password', 'test4.key')

# rebuild and try to reparse final result
print('SAVING')
del parsed1.kdbx.header.data
parsed1.save('/tmp/test4.kdbx')
print('PARSING')
parsed2 = PyKeePass('/tmp/test4.kdbx', 'password', 'test4.key')
if parsed1.kdbx.header.value.dynamic_header.master_seed == parsed2.kdbx.header.value.dynamic_header.master_seed:
    Exception("Database unchanged")
