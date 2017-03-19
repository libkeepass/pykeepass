import unittest
import pykeepass
import icons
from group import Group
from entry import Entry
from datetime import datetime

"""
- save
- read
- __xpath
- add entry
  - update entry - force_creation
  - update mtime
- root group
"""

class EntryFunctionTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.pk = pykeepass.PyKeePass('./test.kdbx', password='passw0rd')

    #---------- Finding entries -----------

    def test_find_entries_by_title(self):
        results = self.pk.find_entries_by_title('root_entry')
        self.assertEqual(len(results), 1)
        self.assertEqual('root_entry', results[0].title)

    def test_find_entries_by_username(self):
        results = self.pk.find_entries_by_username('foobar_user')
        self.assertEqual(len(results), 2)
        self.assertTrue('foobar_user' in [entry.username for entry in results])

    def test_find_entries_by_password(self):
        results = self.pk.find_entries_by_password('passw0rd')
        self.assertEqual(len(results), 2)
        self.assertTrue('group_entry' in [entry.title for entry in results])

    def test_find_entries_by_url(self):
        results = self.pk.find_entries_by_url('http://example.com')
        self.assertEqual(len(results), 2)
        self.assertTrue('group_entry' in [entry.title for entry in results])

    def test_find_entries_by_notes(self):
        results = self.pk.find_entries_by_notes('entry notes')
        self.assertEqual(len(results), 2)
        self.assertTrue('group_entry' in [entry.title for entry in results])

    def test_find_entries_by_path(self):
        results = self.pk.find_entries_by_path('foobar_group/group_entry')
        self.assertIsInstance(results[0], Entry)
        self.assertEqual('group_entry', results[0].title)

    #---------- Adding/Deleting entries -----------

    def test_add_entry(self):
        unique_str = 'test_add_entry_'
        entry = self.pk.add_entry(self.pk.root_group,
                                  unique_str+'title',
                                  unique_str+'user',
                                  unique_str+'pass',
                                  unique_str+'url',
                                  unique_str+'notes',
                                  unique_str+'tags',
                                  icons.KEY)
        results = self.pk.find_entries_by_title(unique_str+'title')
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0].title, unique_str+'title')
        self.assertEqual(results[0].username, unique_str+'user')
        self.assertEqual(results[0].password, unique_str+'pass')
        self.assertEqual(results[0].url, unique_str+'url')
        self.assertEqual(results[0].notes, unique_str+'notes')
        self.assertEqual(results[0].tags, [unique_str+'tags'])
        self.assertEqual(results[0].icon, icons.KEY)


class GroupFunctionTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.pk = pykeepass.PyKeePass('./test.kdbx', password='passw0rd')

    #---------- Finding groups -----------

    def test_find_groups_by_name(self):
        results = self.pk.find_groups_by_name('subgroup')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'subgroup')

    def test_find_groups_by_path(self):
        results = self.pk.find_groups_by_path('/foobar_group/subgroup')

        self.assertIsInstance(results[0], Group)
        self.assertEqual(results[0].name, 'subgroup')

    def test_groups(self):
        results = self.pk.groups

        self.assertEqual(len(results), 4)

    #---------- Adding/Deleting Groups -----------

    def test_add_group(self):
        path = 'base_group/test_add_group'
        self.pk.add_group(path)

        results = self.pk.find_groups_by_path(path)
        self.assertIsInstance(results[0], Group)
        self.assertEqual(results[0].name, 'test_add_group')

class EntryTests(unittest.TestCase):

    def test_fields(self):
        time = datetime.now()
        entry = Entry('title', 'username', 'password',
                    'url', 'notes', 'tags',
                    True, time, icons.KEY)

        self.assertEqual(entry.title, 'title')
        self.assertEqual(entry.username, 'username')
        self.assertEqual(entry.password, 'password')
        self.assertEqual(entry.url, 'url')
        self.assertEqual(entry.notes, 'notes')
        self.assertEqual(entry.expires, True)
        # convert `time` to utc (sans microseconds) before test
        self.assertEqual(entry.expiry_time,
                         (time + (datetime.utcnow() - datetime.now())).replace(microsecond=0))
        self.assertEqual(entry.is_a_history_entry, False)

        entry.set_custom_property('foo', 'bar')
        self.assertEqual(entry.get_custom_property('foo'), 'bar')
        self.assertIn('foo', entry.custom_properties)


if __name__ == '__main__':
    unittest.main()

