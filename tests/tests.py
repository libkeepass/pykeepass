from datetime import datetime
from dateutil import tz
from pykeepass import icons
from pykeepass import pykeepass
from pykeepass.entry import Entry
from pykeepass.group import Group
import os
import shutil
import unittest

"""
Missing Tests:

- add entry
  - force_creation
- root_group
- Group attribute tests
- Entry attribute tests
  - ctime - get/set
  - atime - get/set
  - mtime - get/set
  - expiry_time - get/set
"""

base_dir = os.path.dirname(os.path.realpath(__file__))


class EntryFunctionTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.kp = pykeepass.PyKeePass(base_dir + '/test.kdbx', password='passw0rd', keyfile=base_dir + '/test.key')

    #---------- Finding entries -----------

    def test_find_entries_by_title(self):
        results = self.kp.find_entries_by_title('root_entry')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_title('root_entry', first=True)
        self.assertEqual('root_entry', results.title)

    def test_find_entries_by_username(self):
        results = self.kp.find_entries_by_username('foobar_user')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_username('foobar_user', first=True)
        self.assertEqual('foobar_user', results.username)

    def test_find_entries_by_password(self):
        results = self.kp.find_entries_by_password('passw0rd')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_password('passw0rd', first=True)
        self.assertEqual('passw0rd', results.password)

    def test_find_entries_by_url(self):
        results = self.kp.find_entries_by_url('http://example.com')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_url('http://example.com', first=True)
        self.assertEqual('http://example.com', results.url)

    def test_find_entries_by_notes(self):
        results = self.kp.find_entries_by_notes('entry notes')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_notes('entry notes', first=True)
        self.assertEqual('entry notes', results.notes)

    def test_find_entries_by_path(self):
        results = self.kp.find_entries_by_path('foobar_group/group_entry')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_path('foobar_group/group_entry', first=True)
        self.assertIsInstance(results, Entry)
        self.assertEqual('group_entry', results.title)

    #---------- Adding/Deleting entries -----------

    def test_add_delete_entry(self):
        unique_str = 'test_add_entry_'
        expiry_time = datetime.now()
        entry = self.kp.add_entry(self.kp.root_group,
                                  unique_str+'title',
                                  unique_str+'user',
                                  unique_str+'pass',
                                  url=unique_str+'url',
                                  notes=unique_str+'notes',
                                  tags=unique_str+'tags',
                                  expiry_time=expiry_time,
                                  icon=icons.KEY)
        results = self.kp.find_entries_by_title(unique_str+'title')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_title(unique_str+'title', first=True)

        self.assertEqual(results.title, unique_str+'title')
        self.assertEqual(results.username, unique_str+'user')
        self.assertEqual(results.password, unique_str+'pass')
        self.assertEqual(results.url, unique_str+'url')
        self.assertEqual(results.notes, unique_str+'notes')
        self.assertEqual(results.tags, [unique_str+'tags'])
        # convert naive datetime to utc
        expiry_time_utc = expiry_time.replace(tzinfo=tz.gettz()).astimezone(tz.gettz('UTC'))
        self.assertEqual(results.icon, icons.KEY)

        self.kp.delete_entry(entry)
        results = self.kp.find_entries_by_title(unique_str+'title', first=True)
        self.assertIsNone(results)

    #---------- Entries name collision exception -----------

    def test_raise_exception_entry(self):
        unique_str = 'test_add_entry_'
        entry = self.kp.add_entry(self.kp.root_group,
                                  unique_str+'title',
                                  unique_str+'user',
                                  unique_str+'pass',
                                  url=unique_str+'url',
                                  notes=unique_str+'notes',
                                  tags=unique_str+'tags',
                                  icon=icons.KEY)
        self.assertRaises(Exception, entry)

    # ---------- Entries representation -----------

    def test_print_entries(self):
        self.assertIsInstance(self.kp.entries.__repr__(), str)

class GroupFunctionTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.kp = pykeepass.PyKeePass(base_dir + '/test.kdbx', password='passw0rd', keyfile=base_dir + '/test.key')

    #---------- Finding groups -----------

    def test_find_groups_by_name(self):
        results = self.kp.find_groups_by_name('subgroup')
        self.assertEqual(len(results), 1)
        results = self.kp.find_groups_by_name('subgroup', first=True)
        self.assertEqual(results.name, 'subgroup')

    def test_find_groups_by_path(self):
        results = self.kp.find_groups_by_path('/foobar_group/subgroup')
        self.assertIsInstance(results[0], Group)
        results = self.kp.find_groups_by_path('/foobar_group/subgroup', first=True)
        self.assertEqual(results.name, 'subgroup')

    def test_groups(self):
        results = self.kp.groups

        self.assertEqual(len(results), 5)

    #---------- Adding/Deleting Groups -----------

    def test_add_delete_group(self):
        base_group_name = 'base_group'
        sub_group_name = 'sub_group'
        base_group = self.kp.add_group(self.kp.root_group, base_group_name)
        sub_group = self.kp.add_group(base_group, sub_group_name)

        results = self.kp.find_groups_by_path(base_group_name + '/' + sub_group_name,
                                              first=True)
        self.assertIsInstance(results, Group)
        self.assertEqual(results.name, sub_group_name)

        self.kp.delete_group(sub_group)
        results = self.kp.find_groups_by_path(base_group_name + '/' + sub_group_name,
                                              first=True)
        self.assertIsNone(results)

        # ---------- Groups representation -----------

    def test_print_groups(self):
        self.assertIsInstance(self.kp.groups.__repr__(), str)


class EntryTests(unittest.TestCase):

    def test_fields(self):
        time = datetime.now()
        entry = Entry('title',
                      'username',
                      'password',
                      url='url',
                      notes='notes',
                      tags='tags',
                      expires=True,
                      expiry_time=time,
                      icon=icons.KEY)

        self.assertEqual(entry.title, 'title')
        self.assertEqual(entry.username, 'username')
        self.assertEqual(entry.password, 'password')
        self.assertEqual(entry.url, 'url')
        self.assertEqual(entry.notes, 'notes')
        self.assertEqual(entry.expires, True)
        self.assertEqual(entry.expiry_time,
                         time.replace(tzinfo=tz.gettz()).astimezone(tz.gettz('UTC')))
        self.assertEqual(entry.is_a_history_entry, False)

        entry.set_custom_property('foo', 'bar')
        self.assertEqual(entry.get_custom_property('foo'), 'bar')
        self.assertIn('foo', entry.custom_properties)


class PyKeePassTests(unittest.TestCase):
    def setUp(self):
        shutil.copy(base_dir + '/test.kdbx', base_dir + '/change_pass.kdbx')
        self.kp = pykeepass.PyKeePass(base_dir + '/test.kdbx', password='passw0rd', keyfile=base_dir + '/test.key')
        self.kp_pass = pykeepass.PyKeePass(base_dir + '/change_pass.kdbx', password='passw0rd', keyfile=base_dir + '/test.key')

    def test_set_password(self):
        self.kp_pass.set_password('f00bar')
        self.kp_pass.save()
        self.kp_pass = pykeepass.PyKeePass(base_dir + '/change_pass.kdbx', password='f00bar', keyfile=base_dir + '/test.key')

        results = self.kp.find_entries_by_username('foobar_user', first=True)
        self.assertEqual('foobar_user', results.username)


    def tearDown(self):
        os.remove(base_dir + '/change_pass.kdbx')


if __name__ == '__main__':
    unittest.main()

