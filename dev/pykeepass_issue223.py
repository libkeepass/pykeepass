import shutil
import os
from pykeepass import PyKeePass

# setup
shutil.copy('test4.kdbx', 'test4_issue223.kdbx')
shutil.copy('test4.key', 'test4_issue223.key')

# open database and make change
kp = PyKeePass('test4_issue223.kdbx', 'password', 'test4_issue223.key')
kp.entries[0].title = 'newtitle'

# move keyfile
new_keyfile = 'test4_issue223_new.key'
if os.path.exists(new_keyfile):
    os.remove(new_keyfile)
shutil.move('test4_issue223.key', new_keyfile)

# save
try:
    kp.save()
except Exception as e:
    print('Got exception while saving:', type(e), e)

# open database with new keyfile
try:
    kp = PyKeePass('test4_issue223.kdbx', 'password', new_keyfile)
    print(kp.root_group)
except Exception as e:
    print('Got exception while opening:', e)

