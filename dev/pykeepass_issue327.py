from datetime import datetime, timedelta
from dateutil import tz
from pykeepass import PyKeePass
import base64
import struct

# manually set 'foobar_entry' time so that it overflows
kp = PyKeePass('test4.kdbx', 'password', 'test4.key')
e = kp.find_entries(title='foobar_entry', first=True)
t = e._xpath('Times/CreationTime', first=True)
overflow_seconds = 399999999999
t.text = base64.b64encode(struct.pack('<Q', overflow_seconds)).decode('utf-8')

# catch the exception
try:
    print('ctime:', e.ctime)
except OverflowError:
    print('got an overflow error')
