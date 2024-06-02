import logging
import os
import shutil
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

from pykeepass import PyKeePass, icons
from pykeepass.entry import Entry
from pykeepass.exceptions import BinaryError, CredentialsError, HeaderChecksumError
from pykeepass.group import Group

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

base_dir = Path(os.path.dirname(os.path.realpath(__file__)))
logger = logging.getLogger("pykeepass")


class KDBX3Tests(unittest.TestCase):
    database = base_dir / 'test3.kdbx'
    password = 'password'
    keyfile = base_dir / 'test3.key'

    database_tmp = base_dir / 'test3_tmp.kdbx'
    keyfile_tmp = base_dir / 'test3_tmp.key'

    # get some things ready before testing
    def setUp(self):
        shutil.copy(self.database, self.database_tmp)
        shutil.copy(self.keyfile, self.keyfile_tmp)
        self.kp = PyKeePass(
            base_dir / self.database,
            password=self.password,
            keyfile=base_dir / self.keyfile
        )
        # for tests which modify the database, use this
        self.kp_tmp = PyKeePass(
            base_dir / self.database_tmp,
            password=self.password,
            keyfile=base_dir / self.keyfile_tmp
        )

    def tearDown(self):
        os.remove(self.keyfile_tmp)
        os.remove(self.database_tmp)


class KDBX4Tests(KDBX3Tests):
    database = base_dir / 'test4.kdbx'
    password = 'password'
    keyfile = base_dir / 'test4.key'

    database_tmp = base_dir / 'test4_tmp.kdbx'
    keyfile_tmp = base_dir / 'test4_tmp.key'


class EntryFindTests3(KDBX3Tests):

    # ---------- Finding entries -----------

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
        results = self.kp.find_entries(path=['foobar_group', 'group_entry'])
        self.assertIsInstance(results, Entry)
        results = self.kp.find_entries(path=['foobar_group'])
        self.assertEqual(results, None)
        results = self.kp.find_entries(path=['foobar_group', 'Group_entry'], regex=True, flags='i', first=True)
        self.assertIsInstance(results, Entry)
        self.assertEqual('group_entry', results.title)

    def test_find_entries_by_uuid(self):
        uu = uuid.UUID('cc5f7ecd-2a00-48ca-9621-c222a347b0bb')
        results = self.kp.find_entries_by_uuid(uu)[0]
        self.assertIsInstance(results, Entry)
        self.assertEqual(uu, results.uuid)
        self.assertEqual('foobar_user', results.username)

    def test_find_entries_by_tags(self):
        results = self.kp.find_entries(tags=['tag1', 'tag2'], first=True)
        self.assertIsInstance(results, Entry)
        self.assertEqual('foobar_entry', results.title)

    def test_find_entries_by_string(self):
        results = self.kp.find_entries_by_string({'custom_field': 'custom field value'})[0]
        self.assertIsInstance(results, Entry)
        self.assertEqual('custom field value', results.get_custom_property('custom_field'))
        uu = uuid.UUID('1e73786c-7495-8c4c-9b3d-ff273aad5b54')
        self.assertEqual(uu, results.uuid)

    def test_find_entries_by_autotype_sequence(self):
        results = self.kp.find_entries(autotype_sequence='{TAB}', regex=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].autotype_sequence, '{USERNAME}{TAB}{PASSWORD}{ENTER}')

    def test_find_entries_by_autotype_window(self):
        results = self.kp.find_entries(autotype_window='test', regex=True, flags="i")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].autotype_window, 'TEST')

    def test_find_entries_by_autotype_enabled(self):
        results = self.kp.find_entries(autotype_enabled=True)
        self.assertEqual(len(results), len(self.kp.entries) - 1)

    def test_find_entries_by_otp(self):
        results = self.kp.find_entries(otp='nonmatch', regex=True, flags='i')
        self.assertEqual(len(results), 0)
        results = self.kp.find_entries(otp='OTPSECRETT', regex=True)
        self.assertEqual(len(results), 1)
        self.assertEqual('foobar_entry', results[0].title)
        import pyotp
        self.assertEqual(len(pyotp.parse_uri(results[0].otp).now()), 6)

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

    # ---------- History -----------

    def test_is_a_history_entry(self):
        for title in ["root_entry", "subentry"]:
            res1 = self.kp.find_entries(title=title)
            for entry in res1:
                self.assertFalse(entry.is_a_history_entry)
            res2 = self.kp.find_entries(title=title, history=True)
            self.assertTrue(len(res2) > len(res1))
            for entry in res2:
                if entry not in res1:
                    self.assertTrue(entry.is_a_history_entry)

    def test_history(self):
        entry = self.kp.find_entries(title="subentry2", first=True)
        hist = entry.history
        self.assertIsInstance(hist, list)
        self.assertEqual(len(hist), 0)

        entry = self.kp.find_entries(title="subentry", first=True)
        hist = entry.history
        self.assertIsInstance(hist, list)
        self.assertEqual(len(hist), 4)
        self.assertEqual(len(set(hist)), 4)
        self.assertNotEqual(hist[0], hist[1])

    def test_history_path(self):
        for title in ["root_entry", "subentry"]:
            entry = self.kp.find_entries(title=title, first=True)
            hist = entry.history
            self.assertTrue(len(hist) > 0)
            for item in hist:
                self.assertEqual(item.path, entry.path)

    def test_history_group(self):
        for title in ["root_entry", "subentry"]:
            entry = self.kp.find_entries(title=title, first=True)
            grp1 = entry.group
            hist = entry.history
            self.assertTrue(len(hist) > 0)
            for item in hist:
                grp2 = item.group
                self.assertEqual(grp1, grp2)

    # ---------- Adding/Deleting entries -----------

    def test_add_delete_move_entry(self):
        unique_str = 'test_add_entry_'
        expiry_time = datetime.now(timezone.utc)
        entry = self.kp.add_entry(
            self.kp.root_group,
            unique_str + 'title',
            unique_str + 'user',
            unique_str + 'pass',
            url=unique_str + 'url',
            notes=unique_str + 'notes',
            tags=['tag1', 'tag2', 'tag3;tag4', 'tag5,tag6'],
            expiry_time=expiry_time,
            icon=icons.KEY
        )
        results = self.kp.find_entries_by_title(unique_str + 'title')
        self.assertEqual(len(results), 1)
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)

        self.assertEqual(results.title, unique_str + 'title')
        self.assertEqual(results.username, unique_str + 'user')
        self.assertEqual(results.password, unique_str + 'pass')
        self.assertEqual(results.url, unique_str + 'url')
        self.assertEqual(results.notes, unique_str + 'notes')
        self.assertEqual(len(results.tags), 6)
        self.assertTrue(results.uuid is not None)
        self.assertTrue(results.autotype_sequence is None)
        self.assertEqual(results.icon, icons.KEY)

        sub_group = self.kp.add_group(self.kp.root_group, 'sub_group')
        self.kp.move_entry(entry, sub_group)
        results = self.kp.find_entries(path=['sub_group', 'test_add_entry_title'], first=True)
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


    def test_raise_exception_entry(self):
        # Entries name collision exception
        unique_str = 'test_add_entry_'
        entry = self.kp.add_entry(
            self.kp.root_group,
            unique_str + 'title',
            unique_str + 'user',
            unique_str + 'pass',
            url=unique_str + 'url',
            notes=unique_str + 'notes',
            tags=unique_str + 'tags',
            icon=icons.KEY
        )
        self.assertRaises(Exception, entry)

    # ---------- Timezone test -----------

    def test_expiration_time_tz(self):
        # The expiration date is compared in UTC
        # setting expiration date with tz offset 6 hours should result in expired entry
        unique_str = 'test_exptime_tz_1_'
        expiry_time = datetime.now(timezone(offset=timedelta(hours=6))).replace(microsecond=0)
        self.kp.add_entry(
            self.kp.root_group,
            unique_str + 'title',
            unique_str + 'user',
            unique_str + 'pass',
            expiry_time=expiry_time
        )
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)
        self.assertEqual(results.expired, True)
        self.assertEqual(results.expiry_time, expiry_time.astimezone(timezone.utc))

        # setting expiration date with UTC tz should result in expired entry
        unique_str = 'test_exptime_tz_2_'
        expiry_time = datetime.now(timezone.utc).replace(microsecond=0)
        self.kp.add_entry(
            self.kp.root_group,
            unique_str + 'title',
            unique_str + 'user',
            unique_str + 'pass',
            expiry_time=expiry_time
        )
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)
        self.assertEqual(results.expired, True)
        self.assertEqual(results.expiry_time, expiry_time.astimezone(timezone.utc))

        # setting expiration date with tz offset -6 hours while adding 6 hours should result in valid entry
        unique_str = 'test_exptime_tz_3_'
        expiry_time = datetime.now(timezone(offset=timedelta(hours=-6))).replace(microsecond=0) + timedelta(hours=6)
        self.kp.add_entry(
            self.kp.root_group,
            unique_str + 'title',
            unique_str + 'user',
            unique_str + 'pass',
            expiry_time=expiry_time
        )
        results = self.kp.find_entries_by_title(unique_str + 'title', first=True)
        self.assertEqual(results.expired, False)
        self.assertEqual(results.expiry_time, expiry_time.astimezone(timezone.utc))

    # ---------- Entries representation -----------

    def test_print_entries(self):
        self.assertIsInstance(self.kp.entries.__repr__(), str)

        e = self.kp.find_entries(title='Тест', first=True)
        e.save_history()
        self.assertIsInstance(e.__repr__(), str)
        self.assertIsInstance(e.history.__repr__(), str)

        # issue 250
        e = self.kp.find_entries(username='blank_title', first=True)
        self.assertIsNot(e, None)
        self.assertIsInstance(e.__repr__(), str)


class GroupFindTests3(KDBX3Tests):

    # ---------- Finding groups -----------

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
        results = self.kp.find_groups_by_path(['foobar_group', 'subgroup'])
        self.assertIsInstance(results, Group)
        results = self.kp.find_groups(path=['foobar_group', 'subgroup'], first=True)
        self.assertEqual(results.name, 'subgroup')
        results = self.kp.find_groups(path=['foobar_group', 'group_entry'])
        self.assertEqual(results, None)

    def test_find_groups_by_uuid(self):
        uu = uuid.UUID('95155a32-5317-a10f-d4e4-d0c2030264b6')
        results = self.kp.find_groups_by_uuid(uu, first=True)
        self.assertIsInstance(results, Group)
        results = self.kp.find_groups(uuid=uu, regex=True)
        self.assertEqual(len(results), 1)

    def test_find_groups_by_notes(self):
        results = self.kp.find_groups(notes='group notes')
        self.assertEqual(len(results), 1)
        uu = uuid.UUID('95155a32-5317-a10f-d4e4-d0c2030264b6')
        self.assertEqual(results[0].uuid, uu)

    def test_groups(self):
        results = self.kp.groups

        self.assertEqual(len(results), 7)

    # ---------- Adding/Deleting Groups -----------

    def test_add_delete_move_group(self):
        notes_text = "this is a note for a group!"
        base_group = self.kp.add_group(self.kp.root_group, 'base_group', notes=notes_text)
        sub_group = self.kp.add_group(base_group, 'sub_group')
        sub_group2 = self.kp.add_group(base_group, 'sub_group2')

        self.assertEqual(base_group.notes, notes_text)
        base_group.notes = ''
        self.assertEqual(base_group.notes, '')

        results = self.kp.find_groups(path=['base_group', 'sub_group'], first=True)
        self.assertIsInstance(results, Group)
        self.assertEqual(results.name, sub_group.name)
        self.assertTrue(results.uuid is not None)

        self.kp.move_group(sub_group2, sub_group)
        results = self.kp.find_groups(path=['base_group', 'sub_group', 'sub_group2'], first=True)
        self.assertEqual(results.name, sub_group2.name)

        self.kp.delete_group(sub_group)
        results = self.kp.find_groups(path=['base_group', 'sub_group'], first=True)
        self.assertIsNone(results)

        # ---------- Groups representation -----------

    def test_print_groups(self):
        self.assertIsInstance(self.kp.groups.__repr__(), str)

        g = self.kp.find_groups(notes='blank_name')
        self.assertIsNot(g, None)
        self.assertIsInstance(g.__repr__(), str)

class RecycleBinTests3(KDBX3Tests):

    def test_recyclebincreation(self):
        self.assertIsNone(self.kp.recyclebin_group)

        entry = self.kp.add_entry( self.kp.root_group, "RecycleBinTest1", "login", "password")
        self.kp.trash_entry(entry)

        self.assertIsNotNone(self.kp.recyclebin_group)
        self.assertEqual( len(self.kp.recyclebin_group.entries), 1)

    def test_entry(self):
        entry = self.kp.add_entry( self.kp.root_group, "RecycleBinTest2", "login", "password")
        entry_uuid = entry.uuid
        self.kp.trash_entry(entry)

        entries_in_root = self.kp.find_entries(uuid=entry_uuid, group=self.kp.root_group, recursive=False )
        self.assertEqual( len(entries_in_root), 0)

        entries_in_recyclebin = self.kp.find_entries(uuid=entry_uuid, group=self.kp.recyclebin_group, recursive=False )
        self.assertEqual( len(entries_in_recyclebin), 1)

    def test_group(self):
        group = self.kp.add_group( self.kp.root_group, "RecycleBinTest3 Group")
        group_uuid = group.uuid
        entry = self.kp.add_entry( group, "RecycleBinTest3 Entry", "login", "password")
        entry_uuid = entry.uuid

        self.kp.trash_group(group)

        groups_in_root = self.kp.find_groups(uuid=group_uuid, group=self.kp.root_group, recursive=False )
        self.assertEqual( len(groups_in_root), 0)

        groups_in_recyclebin = self.kp.find_groups(uuid=group_uuid, group=self.kp.recyclebin_group, recursive=False )
        self.assertEqual( len(groups_in_recyclebin), 1)

        group_in_recyclebin = groups_in_recyclebin[0]
        self.assertEqual( len(group_in_recyclebin.entries), 1)
        self.assertEqual( group_in_recyclebin.entries[0].uuid, entry_uuid)

    def test_recyclebinemptying(self):
        entry = self.kp.add_entry( self.kp.root_group, "RecycleBinTest4 Entry", "login", "password")
        self.kp.trash_entry(entry)

        group = self.kp.add_group( self.kp.root_group, "RecycleBinTest4 Group")
        self.kp.trash_group(group)

        self.assertEqual( len(self.kp.recyclebin_group.subgroups), 1)
        self.assertEqual( len(self.kp.recyclebin_group.entries), 1)

        self.kp.empty_group(self.kp.recyclebin_group)

        self.assertEqual( len(self.kp.recyclebin_group.subgroups), 0)
        self.assertEqual( len(self.kp.recyclebin_group.entries), 0)


class EntryTests3(KDBX3Tests):

    def test_fields(self):
        expiry_time = datetime.now(timezone.utc).replace(microsecond=0)
        entry = Entry(
            'title',
            'username',
            'password',
            url='url',
            notes='notes',
            tags='tags',
            otp='otp',
            expires=True,
            expiry_time=expiry_time,
            icon=icons.KEY,
            kp=self.kp
        )

        self.assertEqual(entry.title, 'title')
        self.assertEqual(entry.username, 'username')
        self.assertEqual(entry.password, 'password')
        self.assertEqual(entry.url, 'url')
        self.assertEqual(entry.notes, 'notes')
        self.assertEqual(entry.tags, ['tags'])
        self.assertEqual(entry.otp, 'otp')
        self.assertEqual(entry.expires, True)
        self.assertEqual(entry.expiry_time, expiry_time)
        self.assertEqual(entry.icon, icons.KEY)
        self.assertEqual(entry.is_a_history_entry, False)
        self.assertEqual(
            self.kp.find_entries(title='subentry', first=True).path,
            ['foobar_group', 'subgroup', 'subentry']
        )
        self.assertEqual(
            self.kp.find_entries(title='root_entry', first=True).history[0].group,
            self.kp.root_group
        )

    def test_references(self):
        original_entry = self.kp.find_entries(title='foobar_entry', first=True)
        original_entry_duplicate = self.kp.find_entries(title='foobar_entry', first=True)
        clone1 = self.kp.find_entries(title='foobar_entry - Clone', first=True)
        clone2 = self.kp.find_entries(title='foobar_entry - Clone of clone', first=True)
        prefixed = self.kp.find_entries(title='foobar_entry - Clone with prefix and suffix', first=True)
        self.assertEqual(self.kp.deref(clone2.username), original_entry.username)
        self.assertEqual(clone2.deref('username'), original_entry.username)
        self.assertEqual(clone2.deref('password'), original_entry.password)
        self.assertEqual(original_entry.ref('username'), clone1.username)
        self.assertEqual(prefixed.deref('username'), 'domain\\{}2'.format(original_entry.username))
        self.assertEqual(prefixed.deref('password'), 'A{}BC'.format(original_entry.password))
        self.assertEqual(original_entry, original_entry_duplicate)
        self.assertEqual(hash(original_entry), hash(original_entry_duplicate))
        self.assertNotEqual(original_entry, clone1)
        self.assertNotEqual(clone1, clone2)

    def test_broken_reference(self):
        # TODO: move the entry into test databases
        broken_entry_title = 'broken reference'
        self.kp.add_entry(
            self.kp.root_group,
            title=broken_entry_title,
            username='{REF:U@I:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}',
            password='{REF:P@I:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}',
        )
        broken_entry = self.kp.find_entries(title=broken_entry_title, first=True)
        self.assertEqual(broken_entry.deref('username'), None)
        self.assertEqual(broken_entry.deref('password'), None)
        self.kp.delete_entry(broken_entry)

    def test_set_and_get_fields(self):
        time = datetime.now(timezone.utc).replace(microsecond=0)
        changed_time = time + timedelta(hours=9)
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
        entry.set_custom_property('multiline', 'hello\nworld')
        entry.otp = "otpsecret"

        self.assertEqual(entry.title, changed_string + 'title')
        self.assertEqual(entry.username, changed_string + 'username')
        self.assertEqual(entry.password, changed_string + 'password')
        self.assertEqual(entry.url, changed_string + 'url')
        self.assertEqual(entry.notes, changed_string + 'notes')
        self.assertEqual(entry.icon, icons.GLOBE)
        self.assertEqual(entry.get_custom_property('foo'), 'bar')
        self.assertEqual(entry.get_custom_property('multiline'), 'hello\nworld')
        self.assertEqual(entry.otp, 'otpsecret')
        self.assertIn('foo', entry.custom_properties)
        entry.delete_custom_property('foo')
        self.assertEqual(entry.get_custom_property('foo'), None)
        # test time properties
        self.assertEqual(entry.expires, False)
        self.assertEqual(entry.expiry_time, changed_time)

        entry.tags = 'changed_tags'
        self.assertEqual(entry.tags, ['changed_tags'])
        entry.tags = 'changed;tags'
        self.assertEqual(entry.tags, ['changed', 'tags'])
        entry.tags = ['changed', 'again', 'tags']
        self.assertEqual(entry.tags, ['changed', 'again', 'tags'])
        entry.tags = []
        self.assertEqual(entry.tags, [])

    def test_expired_datetime_offset(self):
        """Test for https://github.com/pschmitt/pykeepass/issues/115"""
        future_time = datetime.now(timezone.utc) + timedelta(days=1)
        past_time = datetime.now(timezone.utc) - timedelta(days=1)
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

    def test_touch(self):
        """Test for https://github.com/pschmitt/pykeepass/issues/120"""
        entry = self.kp.find_entries_by_title('root_entry', first=True)
        atime = entry.atime
        mtime = entry.mtime
        ctime = entry.ctime
        entry.touch()
        self.assertTrue(atime < entry.atime)
        self.assertEqual(mtime, entry.mtime)
        self.assertEqual(ctime, entry.ctime)

        entry = self.kp.find_entries_by_title('foobar_entry', first=True)
        atime = entry.atime
        mtime = entry.mtime
        ctime = entry.ctime
        entry.touch(modify=True)
        self.assertTrue(atime < entry.atime)
        self.assertTrue(mtime < entry.mtime)
        self.assertEqual(ctime, entry.ctime)

        group = self.kp.find_groups(name='foobar_group', first=True)
        atime = group.atime
        mtime = group.mtime
        ctime = group.ctime
        group.touch(modify=True)
        self.assertTrue(atime < group.atime)
        self.assertTrue(mtime < group.mtime)
        self.assertEqual(ctime, group.ctime)


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

    def test_is_custom_property_protected(self):
        e = self.kp.add_entry(self.kp.root_group, 'test-protect', 'some-user', 'pass')
        e.set_custom_property('protected', 'something', protect=True)
        e.set_custom_property('explicit-unprotected', 'other', protect=False)
        e.set_custom_property('not-protected', 'secret')
        self.assertTrue(e.is_custom_property_protected('protected'))
        self.assertFalse(e.is_custom_property_protected('explicit-unprotected'))
        self.assertFalse(e.is_custom_property_protected('not-protected'))
        self.assertFalse(e.is_custom_property_protected('non-existent'))

    def test_reindex(self):
        e1 = self.kp.add_entry(self.kp.root_group, 'Test-Index1', 'user-index', 'pass')
        e2 = self.kp.add_entry(self.kp.root_group, 'Test-Index2', 'user-index', 'pass')
        e3 = self.kp.add_entry(self.kp.root_group, 'Test-Index3', 'user-index', 'pass')
        e4 = self.kp.add_entry(self.kp.root_group, 'Test-Index4', 'user-index', 'pass')
        e2.reindex(0)
        e3.reindex(0)
        e4.reindex(0)
        entries = self.kp.find_entries(username="user-index")
        self.assertEqual(entries, [e4,e3,e2,e1])


class EntryHistoryTests3(KDBX3Tests):

    # ---------- History -----------

    def test_find_history_entries(self):
        '''run some tests on entries created by pykeepass'''
        prefix = 'TFE_'
        changed = 'tfe_changed_'

        # create some new entries to have clean start
        e1 = self.kp.add_entry(
            self.kp.root_group,
            prefix + 'title',
            prefix + 'user',
            prefix + 'pass'
        )
        g1 = self.kp.add_group(self.kp.root_group, prefix + 'group')
        e2 = self.kp.add_entry(
            g1,
            prefix + 'title',
            prefix + 'user',
            prefix + 'pass'
        )
        g2 = self.kp.add_group(g1, prefix + 'sub_group')
        e2 = self.kp.add_entry(
            g2,
            prefix + 'title',
            prefix + 'user',
            prefix + 'pass'
        )

        # no history tests
        res1 = self.kp.find_entries(title=prefix + 'title')
        self.assertEqual(len(res1), 3)
        for entry in res1:
            self.assertFalse(entry.is_a_history_entry)
            hist = entry.history
            self.assertIsInstance(hist, list)
            self.assertEqual(len(hist), 0)

        res2 = self.kp.find_entries(title=prefix + 'title', history=True)
        self.assertEqual(len(res2), 3)

        # create history
        for entry in res1:
            entry.save_history()

        # first history tests
        # we should not find any history items
        res1 = self.kp.find_entries(title=prefix + 'title')
        self.assertEqual(len(res1), 3)
        for entry in res1:
            self.assertFalse(entry.is_a_history_entry)
            hist = entry.history
            self.assertEqual(len(hist), 1)
            for item in hist:
                self.assertTrue(item.is_a_history_entry)
                self.assertEqual(item.group, entry.group)
                self.assertTrue(str(item).startswith('HistoryEntry:'))

        # here history items are expected
        res2 = self.kp.find_entries(title=prefix + 'title', history=True)
        self.assertEqual(len(res2), 6)
        for entry in res2:
            if entry not in res1:
                self.assertTrue(entry.is_a_history_entry)

        # change the active entries to test integrity of the history items
        backup = {}
        now = datetime.now(timezone.utc)
        for entry in res1:
            backup[entry.uuid] = {"atime": entry.atime, "mtime": entry.mtime, "ctime": entry.ctime}
            entry.title = changed + 'title'
            entry.username = changed + 'user'
            entry.password = changed + 'pass'
            entry.atime = now
            entry.mtime = now

        # changed entries tests
        # title of active entries has changed, so we shouldn't find anything
        res = self.kp.find_entries(title=prefix + 'title')
        self.assertEqual(len(res), 0)
        # title of history items should still be intact
        res = self.kp.find_entries(title=prefix + 'title', history=True)
        self.assertEqual(len(res), 3)

        # dito username, assuming if this works, it will also work for all other find_by cases
        res = self.kp.find_entries(username=prefix + 'user')
        self.assertEqual(len(res), 0)
        res = self.kp.find_entries(username=prefix + 'user', history=True)
        self.assertEqual(len(res), 3)

        # testing integrity of history item
        res = self.kp.find_entries(title=changed + 'title')
        for entry in res:
            for item in entry.history:
                self.assertEqual(item.title, prefix + 'title')
                self.assertEqual(item.username, prefix + 'user')
                self.assertEqual(item.password, prefix + 'pass')
                self.assertEqual(item.atime, backup[entry.uuid]["atime"])
                self.assertEqual(item.mtime, backup[entry.uuid]["mtime"])
                self.assertEqual(item.ctime, backup[entry.uuid]["ctime"])

        # create a second history item
        # back in time I had the problem that the first call to save_history() worked but not the second
        for entry in res:
            entry.save_history()

        # second history tests
        res1 = self.kp.find_entries(title=changed + 'title')
        self.assertEqual(len(res1), 3)
        for entry in res1:
            self.assertFalse(entry.is_a_history_entry)
            hist = entry.history
            self.assertEqual(len(hist), 2)
            for item in hist:
                self.assertTrue(item.is_a_history_entry)
                self.assertEqual(item.group, entry.group)

        res2 = self.kp.find_entries(title=changed + 'title', history=True)
        self.assertEqual(len(res2), 6)
        for entry in res2:
            if entry not in res1:
                self.assertTrue(entry.is_a_history_entry)

        # try deleting a history entry
        h = e1.history[0]
        self.assertIn(h, e1.history)
        e1.delete_history(h)
        self.assertNotIn(h, e1.history)

        # delete all history
        self.assertTrue(len(e1.history) > 0)
        e1.delete_history(all=True)
        self.assertTrue(len(e1.history) == 0)

class GroupTests3(KDBX3Tests):

    def test_fields(self):
        self.assertEqual(
            self.kp.find_groups(name='subgroup2', first=True).path,
            ['foobar_group', 'subgroup', 'subgroup2']
        )

    def test_empty_group(self):
        # test that groups are properly emptied
        emptytest = self.kp.add_group(self.kp.root_group, 'emptytest_group')
        self.kp.add_entry(emptytest, 'emptytest_entry', 'user', 'pass')
        self.kp.add_group(emptytest, 'emptytest_subgroup')
        self.assertEqual(len(emptytest.entries), 1)
        self.assertEqual(len(emptytest.subgroups), 1)
        self.kp.empty_group(emptytest)
        self.assertEqual(len(emptytest.entries), 0)
        self.assertEqual(len(emptytest.subgroups), 0)


class AttachmentTests3(KDBX3Tests):
    # get some things ready before testing

    def test_create_delete_binary(self):
        with self.assertRaises(BinaryError):
            self.kp_tmp.delete_binary(999)
        with self.assertRaises(BinaryError):
            e = self.kp_tmp.entries[0]
            e.add_attachment(filename='foo.txt', id=123)
            e.attachments[0].binary

        binary_id = self.kp_tmp.add_binary(b'Ronald McDonald Trump')
        self.kp_tmp.save()
        self.kp_tmp.reload()
        self.assertEqual(self.kp_tmp.binaries[binary_id], b'Ronald McDonald Trump')
        self.assertEqual(len(self.kp_tmp.attachments), 2)

        num_attach = len(self.kp_tmp.binaries)
        self.kp_tmp.delete_binary(binary_id)
        self.kp_tmp.save()
        self.kp_tmp.reload()
        self.assertEqual(len(self.kp_tmp.binaries), num_attach - 1)

        # test empty attachment - issue 314
        a = self.kp.find_attachments(filename='foo.txt', first=True)
        self.assertEqual(a._element.text, None)
        self.assertEqual(a.data, b'')

    def test_attachment_reference_decrement(self):
        e = self.kp.entries[0]

        binary_id1 = self.kp.add_binary(b'foobar')
        binary_id2 = self.kp.add_binary(b'foobar2')

        attachment1 = e.add_attachment(binary_id1, 'foo.txt')
        attachment2 = e.add_attachment(binary_id2, 'foo.txt')

        self.kp.delete_binary(binary_id1)

        self.assertEqual(attachment2.id, binary_id2 - 1)

    def test_fields(self):
        # test creation
        e = self.kp.entries[0]
        binary_id = self.kp.add_binary(b'foobar')
        a = e.add_attachment(filename='test.txt', id=binary_id)
        self.assertEqual(a.data, b'foobar')
        self.assertEqual(a.id, binary_id)
        self.assertEqual(a.filename, 'test.txt')


class PyKeePassTests3(KDBX3Tests):
    def test_consecutives_saves_with_stream(self):
        # https://github.com/libkeepass/pykeepass/pull/388
        self.setUp()

        with open(base_dir / self.keyfile_tmp, 'rb') as f:
            keyfile = BytesIO(f.read())

        for _i in range(5):
            with PyKeePass(
                base_dir / self.database_tmp,
                password=self.password,
                keyfile=keyfile,
            ) as kp:
                kp.save()

    def test_set_credentials(self):
        self.kp_tmp.password = 'f00bar'
        self.kp_tmp.keyfile = base_dir / 'change.key'
        self.kp_tmp.save()
        self.kp_tmp = PyKeePass(
            self.kp_tmp.filename,
            'f00bar',
            self.kp_tmp.keyfile
        )

        results = self.kp.find_entries_by_username('foobar_user', first=True)
        self.assertEqual('foobar_user', results.username)

    def test_dump_xml(self):
        self.kp.dump_xml('db_dump.xml')
        with open('db_dump.xml') as f:
            first_line = f.readline()
            self.assertEqual(first_line, '<?xml version=\'1.0\' encoding=\'utf-8\' standalone=\'yes\'?>\n')

    def test_credchange(self):
        """
        - test rec/req boolean (expired, no expired, days=-1)
        - test get/set days
        - test cred set timer reset
        """

        required_days = 5
        recommended_days = 5
        unexpired_date = datetime.now(timezone.utc) - timedelta(days=1)
        expired_date = datetime.now(timezone.utc) - timedelta(days=10)

        self.kp.credchange_required_days = required_days
        self.kp.credchange_recommended_days = recommended_days

        # test not expired
        self.kp.credchange_date = unexpired_date
        self.assertFalse(self.kp.credchange_required)
        self.assertFalse(self.kp.credchange_recommended)

        # test expired
        self.kp.credchange_date = expired_date
        self.assertTrue(self.kp.credchange_required)
        self.assertTrue(self.kp.credchange_recommended)

        # test expiry disabled
        self.kp.credchange_required_days = -1
        self.kp.credchange_recommended_days = -1
        self.assertFalse(self.kp.credchange_required)
        self.assertFalse(self.kp.credchange_recommended)

        # test credential update
        self.kp.credchange_required_days = required_days
        self.kp.credchange_recommended_days = recommended_days
        self.kp.credchange_date = expired_date
        self.assertTrue(self.kp.credchange_required)
        self.assertTrue(self.kp.credchange_recommended)
        self.kp.keyfile = 'foo'
        self.assertFalse(self.kp.credchange_required)
        self.assertFalse(self.kp.credchange_recommended)

class BugRegressionTests3(KDBX3Tests):
    def test_issue129(self):
        # issue 129 - protected multiline string fields lose newline
        e = self.kp.find_entries(title='foobar_entry', first=True)
        self.assertEqual(e.get_custom_property('multiline'), 'hello\nworld')

    def test_pull102(self):
        # PR 102 - entries are protected after save
        # reset self.kp_tmp
        self.setUp()
        e = self.kp_tmp.find_entries(title='foobar_entry', first=True)
        self.assertEqual(e.password, 'foobar')
        self.kp_tmp.save()
        self.assertEqual(e.password, 'foobar')

    def test_issue193(self):
        # issue 193 - kp.entries doesn't return entries with title=None
        e = self.kp.add_entry(self.kp.root_group, 'test', 'user', 'pass')
        prop = e._xpath('String/Key[text()="Title"]/..', first=True)
        e._element.remove(prop)
        self.assertTrue(e.title is None)
        self.assertTrue(e in self.kp.entries)
        # also test for kp.groups
        g = self.kp.add_group(self.kp.root_group, 'test_g')
        prop = g._xpath('Name', first=True)
        g._element.remove(prop)
        self.assertTrue(g.name is None)
        self.assertTrue(g in self.kp.groups)

    def test_issue194(self):
        # entries with Protected=True aren't being protected properly

        self.kp_tmp.add_entry(self.kp_tmp.root_group, 'protect_test', 'user', 'pass')
        self.kp_tmp.save()
        self.kp_tmp.reload()
        e = self.kp_tmp.find_entries(title='protect_test', first=True)
        self.assertEqual(e.password, 'pass')

    def test_issue223(self):
        # issue 223 - database is clobbered when kp.save() fails
        # even if exception is caught

        # test clobbering with file on disk
        # change keyfile so database save fails
        self.kp_tmp.keyfile = 'foo'
        with self.assertRaises(Exception):
            self.kp_tmp.save()
        # try to open database
        self.kp_tmp.keyfile = self.keyfile_tmp
        PyKeePass(self.database_tmp, self.password, self.keyfile_tmp)
        # reset test database
        self.setUp()

        # test clobbering with buffer
        stream = BytesIO()
        self.kp_tmp.save(stream)
        stream.seek(0)

        # change keyfile so database save fails
        self.kp_tmp.keyfile = 'foo'
        self.kp_tmp.password = ('invalid', 'type')
        with self.assertRaises(Exception):
            self.kp_tmp.save(stream)
        stream.seek(0)
        # try to open database
        self.kp_tmp.keyfile = self.keyfile_tmp
        PyKeePass(stream, self.password, self.keyfile_tmp)

    def test_issue308(self):
        # find_entries/find_groups() break when supplied None values directly

        results = self.kp.find_entries(title='foobar_entry')
        results2 = self.kp.find_entries(title='foobar_entry', username=None)

        self.assertEqual(results, results2)

    def test_issue344(self):
        # accessing expiry_time throws exception when None

        e = self.kp_tmp.find_entries(title='none_date', first=True)
        e._element.xpath('Times/ExpiryTime')[0].text = None
        self.assertEqual(e.expiry_time, None)

    def test_issue376(self):
        # Setting the properties of an entry should not change the Protected
        # property
        subgroup = self.kp.root_group
        e = self.kp.add_entry(subgroup, 'banana_entry', 'user', 'pass')

        self.assertEqual(e._is_property_protected('Password'), True)
        self.assertEqual(e._is_property_protected('Title'), False)
        self.assertEqual(e.otp, None)
        self.assertEqual(e._is_property_protected('otp'), False)

        e.title = 'pineapple'
        e.password = 'pizza'
        e.otp = 'aa'

        self.assertEqual(e._is_property_protected('Password'), True)
        self.assertEqual(e._is_property_protected('Title'), False)
        self.assertEqual(e._is_property_protected('otp'), True)

        # Using protected=None should not change the current status
        e._set_string_field('XYZ', '1', protected=None)
        self.assertEqual(e._is_property_protected('XYZ'), False)

        e._set_string_field('XYZ', '1', protected=True)
        self.assertEqual(e._is_property_protected('XYZ'), True)

        e._set_string_field('XYZ', '1', protected=None)
        self.assertEqual(e._is_property_protected('XYZ'), True)

        e._set_string_field('XYZ', '1', protected=False)
        self.assertEqual(e._is_property_protected('XYZ'), False)

class EntryFindTests4(KDBX4Tests, EntryFindTests3):
    pass

class GroupFindTests4(KDBX4Tests, GroupFindTests3):
    pass

class RecycleBinTests4(KDBX4Tests, RecycleBinTests3):
    pass

class EntryTests4(KDBX4Tests, EntryTests3):
    pass

class GroupTests3(KDBX4Tests, GroupTests3):
    pass

class AttachmentTests4(KDBX4Tests, AttachmentTests3):
    pass

class PyKeePassTests4(KDBX4Tests, PyKeePassTests3):
    pass

class BugRegressionTests4(KDBX4Tests, BugRegressionTests3):
    pass


class CtxManagerTests(unittest.TestCase):
    def test_ctx_manager(self):
        with PyKeePass(base_dir / 'test4.kdbx', password='password', keyfile=base_dir / 'test4.key') as kp:
            results = kp.find_entries_by_username('foobar_user', first=True)
            self.assertEqual('foobar_user', results.username)

class PyKeePassTests3(KDBX3Tests):
    """Tests on PyKeePass class that don't involve attachments or finding entries/groups"""

    def test_database_info(self):
        """Test database properties"""

        # Test name
        self.assertEqual(self.kp_tmp.database_name, None)
        self.kp_tmp.database_name = "Test Name"
        self.assertEqual(self.kp_tmp.database_name, "Test Name")

        # Test Description
        self.assertEqual(self.kp_tmp.database_description, None)
        self.kp_tmp.database_description = "Test Description"
        self.assertEqual(self.kp_tmp.database_description, "Test Description")

        # Test Default User Name
        self.assertEqual(self.kp_tmp.default_username, None)
        self.kp_tmp.default_username = "Test User"
        self.assertEqual(self.kp_tmp.default_username, "Test User")

        self.kp_tmp.save()
        self.kp_tmp.reload()

        self.assertEqual(self.kp_tmp.database_name, "Test Name")
        self.assertEqual(self.kp_tmp.database_description, "Test Description")
        self.assertEqual(self.kp_tmp.default_username, "Test User")

class PyKeePassTests4(KDBX4Tests, PyKeePassTests3):
    pass

class KDBXTests(unittest.TestCase):
    """Tests on KDBX parsing"""

    def test_open_save(self):
        """try to open all databases, save them, then open the result"""

        # for database stream open test
        with open(base_dir / 'test3.kdbx', 'rb') as file:
            stream = BytesIO(file.read())
        # for keyfile file descriptor test
        keyfile_fd = open(base_dir / 'test4.key', 'rb')

        filenames_in = [
            base_dir / 'test3.kdbx',                 # KDBX v3
            base_dir / 'test4_aes.kdbx',             # KDBX v4 AES
            base_dir / 'test4_aeskdf.kdbx',          # KDBX v3 AESKDF
            base_dir / 'test4_chacha20.kdbx',        # KDBX v4 ChaCha
            base_dir / 'test4_twofish.kdbx',         # KDBX v4 Twofish
            base_dir / 'test4_hex.kdbx',             # legacy 64 byte hexadecimal keyfile
            base_dir / 'test3_transformed.kdbx',     # KDBX v3 transformed_key open
            base_dir / 'test4_transformed.kdbx',     # KDBX v4 transformed_key open
            stream,                                               # test stream opening
            base_dir / 'test4_aes_uncompressed.kdbx',# KDBX v4 AES uncompressed
            base_dir / 'test4_twofish_uncompressed.kdbx',# KDBX v4 Twofish uncompressed
            base_dir / 'test4_chacha20_uncompressed.kdbx',# KDBX v4 ChaCha uncompressed
            base_dir / 'test4_argon2id.kdbx',        # KDBX v4 Argon2id
            base_dir / 'test4.kdbx',        # KDBX v4 with keyfile file descriptor
        ]
        filenames_out = [
            base_dir / 'test3.kdbx.out',
            base_dir / 'test4_aes.kdbx.out',
            base_dir / 'test4_aeskdf.kdbx.out',
            base_dir / 'test4_chacha20.kdbx.out',
            base_dir / 'test4_twofish.kdbx.out',
            base_dir / 'test4_hex.kdbx.out',
            base_dir / 'test3_transformed.kdbx.out',
            base_dir / 'test4_transformed.kdbx.out',
            BytesIO(),
            base_dir / 'test4_aes_uncompressed.kdbx.out',
            base_dir / 'test4_twofish_uncompressed.kdbx.out',# KDBX v4 Twofish uncompressed
            base_dir / 'test4_chacha20_uncompressed.kdbx.out',# KDBX v4 ChaCha uncompressed
            base_dir / 'test4_argon2id.kdbx.out',
            base_dir / 'test4.kdbx.out',        # KDBX v4 with keyfile file descriptor
        ]
        passwords = [
            'password',
            'password',
            'password',
            'password',
            'password',
            'password',
            None,
            None,
            'password',
            'password',
            'password',
            'password',
            'password',
            'password',
        ]
        transformed_keys = [
            None,
            None,
            None,
            None,
            None,
            None,
            b'\xfb\xb1!\x0e0\x94\xd4\x868\xa5\x04\xe6T\x9b<\xf9+\xb8\x82EN\xbc\xbe\xbc\xc8\xd3\xbbf\xfb\xde\xff.',
            b'\x95\x0be\x9ca\x9e<\xe0\x07\x02\x7f\xc3\xd8\xa1\xa6&\x985\x8f!\xa6\x18k\x13\xa2\xd2\r=\xf3\xebd\xc5',
            None,
            None,
            None,
            None,
            None,
            None,
 ]
        keyfiles = [
            base_dir / 'test3.key',
            base_dir / 'test4.key',
            base_dir / 'test4.key',
            base_dir / 'test4.key',
            base_dir / 'test4.key',
            base_dir / 'test4_hex.key',
            None,
            None,
            base_dir / 'test3.key',
            None,
            None,
            None,
            None,
            keyfile_fd
        ]
        encryption_algorithms = [
            'aes256',
            'aes256',
            'aes256',
            'chacha20',
            'twofish',
            'chacha20',
            'aes256',
            'chacha20',
            'aes256',
            'aes256',
            'twofish',
            'chacha20',
            'aes256',
            'chacha20',
        ]
        kdf_algorithms = [
            'aeskdf',
            'argon2',
            'aeskdf',
            'argon2',
            'argon2',
            'argon2',
            'aeskdf',
            'argon2',
            'aeskdf',
            'argon2',
            'argon2',
            'argon2',
            'argon2id',
            'argon2',
        ]
        versions = [
            (3, 1),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (3, 1),
            (4, 0),
            (3, 1),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
        ]

        for (filename_in, filename_out, password, transformed_key,
             keyfile, encryption_algorithm, kdf_algorithm, version) in zip(
                 filenames_in, filenames_out, passwords, transformed_keys,
                 keyfiles, encryption_algorithms, kdf_algorithms, versions
        ):
            kp = PyKeePass(
                filename_in,
                password,
                keyfile,
                transformed_key=transformed_key
            )
            self.assertEqual(kp.encryption_algorithm, encryption_algorithm)
            self.assertEqual(kp.kdf_algorithm, kdf_algorithm)
            self.assertEqual(kp.version, version)

            kp.save(
                filename_out,
                transformed_key=transformed_key
            )

            if hasattr(filename_out, "seek"):
                # rewind so PyKeePass can read from the same stream
                filename_out.seek(0)

            kp = PyKeePass(
                filename_out,
                password,
                keyfile,
                transformed_key=transformed_key
            )

        for filename in base_dir.glob('*.out'):
            os.remove(filename)

        keyfile_fd.close()


    def test_open_error(self):

        databases = [
            'test3.kdbx',
            'test3.kdbx',
            'test4.kdbx',
            'test4.kdbx',
            'test4.kdbx',
            'test4.kdbx',
            'test3.key',
        ]
        passwords = [
            'invalid',
            'password',
            'invalid',
            'password',
            'password',
            'password',
            'password',
        ]
        keyfiles = [
            'test3.key',
            'test4.key',
            'test4.key',
            'test_invalidversion.key',
            'test.svg',
            'test3.key',
        ]
        errors = [
            CredentialsError,
            CredentialsError,
            CredentialsError,
            CredentialsError,
            CredentialsError,
            CredentialsError,
            HeaderChecksumError,
        ]
        for database, password, keyfile, error in zip(databases, passwords, keyfiles, errors):
            with self.assertRaises(error):
                PyKeePass(
                    base_dir / database,
                    password,
                    base_dir / keyfile
                )


    def test_open_no_decrypt(self):
        """Open database but do not decrypt payload.  Needed for reading header data for OTP tokens"""


        databases = [
            'test3.kdbx',
            'test4.kdbx',
        ]
        passwords = [
            'invalid_password',
            'invalid_password',
        ]
        enc_algs = [
            'aes256',
            'chacha20'
        ]
        versions = [
            (3, 1),
            (4, 0),
        ]
        for database, password, enc_alg, version in zip(databases, passwords, enc_algs, versions):
            kp = PyKeePass(
                os.path.join(base_dir, database),
                password,
                decrypt=False
            )

            self.assertEqual(kp.encryption_algorithm, enc_alg)
            self.assertEqual(kp.version, version)

if __name__ == '__main__':
    unittest.main()

