pykeepass
============

This library allows you to write entries to a KeePass database

.. code-block::

   import pykeepass
   # load database
   pykeepass.read(
      'db.kdbx',
      password='somePassw0rd'
   )
   # find any group by its name
   group = pykeepass.find_group_by_name('folder1')
   # find any entry by its title
   entry = pykeepass.find_entry('test')
   # retrieve the associated password
   pykeepass.get_entry_password_field(entry).Value
   # write a new entry
   pykeepass.create_entry(
      group,
      'new_entry',
      'myusername',
      'myPassw0rdXX'
   )
   # save database
   pykeepass.write_to('/tmp/pykeepass.kdbx')
