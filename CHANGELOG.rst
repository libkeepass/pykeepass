4.1.0 - 2024-06-26
------------------
- merged PR#389 - add PyKeePass.database_name and database_description
- merged PR#392, fixed #390 - fix pkg_resources dependency issue
- fixed #391 - Entry.tags returns empty list instead of None
- fixed #395 - set 'encoding' attribute when exporting as XML
- fixed #383 - parse datetimes using isoformat instead of strptime

4.0.7 - 2024-02-29
------------------
- fixed #359 - PyKeePass has `decrypt` kwarg for accessing header info
- merged PR#347 - added Entry.index and Entry.move for moving entries
- merged PR#367 - added Entry.autotype_window setter
- merged PR#364 - allow filename/keyfile to be file-like objects
- merged PR#371 - drop dateutil dependency
- merged PR#348 - switch to pyproject.toml

4.0.6 - 2023-08-22
------------------
- fixed #350 - fixed all Python 2 deprecation FIXMEs (e.g. future, )

4.0.5 - 2023-06-05
------------------
- fixed #344 - AttributeError when accessing Times with None value
- use __hash__ when evaluating equality
- use mtime/uuid for HistoryEntry hashing

4.0.4 - 2023-05-23
------------------
- fixed #314 - correctly handle binaries with no data
- fixed #265 - check for keepass signature
- fixed #319 - support pathlib for filename/keyfile
- fixed #194 - added 'protected' arg to _set_string_field
- use official icon names from KeePass source and deprecate old icons
- added Entry.is_custom_property_protected()
- fixed #338 - allow comma entry tag separator

4.0.3 - 2022-06-21
------------------
- added otp support
- added debug_setup() function

4.0.2 - 2022-05-21
------------------
- added support for argon2id key derivation function
- added credential expiry functions
- fixes #223 - safe saving

4.0.1 - 2021-05-22
------------------
- added Entry.delete_history()
- added HistoryEntry class
- added Group.touch()
- support 2.0 keyfiles
- added PyKeePass.reload()
- dropped python2 tests
- fixed #284 - autotype_sequence returns string 'None'
- fixed #244 - incorrect PKCS padding error

4.0.0 - 2021-01-15
------------------
- paths changed from strings to lists
- added PyKeePass.recyclebin_group
- added PyKeePass.trash_group()
- added PyKeePass.trash_entry()
- added PyKeePass.empty_group()
- support reading/saving from streams
- fixed PyKeePass.dump_xml() pretty printing
- fixed #212 - properly pad encrypted payload
- fixed #222 - corrected transform_rounds field length

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
