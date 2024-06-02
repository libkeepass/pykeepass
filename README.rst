pykeepass
============

.. image:: https://github.com/libkeepass/pykeepass/workflows/CI/badge.svg
   :target: https://github.com/libkeepass/pykeepass/actions?query=workflow%3ACI

.. image:: https://readthedocs.org/projects/pykeepass/badge/?version=latest
   :target: https://pykeepass.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/matrix/pykeepass:matrix.org.svg
   :target: https://matrix.to/#/#pykeepass:matrix.org

.. image:: https://img.shields.io/badge/irc-%23pykeepass-brightgreen
   :target: https://webchat.freenode.net/?channels=pykeepass
    
This library allows you to write entries to a KeePass database.

Come chat at `#pykeepass`_ on Freenode or `#pykeepass:matrix.org`_ on Matrix.

.. _#pykeepass: irc://irc.freenode.net
.. _#pykeepass\:matrix.org: https://matrix.to/#/%23pykeepass:matrix.org

Installation
------------

.. code::

   sudo apt install python3-lxml
   pip install pykeepass

Example
-------
.. code:: python

   from pykeepass import PyKeePass

   # load database
   >>> kp = PyKeePass('db.kdbx', password='somePassw0rd')

   # find any group by its name
   >>> group = kp.find_groups(name='social', first=True)

   # get the entries in a group
   >>> group.entries
   [Entry: "social/facebook (myusername)", Entry: "social/twitter (myusername)"]

   # find any entry by its title
   >>> entry = kp.find_entries(title='facebook', first=True)

   # retrieve the associated password
   >>> entry.password
   's3cure_p455w0rd'

   # update an entry
   >>> entry.notes = 'primary facebook account'

   # create a new group
   >>> group = kp.add_group(kp.root_group, 'email')

   # create a new entry
   >>> kp.add_entry(group, 'gmail', 'myusername', 'myPassw0rdXX')
   Entry: "email/gmail (myusername)"

   # save database
   >>> kp.save()


..
    TODO: add `Entry` and `Group` sections to document attributes of each

Finding Entries
---------------

**find_entries** (title=None, username=None, password=None, url=None, notes=None, otp=None, path=None, uuid=None, tags=None, string=None, group=None, recursive=True, regex=False, flags=None, history=False, first=False)

Returns entries which match all provided parameters, where ``title``, ``username``, ``password``, ``url``, ``notes``, ``otp``, ``autotype_window`` and ``autotype_sequence`` are strings, ``path`` is a list, ``string`` is a dict, ``autotype_enabled`` is a boolean, ``uuid`` is a ``uuid.UUID`` and ``tags`` is a list of strings.  This function has optional ``regex`` boolean and ``flags`` string arguments, which means to interpret search strings as `XSLT style`_ regular expressions with `flags`_.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html
.. _flags: https://www.w3.org/TR/xpath-functions/#flags 

The ``path`` list is a full path to an entry (ex. ``['foobar_group', 'foobar_entry']``).  This implies ``first=True``.  All other arguments are ignored when this is given.  This is useful for handling user input.

The ``string`` dict allows for searching custom string fields.  ex. ``{'custom_field1': 'custom value', 'custom_field2': 'custom value'}``

The ``group`` argument determines what ``Group`` to search under, and the ``recursive`` boolean controls whether to search recursively.

The ``history`` (default ``False``) boolean controls whether history entries should be included in the search results.

The ``first`` (default ``False``) boolean controls whether to return the first matched item, or a list of matched items.

* if ``first=False``, the function returns a list of ``Entry`` s or ``[]`` if there are no matches
* if ``first=True``, the function returns the first ``Entry`` match, or ``None`` if there are no matches

**entries**

a flattened list of all entries in the database

.. code:: python

   >>> kp.entries
   [Entry: "foo_entry (myusername)", Entry: "foobar_entry (myusername)", Entry: "social/gmail (myusername)", Entry: "social/facebook (myusername)"]

   >>> kp.find_entries(title='gmail', first=True)
   Entry: "social/gmail (myusername)"

   >>> kp.find_entries(title='foo.*', regex=True)
   [Entry: "foo_entry (myusername)", Entry: "foobar_entry (myusername)"]

   >>> entry = kp.find_entries(title='foo.*', url='.*facebook.*', regex=True, first=True)
   >>> entry.url
   'facebook.com'
   >>> entry.title
   'foo_entry'
   >>> entry.title = 'hello'

   >>> group = kp.find_group(name='social', first=True)
   >>> kp.find_entries(title='facebook', group=group, recursive=False, first=True)
   Entry: "social/facebook (myusername)"

   >>> entry.otp
   otpauth://totp/test:lkj?secret=TEST%3D%3D%3D%3D&period=30&digits=6&issuer=test



Finding Groups
--------------

**find_groups** (name=None, path=None, uuid=None, notes=None, group=None, recursive=True, regex=False, flags=None, first=False)

where ``name`` and ``notes`` are strings, ``path`` is a list, ``uuid`` is a ``uuid.UUID``. This function has optional ``regex`` boolean and ``flags`` string arguments, which means to interpret search strings as `XSLT style`_ regular expressions with `flags`_.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html
.. _flags: https://www.w3.org/TR/xpath-functions/#flags 

The ``path`` list is a full path to a group (ex. ``['foobar_group', 'sub_group']``).  This implies ``first=True``.  All other arguments are ignored when this is given.  This is useful for handling user input.

The ``group`` argument determines what ``Group`` to search under, and the ``recursive`` boolean controls whether to search recursively.

The ``first`` (default ``False``) boolean controls whether to return the first matched item, or a list of matched items.

* if ``first=False``, the function returns a list of ``Group`` s or ``[]`` if there are no matches
* if ``first=True``, the function returns the first ``Group`` match, or ``None`` if there are no matches

**root_group**

the ``Root`` group to the database

**groups**

a flattened list of all groups in the database

.. code:: python

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


Entry Functions and Properties
------------------------------
**add_entry** (destination_group, title, username, password, url=None, notes=None, tags=None, expiry_time=None, icon=None, force_creation=False)

**delete_entry** (entry)

**trash_entry** (entry)

move a group to the recycle bin.  The recycle bin is created if it does not exit.  ``entry`` must be an empty Entry.

**move_entry** (entry, destination_group)

**atime**

access time

**ctime**

creation time

**mtime**

modification time

where ``destination_group`` is a ``Group`` instance.  ``entry`` is an ``Entry`` instance. ``title``, ``username``, ``password``, ``url``, ``notes``, ``tags``, ``icon`` are strings. ``expiry_time`` is a ``datetime`` instance.

If ``expiry_time`` is a naive datetime object (i.e. ``expiry_time.tzinfo`` is not set), the timezone is retrieved from ``dateutil.tz.gettz()``.

.. code:: python

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

Group Functions and Properties
------------------------------
**add_group** (destination_group, group_name, icon=None, notes=None)

**delete_group** (group)

**trash_group** (group)

move a group to the recycle bin.  The recycle bin is created if it does not exit.  ``group`` must be an empty Group.

**empty_group** (group)

delete all entries and subgroups of a group.  ``group`` is an instance of ``Group``.

**move_group** (group, destination_group)

**atime**

access time

**ctime**

creation time

**mtime**

modification time

``destination_group`` and ``group`` are instances of ``Group``.  ``group_name`` is a string

.. code:: python

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

Attachments
-----------

In this section, *binary* refers to the bytes of the attached data (stored at the root level of the database), while *attachment* is a reference to a binary (stored in an entry).  A binary can be referenced by none, one or many attachments.

**add_binary** (data, compressed=True, protected=True)

where ``data`` is bytes.  Adds a blob of data to the database. The attachment reference must still be added to an entry (see below).  ``compressed`` only applies to KDBX3 and ``protected`` only applies to KDBX4 (no effect if used on wrong database version).  Returns id of attachment.

**delete_binary** (id)

where ``id`` is an int.  Removes binary data from the database and deletes any attachments that reference it.  Since attachments reference binaries by their positional index, attachments that reference binaries with id > ``id`` will automatically be decremented.

**find_attachments** (id=None, filename=None, element=None, recursive=True, regex=False, flags=None, history=False, first=False)

where ``id`` is an int, ``filename`` is a string, and element is an ``Entry`` or ``Group`` to search under.

* if ``first=False``, the function returns a list of ``Attachment`` s or ``[]`` if there are no matches
* if ``first=True``, the function returns the first ``Attachment`` match, or ``None`` if there are no matches

**binaries**

list of bytestrings containing binary data.  List index corresponds to attachment id

**attachments**

list containing all ``Attachment`` s in the database.

**Entry.add_attachment** (id, filename)

where ``id`` is an int and ``filename`` is a string.  Creates a reference using the given filename to a database binary.  The existence of a binary with the given id is not checked.  Returns ``Attachment``.

**Entry.delete_attachment** (attachment)

where ``attachment`` is an ``Attachment``.  Deletes a reference to a database binary.

**Entry.attachments**

list of ``Attachment`` s for this Entry.

**Attachment.id**

id of data that this attachment points to

**Attachment.filename**

string representing this attachment

**Attachment.data**

the data that this attachment points to.  Raises ``BinaryError`` if data does not exist.

**Attachment.entry**

the entry that this attachment is attached to

.. code:: python

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

Credential Expiry
-----------------

**credchange_date**

datetime object with date of last credentials change

**credchange_required**

boolean whether database credentials have expired and are required to change

**credchange_recommended**

boolean whether database credentials have expired and are recommended to change

**credchange_required_days**

days after **credchange_date** that credential update is required

**credchange_recommended_days**

days after **credchange_date** that credential update is recommended


Miscellaneous
-------------
**read** (filename=None, password=None, keyfile=None, transformed_key=None, decrypt=False)

where ``filename``, ``password``, and ``keyfile`` are strings (  ``filename`` and ``keyfile`` may also be file-like objects).  ``filename`` is the path to the database, ``password`` is the master password string, and ``keyfile`` is the path to the database keyfile.  At least one of ``password`` and ``keyfile`` is required.  Alternatively, the derived key can be supplied directly through ``transformed_key``.  ``decrypt`` tells whether the file should be decrypted or not.

Can raise ``CredentialsError``, ``HeaderChecksumError``, or ``PayloadChecksumError``.

**reload** ()

reload database from disk using previous credentials

**save** (filename=None)

where ``filename`` is the path of the file to save to (``filename`` may also be file-like object).  If ``filename`` is not given, the path given in ``read`` will be used.

**password**

string containing database password.  Can also be set.  Use ``None`` for no password.

**filename**

string containing path to database.  Can also be set

**keyfile**

string containing path to the database keyfile.  Can also be set.  Use ``None`` for no keyfile.

**version**

tuple containing database version.  e.g. ``(3, 1)`` is a KDBX version 3.1 database.

**encryption_algorithm**

string containing algorithm used to encrypt database.  Possible values are ``aes256``, ``chacha20``, and ``twofish``.

**create_database** (filename, password=None, keyfile=None, transformed_key=None)

create a new database at ``filename`` with supplied credentials.  Returns ``PyKeePass`` object

**tree**

database lxml tree

**xml**

get database XML data as string

**dump_xml** (filename)

pretty print database XML to file

TOTP
-------

**Entry.otp**

TOTP URI which can be passed to an OTP library to generate codes

.. code:: python

   # find an entry which has otp attribute
   >>> e = kp.find_entries(otp='.*', regex=True, first=True)
   >>> import pyotp
   >>> pyotp.parse_uri(e.otp).now()
   799270


Tests and Debugging
-------------------

Run tests with :code:`python tests/tests.py` or :code:`python tests/tests.py SomeSpecificTest`

Enable debugging when doing tests in console:

   >>> from pykeepass.pykeepass import debug_setup
   >>> debug_setup()
   >>> kp.entries[0]
   DEBUG:pykeepass.pykeepass:xpath query: //Entry
   DEBUG:pykeepass.pykeepass:xpath query: (ancestor::Group)[last()]
   DEBUG:pykeepass.pykeepass:xpath query: (ancestor::Group)[last()]
   DEBUG:pykeepass.pykeepass:xpath query: String/Key[text()="Title"]/../Value
   DEBUG:pykeepass.pykeepass:xpath query: String/Key[text()="UserName"]/../Value
   Entry: "root_entry (foobar_user)"
