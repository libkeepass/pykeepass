3.2.1 - 2020-07-19
------------------
- pin construct version to last supporting python2
- hard dependency on pycryptodomex
- fixed #193 - kp.groups, kp.entries not returning elements with name/title None

3.2.0 - 2020-01-18
------------------
- added PyKeePass.xml()
- added create_database()
- added tag searching - #182
- fixed #181 - binary attachments missing Compressed attribute unparseable
- fixed #129 - protected multiline fields missing newline
- fixed problem where entries are protected after save

3.1.0 - 2019-10-24
------------------
- removed context manager
- added autotype string support
- added attachments
- fixed find_entries(path=xxx) behavior
- Entry.uuid, Group.uuid now return uuid.UUID object instead of string

3.0.0 - 2018-09-07
------------------
- added context manager
- added custom string field searching
- added 'Notes' field
- renamed 'tree' argument to 'group'
- KDBX4 support

2.8.0 - 2017-11-09
------------------

2.7.0 - 2017-06-25
------------------

2.6.0 - 2017-08-19
------------------

2.5.0 - 2017-03-19
------------------

2.4.0 - 2016-09-25
------------------

2.3.0 - 2016-10-13
-------------------

2.2.0 - 2016-10-10
------------------
