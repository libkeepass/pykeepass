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
   >>> group = kp.find_groups_by_name('social', first=True)

   # get the entries in a group
   >>> group.entries
   [Entry: "social/facebook", Entry: "social/twitter"]

   # find any entry by its title
   >>> entry = kp.find_entries_by_title('facebook', first=True)

   # retrieve the associated password
   >>> entry.password
   's3cure_p455w0rd'

   # update an entry
   >>> entry.notes = 'primary facebook account'

   # create a new group
   >>> group = kp.add_group('email')

   # create a new entry
   >>> kp.add_entry(group, 'gmail', 'myusername', 'myPassw0rdXX')

   # save database
   >>> kp.save()


Finding Entries
----------------------

The supported find commands are listed below

* **find_entries_by_title** (title, regex=False, tree=None, history=False, first=False)
* **find_entries_by_username** (username, regex=False, tree=None, history=False, first=False)
* **find_entries_by_password** (password, regex=False, tree=None, history=False, first=False)
* **find_entries_by_url** (url, regex=False, tree=None, history=False, first=False)
* **find_entries_by_notes** (notes, regex=False, tree=None, history=False, first=False)
* **find_entries_by_path** (path, regex=False, tree=None, history=False, first=False)

where ``title``, ``username``, ``password``, ``url``, ``notes`` and ``path`` are strings.  These functions have an optional ``regex`` boolean argument which means to interpret the string as an `XSLT style`_ regular expression.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html

The ``history`` (default ``False``) boolean controls whether history entries should be included in the search results.

The ``first`` (default ``False``) boolean controls whether to return the first matched item, or a list of matched items.
* if ``first=False``, the function returns a list of ``Entry`` s or ``[]`` if there are no matches
* if ``first=True``, the function returns the first ``Entry`` match, or ``None`` if there are no matches

* **entries**

a flattened list of all entries in the database

.. code:: python

   >>> kp.entries
   [Entry: "foo_entry", Entry: "foobar_entry", Entry: "social/gmail", Entry: "social/facebook"]

   >>> kp.find_entries_by_name('gmail', first=True)
   Entry: "social/gmail"

   >>> kp.find_entries_by_name('foo.*', regex=True)
   [Entry: "foo_entry", Entry: "foobar_entry"]

   >>> entry = kp.find_entries_by_url('.*facebook.*', regex=True, first=True)
   >>> entry.url
   'facebook.com'

   >>> kp.find_groups_by_name('social', first=True).entries
   [Entry: "social/gmail", Entry: "social/facebook"]

Finding Groups
----------------------

* **find_groups_by_name** (name, tree=None, regex=False, first=False)
* **find_groups_by_path** (path, tree=None, regex=False, first=False)

where ``name`` and ``path`` are strings.  These functions have an optional ``regex`` boolean argument which means to interpret the string as an `XSLT style`_ regular expression.

.. _XSLT style: https://www.xml.com/pub/a/2003/06/04/tr.html

The ``first`` (default ``False``) boolean controls whether to return the first matched item, or a list of matched items.
* if ``first=False``, the function returns a list of ``Group`` s or ``[]`` if there are no matches
* if ``first=True``, the function returns the first ``Group`` match, or ``None`` if there are no matches

* **root_group**

the ``Root`` group to the database

* **groups**

a flattened list of all groups in the database

.. code:: python

   >>> kp.groups
   [Group: "foo", Group "foobar", Group: "social", Group: "social/foo_subgroup"]
       
   >>> kp.find_groups_by_name('foo', first=True)
   Group: "foo"

   >>> kp.find_groups_by_name('foo.*', regex=True)
   [Group: "foo", Group "foobar"]

   >>> kp.find_groups_by_path('social/.*', regex=True)
   [Group: "social/foo_subgroup"]

   >>> kp.find_groups_by_name('social', first=True).subgroups
   [Group: "social/foo_subgroup"]

   >>> kp.root_group
   Group: "/"


Adding Entries
--------------
* **add_entry** (destination_group, title, username, password, url=None, notes=None, tags=None, icon=None, force_creation=False)

This function adds a new entry to the existing group ``destination_group``.

``destination_group`` is a ``Group`` instance.  ``title``, ``username``, ``password``, ``url``, ``notes``, ``tags``, ``icon`` are strings.

.. code:: python

   # add a new entry to the Root group
   >>> kp.add_entry(kp.root_group, 'testing', 'foo_user', 'passw0rd')
   Entry: "testing"

   # add a new entry to the social group
   >>> group = find_groups_by_name('social', first=True)
   >>> kp.add_entry(group, 'testing', 'foo_user', 'passw0rd')
   Entry: "testing"

Adding Groups
--------------
* **add_group** (destination_group, group_name)

This function adds a new group to the existing group ``destination_group``.

``destination_group`` is a ``Group`` instance.  ``group_name`` is a string.

.. code:: python

   # add a new group to the Root group
   >>> group = kp.add_group(kp.root_group, 'social')

   # add a new subgroup
   >>> kp.add_group(group, 'gmail')
   Group: "social/gmail"
       
