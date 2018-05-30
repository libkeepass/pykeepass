pykeepass
============

This library allows you to write entries to a KeePass database

Simple Example
--------------
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


Finding Entries
----------------------

**find_entries** (title=None, username=None, password=None, url=None, notes=None, path=None, uuid=None, string=none, group=None, recursive=True, regex=False, flags=None, history=False, first=False)

Returns entries which match all provided parameters, where ``title``, ``username``, ``password``, ``url``, ``notes``, ``path`` and ``uuid`` are strings, ``string`` is a dict.  This function has optional ``regex`` boolean and ``flags`` string arguments, which means to interpret search strings as `XSLT style`_ regular expressions with `flags`_.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html
.. _flags: https://www.w3.org/TR/xpath-functions/#flags 

The ``path`` string can be a direct path to an entry, or (when ending in ``/``) the path to the group to recursively search under.

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

   >>> group = kp.find_group(name='social', first=True)
   >>> kp.find_entries(title='facebook', group=group, recursive=False, first=True)
   Entry: "social/facebook (myusername)"

For backwards compatibility, the following function are also available:

**find_entries_by_title** (title, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_username** (username, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_password** (password, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_url** (url, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_notes** (notes, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_path** (path, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_uuid** (uuid, regex=False, flags=None, tree=None, history=False, first=False)

**find_entries_by_string** (string, regex=False, flags=None, tree=None, history=False, first=False)

Finding Groups
----------------------

**find_groups** (name=None, path=None, uuid=None, notes=None, group=None, recursive=True, regex=False, flags=None, first=False)

where ``name``, ``path``, ``uuid`` and ``notes`` are strings.  This function has optional ``regex`` boolean and ``flags`` string arguments, which means to interpret search strings as `XSLT style`_ regular expressions with `flags`_.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html
.. _flags: https://www.w3.org/TR/xpath-functions/#flags 

The ``path`` string must end in ``/``.

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

   >>> kp.find_groups(path='social/', regex=True)
   [Group: "social", Group: "social/foo_subgroup"]

   >>> kp.find_groups(name='social', first=True).subgroups
   [Group: "social/foo_subgroup"]

   >>> kp.root_group
   Group: "/"

For backwards compatibility, the following functions are also available:

**find_groups_by_name** (name, tree=None, regex=False, flags=None, first=False)

**find_groups_by_path** (path, tree=None, regex=False, flags=None, first=False)

**find_groups_by_uuid** (uuid, tree=None, regex=False, flags=None, first=False)

**find_groups_by_notes** (notes, tree=None, regex=False, flags=None, first=False)


Adding Entries
--------------
**add_entry** (destination_group, title, username, password, url=None, notes=None, tags=None, expiry_time=None, icon=None, force_creation=False)

**delete_entry** (entry)

**move_entry** (entry, destination_group)

where ``destination_group`` is a ``Group`` instance.  ``entry`` is an ``Entry`` instance. ``title``, ``username``, ``password``, ``url``, ``notes``, ``tags``, ``icon`` are strings. ``expiry_time`` is a ``datetime`` instance.

If ``expiry_time`` is a naive datetime object (i.e. ``expiry_time.tzinfo`` is not set), the timezone is retrieved from ``dateutil.tz.gettz()``.

.. code:: python

   # add a new entry to the Root group
   >>> kp.add_entry(kp.root_group, 'testing', 'foo_user', 'passw0rd')
   Entry: "testing (foo_user)"

   # add a new entry to the social group
   >>> group = find_groups(name='social', first=True)
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

Adding Groups
--------------
**add_group** (destination_group, group_name, icon=None, notes=None)

**delete_group** (group)

**move_group** (group, destination_group)

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

Miscellaneous
-------------
**read** (filename, password=None, keyfile=None)

where ``filename``, ``password``, and ``keyfile`` are strings.  ``filename`` is the path to the database, ``password`` is the master password string, and ``keyfile`` is the path to the database keyfile.  At least one of ``password`` and ``keyfile`` is required.

**save** (filename=None)

where ``filename`` is the path of the file to save to.  If ``filename`` is not given, the path given in ``read`` will be used.

**set_credentials** (password=None, keyfile=None)

clear current database credentials and set to the ones given.  ``password`` and ``keyfile`` are strings.  At least one of ``password`` and ``keyfile`` is required

Tests
-------------

To run them issue :code:`$ python tests/tests.py`
