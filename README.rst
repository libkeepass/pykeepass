pykeepass
============

This library allows you to write entries to a KeePass database

.. code-block::

   from pykeepass import PyKeePass

   # load database
   kp = PyKeePass(
      'db.kdbx',
      password='somePassw0rd'
   )

   # find any group by its name
   group = pk.find_group_by_name('folder1')

   # find any entry by its title
   entry = pk.find_entry('test')

   # retrieve the associated password
   pk.get_entry_password_field(entry).Value

   # write a new entry
   pk.create_entry(
      group,
      'new_entry',
      'myusername',
      'myPassw0rdXX'
   )

   # save database
   pk.write_to('/tmp/pykeepass.kdbx')
