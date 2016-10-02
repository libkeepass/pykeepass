pykeepass
============

This library allows you to write entries to a KeePass database

.. code-block::

   import pykeepass
   # load database
   kdb = pykeepass.open(
      'db.kdbx',
      password='somePassw0rd'
   ).__enter__()
   # find any group by its name
   group = pykeepass.find_group_by_name(kdb.tree, 'folder1')
   # find any entry by its title
   entry = pykeepass.find_entry(kdb.tree, 'test')
   # retrieve the associated password
   pykeepass.get_entry_password_field(entry).Value
   # write a new entry
   pykeepass.create_entry(
      kdb.tree,
      group,
      'new_entry',
      'myusername',
      'myPassw0rdXX'
   )
   # save database
   with open('/tmp/pykeepass.kdbx', 'w+') as f:
      kdb.write_to(f)
