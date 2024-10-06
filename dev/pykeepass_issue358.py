#!/usr/bin/env python3

from pykeepass import PyKeePass

db, password, key = 'test4.kdbx', 'password', 'test4.key'

kp = PyKeePass(db, password, key)
print('before:', kp.binaries)

e = kp.add_entry(kp.root_group, "foo", "", "")
binary_id = kp.add_binary("bar".encode())
e.add_attachment(binary_id, "baz.txt")
kp.save()

kp.delete_binary(binary_id)
kp.save()

kp2 = PyKeePass(db, password, key)
print('after:', kp2.binaries)
