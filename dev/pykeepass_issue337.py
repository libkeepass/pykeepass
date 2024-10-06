#!/usr/bin/env python3

import subprocess
from pykeepass import PyKeePass
db, password, key = 'test3.kdbx', 'password', 'test3.key'

kp = PyKeePass(db, password, key)

print(open(key, 'rb').read())
