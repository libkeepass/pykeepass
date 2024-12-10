# pykeepass

<a href="https://github.com/libkeepass/pykeepass/actions/workflows/ci.yaml"><img src="https://github.com/libkeepass/pykeepass/actions/workflows/ci.yaml/badge.svg"/></a>
<a href="https://libkeepass.github.io/pykeepass"><img src="https://readthedocs.org/projects/pykeepass/badge/?version=latest"/></a>
<a href="https://matrix.to/#/%23pykeepass:matrix.org"><img src="https://img.shields.io/badge/chat-%23pykeepass-green"/></a>
    
This library allows you to write entries to a KeePass database.

Come chat at [#pykeepass:matrix.org](https://matrix.to/#/%23pykeepass:matrix.org) on Matrix.

# Installation

``` bash
sudo apt install python3-lxml
pip install pykeepass
```

# Quickstart

General database manipulation

``` python
from pykeepass import PyKeePass

# load database
>>> kp = PyKeePass('db.kdbx', password='somePassw0rd')

# get all entries
>>> kp.entries
[Entry: "foo_entry (myusername)", Entry: "foobar_entry (myusername)", ...]

# find any group by its name
>>> group = kp.find_groups(name='social', first=True)

# get the entries in a group
>>> group.entries
[Entry: "social/facebook (myusername)", Entry: "social/twitter (myusername)"]

# find any entry by its title
>>> entry = kp.find_entries(title='facebook', first=True)

# retrieve the associated password and OTP information
>>> entry.password
's3cure_p455w0rd'
>>> entry.otp
otpauth://totp/test:lkj?secret=TEST%3D%3D%3D%3D&period=30&digits=6&issuer=test

# update an entry
>>> entry.notes = 'primary facebook account'

# create a new group
>>> group = kp.add_group(kp.root_group, 'email')

# create a new entry
>>> kp.add_entry(group, 'gmail', 'myusername', 'myPassw0rdXX')
Entry: "email/gmail (myusername)"

# save database
>>> kp.save()
```

Finding and manipulating entries

``` python
# add a new entry to the Root group
>>> kp.add_entry(kp.root_group, 'testing', 'foo_user', 'passw0rd')
Entry: "testing (foo_user)"

# add a new entry to the social group
>>> group = kp.find_groups(name='social', first=True)
>>> entry = kp.add_entry(group, 'testing', 'foo_user', 'passw0rd')
Entry: "testing (foo_user)"

# save the database
>>> kp.save()

# delete an entry
>>> kp.delete_entry(entry)

# move an entry
>>> kp.move_entry(entry, kp.root_group)

# save the database
>>> kp.save()

# change creation time
>>> from datetime import datetime, timezone
>>> entry.ctime = datetime(2023, 1, 1, tzinfo=timezone.utc)

# update modification or access time
>>> entry.touch(modify=True)

# save entry history
>>> entry.save_history()
```

Finding and manipulating groups

``` python
>>> kp.groups
[Group: "foo", Group "foobar", Group: "social", Group: "social/foo_subgroup"]

>>> kp.find_groups(name='foo', first=True)
Group: "foo"

>>> kp.find_groups(name='foo.*', regex=True)
[Group: "foo", Group "foobar"]

>>> kp.find_groups(path=['social'], regex=True)
[Group: "social", Group: "social/foo_subgroup"]

>>> kp.find_groups(name='social', first=True).subgroups
[Group: "social/foo_subgroup"]

>>> kp.root_group
Group: "/"

# add a new group to the Root group
>>> group = kp.add_group(kp.root_group, 'social')

# add a new group to the social group
>>> group2 = kp.add_group(group, 'gmail')
Group: "social/gmail"

# save the database
>>> kp.save()

# delete a group
>>> kp.delete_group(group)

# move a group
>>> kp.move_group(group2, kp.root_group)

# save the database
>>> kp.save()

# change creation time
>>> from datetime import datetime, timezone
>>> group.ctime = datetime(2023, 1, 1, tzinfo=timezone.utc)

# update modification or access time
>>> group.touch(modify=True)
```

Attachments

``` python
>>> e = kp.add_entry(kp.root_group, title='foo', username='', password='')

# add attachment data to the db
>>> binary_id = kp.add_binary(b'Hello world')

>>> kp.binaries
[b'Hello world']

# add attachment reference to entry
>>> a = e.add_attachment(binary_id, 'hello.txt')
>>> a
Attachment: 'hello.txt' -> 0

# access attachments
>>> a
Attachment: 'hello.txt' -> 0
>>> a.id
0
>>> a.filename
'hello.txt'
>>> a.data
b'Hello world'
>>> e.attachments
[Attachment: 'hello.txt' -> 0]

# list all attachments in the database
>>> kp.attachments
[Attachment: 'hello.txt' -> 0]

# search attachments
>>> kp.find_attachments(filename='hello.txt')
[Attachment: 'hello.txt** -> 0]

# delete attachment reference
>>> e.delete_attachment(a)

# or, delete both attachment reference and binary
>>> kp.delete_binary(binary_id**
```

OTP codes

``` python
# find an entry which has otp attribute
>>> e = kp.find_entries(otp='.*', regex=True, first=True)
>>> import pyotp
>>> pyotp.parse_uri(e.otp).now()
799270
```


# Tests and Debugging

Run tests with `python tests/tests.py` or `python tests/tests.py SomeSpecificTest`

Enable debugging when doing tests in console:

``` python
>>> from pykeepass.pykeepass import debug_setup
>>> debug_setup()
>>> kp.entries[0]
DEBUG:pykeepass.pykeepass:xpath query: //Entry
DEBUG:pykeepass.pykeepass:xpath query: (ancestor::Group)[last()]
DEBUG:pykeepass.pykeepass:xpath query: (ancestor::Group)[last()]
DEBUG:pykeepass.pykeepass:xpath query: String/Key[text()="Title"]/../Value
DEBUG:pykeepass.pykeepass:xpath query: String/Key[text()="UserName"]/../Value
Entry: "root_entry (foobar_user)"
```

