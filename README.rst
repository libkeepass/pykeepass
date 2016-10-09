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

   # get the entries in a group
   group.entries

   # find any entry by its title
   entry = pk.find_entry_by_title('test')

   # retrieve the associated password
   entry.password

   # update an entry
   entry.notes = 'this is a test'

   # write a new entry
   pk.create_entry(
      group,
      'new_entry',
      'myusername',
      'myPassw0rdXX'
   )

   # save database
   pk.save('/tmp/pykeepass.kdbx')
