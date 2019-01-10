# -*- coding: utf-8 -*-

# FIXME python2
from __future__ import unicode_literals

from datetime import datetime, timedelta
from dateutil import tz
from pykeepass import icons, PyKeePass
from pykeepass.entry import Entry
from pykeepass.group import Group
from pykeepass.kdbx_parsing import KDBX
from lxml.etree import Element
import os
import shutil
import unittest
import logging

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
logger = logging.getLogger("pykeepass")


class EntryFindTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )

    #---------- Finding entries -----------

    def test_find_entries_by_title(self):
        results = self.kp.find_entries_by_title('root_entry')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_title('Root_entry', regex=True, flags='i', first=True)
        self.assertEqual('root_entry', results.title)

    def test_find_entries_by_username(self):
        results = self.kp.find_entries_by_username('foobar_user')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_username('Foobar_user', regex=True, flags='i', first=True)
        self.assertEqual('foobar_user', results.username)

    def test_find_entries_by_password(self):
        results = self.kp.find_entries_by_password('passw0rd')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_password('Passw0rd', regex=True, flags='i', first=True)
        self.assertEqual('passw0rd', results.password)

    def test_find_entries_by_url(self):
        results = self.kp.find_entries_by_url('http://example.com')
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_url('http://example.com', first=True)
        self.assertEqual('http://example.com', results.url)

    def test_find_entries_by_notes(self):
        results = self.kp.find_entries_by_notes('entry notes')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_notes('entry notes', regex=True)
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries_by_notes('Entry notes', regex=True, flags='i', first=True)
        self.assertEqual('root entry notes', results.notes)

    def test_find_entries_by_path(self):
        results = self.kp.find_entries(path='foobar_group/', title='group_entry')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries(path='foobar_group/group_entry')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries(path='foobar_group/', title='Group_entry', regex=True, flags='i', first=True)
        self.assertIsInstance(results, Entry)
        self.assertEqual('group_entry', results.title)

    def test_find_entries_by_uuid(self):
        results = self.kp.find_entries_by_uuid('zF9+zSoASMqWIcIio0ewuw==')[0]
        self.assertIsInstance(results, Entry)
        self.assertEqual('zF9+zSoASMqWIcIio0ewuw==', results.uuid)
        self.assertEqual('foobar_user', results.username)

    def test_find_entries_by_string(self):
        results = self.kp.find_entries_by_string({'custom_field': 'custom field value'})[0]
        self.assertIsInstance(results, Entry)
        self.assertEqual('custom field value', results.get_custom_property('custom_field'))
        self.assertEqual('HnN4bHSVjEybPf8nOq1bVA==', results.uuid)

    def test_find_entries_by_autotype_sequence(self):
        results = self.kp.find_entries(autotype_sequence='{TAB}', regex=True)
        self.assertEqual(len(results), 1)

    def test_find_entries_by_autotype_enabled(self):
        results = self.kp.find_entries(autotype_enabled=True)
        self.assertEqual(len(results), len(self.kp.entries) - 1)

    def test_find_entries(self):
        results = self.kp.find_entries(title='Root_entry', regex=True)
        self.assertEqual(len(results), 0)
        results = self.kp.find_entries(title='Root_entry', regex=True, flags='i', first=True)
        self.assertEqual('root_entry', results.title)
        results = self.kp.find_entries(url="http://example.com")
        self.assertEqual(len(results), 2)
        results = self.kp.find_entries(notes="entry notes", url="http://example.com")
        self.assertEqual(len(results), 1)
        self.assertTrue(self.kp.find_entries(title='group_entry', first=True) in results)

        # test `group` argument
        results = self.kp.find_entries(title='foobar_entry', group=None)
        self.assertEqual(len(results), 3)
        group = self.kp.find_groups(name='foobar_group', first=True)
        results = self.kp.find_entries(title='foobar_entry', group=group)
        self.assertEqual(len(results), 2)

    #---------- Adding/Deleting entries -----------

    def test_add_delete_move_entry(self):
        unique_str = 'test_add_entry_'
        expiry_time = datetime.now()
        entry = self.kp.add_entry(self.kp.root_group,
                                  unique_str + 'title',
                                  unique_str + 'user',
                                  unique_str + 'pass',
                                  url=unique_str + 'url',
                                  notes=unique_str + 'notes',
                                  tags=unique_str + 'tags',
                                  expiry_time=expiry_time,
                                  icon=icons.KEY)
        results = self.kp.find_entries_by_title(unique_str + 'title')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)

        self.assertEqual(results.title, unique_str + 'title')
        self.assertEqual(results.username, unique_str + 'user')
        self.assertEqual(results.password, unique_str + 'pass')
        self.assertEqual(results.url, unique_str + 'url')
        self.assertEqual(results.notes, unique_str + 'notes')
        self.assertEqual(results.tags, [unique_str + 'tags'])
        self.assertTrue(results.uuid != None)
        # convert naive datetime to utc
        expiry_time_utc = expiry_time.replace(tzinfo=tz.gettz()).astimezone(tz.gettz('UTC'))
        self.assertEqual(results.icon, icons.KEY)

        sub_group = self.kp.add_group(self.kp.root_group, 'sub_group')
        self.kp.move_entry(entry, sub_group)
        results = self.kp.find_entries(path='sub_group/', title='test_add_entry_title', first=True)
        self.assertEqual(results.title, entry.title)

        self.kp.delete_entry(entry)
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)
        self.assertIsNone(results)

        # test adding entry which exists in another group
        subgroup = self.kp.find_groups(name='subgroup2', first=True)
        self.kp.add_entry(subgroup, title='foobar_entry', username='foobar', password='foobar')

        # test adding entry to root which exists in subgroup
        self.kp.add_entry(subgroup, title='foobar_entry2', username='foobar', password='foobar')
        self.kp.add_entry(self.kp.root_group, title='foobar_entry2', username='foobar', password='foobar')

    #---------- Entries name collision exception -----------

    def test_raise_exception_entry(self):
        unique_str = 'test_add_entry_'
        entry = self.kp.add_entry(self.kp.root_group,
                                  unique_str + 'title',
                                  unique_str + 'user',
                                  unique_str + 'pass',
                                  url=unique_str + 'url',
                                  notes=unique_str + 'notes',
                                  tags=unique_str + 'tags',
                                  icon=icons.KEY)
        self.assertRaises(Exception, entry)

    # ---------- Entries representation -----------

    def test_print_entries(self):
        self.assertIsInstance(self.kp.entries.__repr__(), str)

        e = self.kp.find_entries(title='Тест', first=True)
        e.save_history()
        self.assertIsInstance(e.__repr__(), str)
        self.assertIsInstance(e.history.__repr__(), str)

class GroupFindTests(unittest.TestCase):

    # get some things ready before testing
    def setUp(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )

    #---------- Finding groups -----------

    def test_find_groups_by_name(self):
        results = self.kp.find_groups_by_name('subgroup')
        self.assertEqual(len(results), 1)
        results = self.kp.find_groups_by_name('subgroup', first=True)
        self.assertEqual(results.name, 'subgroup')
        g = self.kp.find_groups(name='foobar_group', first=True)
        results = self.kp.find_groups(group=g, name='.*group.*', regex=True)
        self.assertEqual(len(results), 2)
        results = self.kp.find_groups(group=g, name='.*group.*', regex=True, recursive=False)
        self.assertEqual(len(results), 1)

    def test_find_groups_by_path(self):
        results = self.kp.find_groups_by_path('/foobar_group/subgroup/')
        self.assertIsInstance(results[0], Group)
        results = self.kp.find_groups(path='/foobar_group/', name='subgroup', first=True)
        self.assertEqual(results.name, 'subgroup')

    def test_find_groups_by_uuid(self):
        results = self.kp.find_groups_by_uuid('lRVaMlMXoQ/U5NDCAwJktg==', first=True)
        self.assertIsInstance(results, Group)
        results = self.kp.find_groups(uuid='^lRVaMlMX|^kwTZdSoU', regex=True)
        self.assertEqual(len(results), 2)

    def test_find_groups_by_notes(self):
        results = self.kp.find_groups(notes='group notes')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].uuid, 'lRVaMlMXoQ/U5NDCAwJktg==')

    def test_find_groups(self):
        results = self.kp.find_groups(path='/foobar_group/')
        self.assertIsInstance(results[0], Group)
        results = self.kp.find_groups(path='/foobar_group/', name='subgroup', first=True)
        self.assertEqual(results.name, 'subgroup')

    def test_groups(self):
        results = self.kp.groups

        self.assertEqual(len(results), 6)

    #---------- Adding/Deleting Groups -----------

    def test_add_delete_move_group(self):
        notes_text = "this is a note for a group!"
        base_group = self.kp.add_group(self.kp.root_group, 'base_group', notes=notes_text)
        sub_group = self.kp.add_group(base_group, 'sub_group')
        sub_group2 = self.kp.add_group(base_group, 'sub_group2')

        self.assertEqual(base_group.notes, notes_text)
        base_group.notes = ''
        self.assertEqual(base_group.notes, '')

        results = self.kp.find_groups(path='base_group/', name='sub_group', first=True)
        self.assertIsInstance(results, Group)
        self.assertEqual(results.name, sub_group.name)
        self.assertTrue(results.uuid != None)

        self.kp.move_group(sub_group2, sub_group)
        results = self.kp.find_groups(path='base_group/sub_group/', name='sub_group2', first=True)
        self.assertEqual(results.name, sub_group2.name)

        self.kp.delete_group(sub_group)
        results = self.kp.find_groups(path='base_group/', name='sub_group', first=True)
        self.assertIsNone(results)

        # ---------- Groups representation -----------

    def test_print_groups(self):
        self.assertIsInstance(self.kp.groups.__repr__(), str)


class EntryTests(unittest.TestCase):
    # get some things ready before testing
    def setUp(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )

    def test_fields(self):
        time = datetime.now()
        entry = Entry(
            'title',
            'username',
            'password',
            url='url',
            notes='notes',
            tags='tags',
            expires=True,
            expiry_time=time,
            icon=icons.KEY,
            kp=self.kp
        )

        self.assertEqual(entry.title, 'title')
        self.assertEqual(entry.username, 'username')
        self.assertEqual(entry.password, 'password')
        self.assertEqual(entry.url, 'url')
        self.assertEqual(entry.notes, 'notes')
        self.assertEqual(entry.tags, ['tags'])
        self.assertEqual(entry.expires, True)
        self.assertEqual(entry.expiry_time,
                         time.replace(tzinfo=tz.gettz()).astimezone(tz.gettz('UTC')))
        self.assertEqual(entry.icon, icons.KEY)
        self.assertEqual(entry.is_a_history_entry, False)
        self.assertEqual(self.kp.find_entries(title='subentry', first=True).path, 'foobar_group/subgroup/subentry')
        self.assertEqual(
            self.kp.find_entries(title='root_entry', first=True).history[0].group,
            self.kp.root_group
        )

    def test_set_and_get_fields(self):
        time = datetime.now()
        changed_time = datetime.now() + timedelta(hours=9)
        changed_string = 'changed_'
        entry = Entry(
            'title',
            'username',
            'password',
            url='url',
            notes='notes',
            tags='tags',
            expires=True,
            expiry_time=time,
            icon=icons.KEY,
            kp=self.kp
        )
        entry.title = changed_string + 'title'
        entry.username = changed_string + 'username'
        entry.password = changed_string + 'password'
        entry.url = changed_string + 'url'
        entry.notes = changed_string + 'notes'
        entry.expires = False
        entry.expiry_time = changed_time
        entry.icon = icons.GLOBE
        entry.set_custom_property('foo', 'bar')

        self.assertEqual(entry.title, changed_string + 'title')
        self.assertEqual(entry.username, changed_string + 'username')
        self.assertEqual(entry.password, changed_string + 'password')
        self.assertEqual(entry.url, changed_string + 'url')
        self.assertEqual(entry.notes, changed_string + 'notes')
        self.assertEqual(entry.icon, icons.GLOBE)
        self.assertEqual(entry.get_custom_property('foo'), 'bar')
        self.assertIn('foo', entry.custom_properties)
        entry.delete_custom_property('foo')
        self.assertEqual(entry.get_custom_property('foo'), None)
        # test time properties
        self.assertEqual(entry.expires, False)
        self.assertEqual(entry.expiry_time,
                         changed_time.replace(tzinfo=tz.gettz()).astimezone(tz.gettz('UTC')))

        entry.tags = 'changed_tags'
        self.assertEqual(entry.tags, ['changed_tags'])
        entry.tags = 'changed;tags'
        self.assertEqual(entry.tags, ['changed', 'tags'])
        entry.tags = ['changed', 'again', 'tags']
        self.assertEqual(entry.tags, ['changed', 'again', 'tags'])

    def test_expired_datetime_offset(self):
        """Test for https://github.com/pschmitt/pykeepass/issues/115"""
        future_time = datetime.now() + timedelta(days=1)
        past_time = datetime.now() - timedelta(days=1)
        entry = Entry(
            'title',
            'username',
            'password',
            expires=True,
            expiry_time=future_time,
            kp=self.kp
        )
        self.assertFalse(entry.expired)

        entry.expiry_time = past_time
        self.assertTrue(entry.expired)

    def test_autotype_no_default_sequence(self):
        entry = Entry(
            'title',
            'username',
            'password',
            # create an element, but one without AutoType
            element=Element('Entry'),
            kp=self.kp
        )
        self.assertIsNone(entry.autotype_sequence)

    def test_add_remove_attachment(self):
        entry = self.kp.add_entry(
            self.kp.root_group,
            title='title',
            username='username',
            password='password',
        )

        num_attach = len(entry.attachments)
        entry.add_attachment(0, 'foobar.txt')
        entry.add_attachment(0, 'foobar2.txt')
        self.assertEqual(len(entry.attachments), num_attach + 2)
        a = self.kp.find_attachments(id=0, filename='foobar.txt', first=True)
        self.assertEqual(a.filename, 'foobar.txt')
        self.assertEqual(a.id, 0)
        entry.delete_attachment(a)
        self.assertEqual(len(entry.attachments), num_attach + 1)
        self.assertEqual(entry.attachments[0].filename, 'foobar2.txt')


class GroupTests(unittest.TestCase):
    # get some things ready before testing
    def setUp(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )

    def test_fields(self):
        self.assertEqual(self.kp.find_groups(name='subgroup2', first=True).path, 'foobar_group/subgroup/subgroup2')


class AttachmentTests(unittest.TestCase):
    # get some things ready before testing
    def setUp(self):
        shutil.copy(
            os.path.join(base_dir, 'test3.kdbx'),
            os.path.join(base_dir, 'test3_attachments.kdbx')
        )
        shutil.copy(
            os.path.join(base_dir, 'test4.kdbx'),
            os.path.join(base_dir, 'test4_attachments.kdbx')
        )
        self.open()

    def open(self):
        self.kp3 = PyKeePass(
            os.path.join(base_dir, 'test3_attachments.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test3.key')
        )
        self.kp4 = PyKeePass(
            os.path.join(base_dir, 'test4_attachments.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test4.key')
        )

    def test_create_delete_attachment(self):
        attachment_id3 = self.kp3.add_binary(b'Ronald McDonald Trump')
        attachment_id4 = self.kp4.add_binary(b'Ronald McDonald Trump')
        self.kp3.save()
        self.kp4.save()
        self.open()
        self.assertEqual(self.kp3.binaries[-1], b'Ronald McDonald Trump')
        self.assertEqual(self.kp4.binaries[-1], b'Ronald McDonald Trump')

        num_attach3 = len(self.kp3.binaries)
        num_attach4 = len(self.kp4.binaries)
        self.kp3.delete_binary(len(self.kp3.binaries) - 1)
        self.kp4.delete_binary(len(self.kp4.binaries) - 1)
        self.kp3.save()
        self.kp4.save()
        self.open()
        self.assertEqual(len(self.kp3.binaries), num_attach3 - 1)
        self.assertEqual(len(self.kp4.binaries), num_attach4 - 1)

    def test_attachment_reference_decrement(self):
        e = self.kp3.entries[0]

        attachment_id = self.kp3.add_binary(b'foobar')
        attachment_id2 = self.kp3.add_binary(b'foobar2')

        attachment1 = e.add_attachment(attachment_id, 'foo.txt')
        attachment2 = e.add_attachment(attachment_id2, 'foo.txt')

        self.kp3.delete_binary(attachment_id)

        self.assertEqual(attachment2.id, attachment_id2 - 1)

    def tearDown(self):
        os.remove(os.path.join(base_dir, 'test3_attachments.kdbx'))
        os.remove(os.path.join(base_dir, 'test4_attachments.kdbx'))


class PyKeePassTests(unittest.TestCase):
    def setUp(self):
        shutil.copy(
            os.path.join(base_dir, 'test.kdbx'),
            os.path.join(base_dir, 'change_creds.kdbx')
        )
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )
        self.kp_tmp = PyKeePass(
            os.path.join(base_dir, 'change_creds.kdbx'),
            password='password',
            keyfile=os.path.join(base_dir, 'test.key')
        )

    def test_set_credentials(self):
        self.kp_tmp.password = 'f00bar'
        self.kp_tmp.keyfile = os.path.join(base_dir, 'change.key')
        self.kp_tmp.save()
        self.kp_tmp = PyKeePass(
            os.path.join(base_dir, 'change_creds.kdbx'),
            password='f00bar',
            keyfile=os.path.join(base_dir, 'change.key')
        )

        results = self.kp.find_entries_by_username('foobar_user', first=True)
        self.assertEqual('foobar_user', results.username)

    def test_dump_xml(self):
        self.kp.dump_xml('db_dump.xml')
        with open('db_dump.xml') as f:
            first_line = f.readline()
            self.assertEqual(first_line, '<?xml version=\'1.0\' encoding=\'utf-8\' standalone=\'yes\'?>\n')

    def test_db_info(self):
        self.assertEqual(self.kp.version, (3, 1))
        self.assertEqual(self.kp.encryption_algorithm, 'aes256')

    def tearDown(self):
        os.remove(os.path.join(base_dir, 'change_creds.kdbx'))


class CtxManagerTests(unittest.TestCase):
    def test_ctx_manager(self):
        with PyKeePass(os.path.join(base_dir, 'test.kdbx'), password='password', keyfile=base_dir + '/test.key') as kp:
            results = kp.find_entries_by_username('foobar_user', first=True)
            self.assertEqual('foobar_user', results.username)

class KDBXTests(unittest.TestCase):

    def test_open_save(self):
        """try to open all databases, save them, then open the result"""

        databases = [
            'test3.kdbx',          # KDBX v3 test
            'test4.kdbx',          # KDBX v4 test
            'test4_aes.kdbx',      # KDBX v4 AES test
            'test4_chacha20.kdbx', # KDBX v4 ChaCha test
            'test4_twofish.kdbx',  # KDBX v4 Twofish test
            'test4_hex.kdbx',      # legacy 64 byte hexadecimal keyfile test
            'test4.kdbx',          # KDBX v4 transformed_key open test
        ]
        passwords = [
            'password',
            'password',
            'password',
            'password',
            'password',
            'password',
            None,
        ]
        transformed_keys = [
            None,
            None,
            None,
            None,
            None,
            None,
            b'&Kgm\x80\xb2tX\x19\x16~Y\xacz\xc4\x07\xc0\xbb\xe6eK\xd6 \xa13\xe8\x85Z\x1e{\x94\x93',
        ]
        keyfiles = [
            'test3.key',
            'test4.key',
            'test4.key',
            'test4.key',
            'test4.key',
            'test4_hex.key',
            None,
        ]
        encryption_algorithms = [
            'aes256',
            'chacha20',
            'aes256',
            'chacha20',
            'twofish',
            'chacha20',
            'chacha20',
        ]
        kdf_algorithms = [
            'aeskdf',
            'argon2',
            'argon2',
            'argon2',
            'argon2',
            'argon2',
            'argon2',
        ]

        for (database, password, transformed_key,
             keyfile, encryption_algorithm, kdf_algorithm) in zip(
                databases, passwords, transformed_keys,
                keyfiles, encryption_algorithms, kdf_algorithms
        ):

            kp = PyKeePass(
                os.path.join(base_dir, database),
                password,
                None if keyfile is None else os.path.join(base_dir, keyfile),
                transformed_key=transformed_key
            )
            self.assertEqual(kp.encryption_algorithm, encryption_algorithm)
            self.assertEqual(kp.kdf_algorithm, kdf_algorithm)

            KDBX.parse(
                KDBX.build(
                    kp.kdbx,
                    password=password,
                    keyfile=None if keyfile is None else os.path.join(base_dir, keyfile),
                    transformed_key=transformed_key
                ),
                password=password,
                keyfile=None if keyfile is None else os.path.join(base_dir, keyfile),
                transformed_key=transformed_key
            )

if __name__ == '__main__':
    unittest.main()

