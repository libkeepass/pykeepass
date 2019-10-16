# -*- coding: utf-8 -*-

# FIXME python2
from __future__ import unicode_literals

import logging
import os
import shutil
import unittest
import uuid
from datetime import datetime, timedelta

from dateutil import tz
from lxml.etree import Element

from pykeepass import PyKeePass, icons
from pykeepass.entry import Entry
from pykeepass.exceptions import BinaryError
from pykeepass.group import Group
from pykeepass.kdbx_parsing import KDBX

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


class KDBX3Tests(unittest.TestCase):
    database = 'test3.kdbx'
    password = 'password'
    keyfile = 'test3.key'

    # get some things ready before testing
    def setUp(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, self.database),
            password=self.password,
            keyfile=os.path.join(base_dir, self.keyfile)
        )


class KDBX4Tests(KDBX3Tests):
    database = 'test4.kdbx'
    password = 'password'
    keyfile = 'test4.key'


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
        results = self.kp.find_entries(path='foobar_group/group_entry')
        self.assertIsInstance(results, Entry)
        results = self.kp.find_entries(path='foobar_group/')
        self.assertEqual(results, None)
        results = self.kp.find_entries(path='foobar_group/Group_entry', regex=True, flags='i', first=True)
        self.assertIsInstance(results, Entry)
        self.assertEqual('group_entry', results.title)

    def test_find_entries_by_uuid(self):
        uu = uuid.UUID('cc5f7ecd-2a00-48ca-9621-c222a347b0bb')
        results = self.kp.find_entries_by_uuid(uu)[0]
        self.assertIsInstance(results, Entry)
        self.assertEqual(uu, results.uuid)
        self.assertEqual('foobar_user', results.username)

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

    def test_history_path(self):
        for title in ["root_entry", "subentry"]:
            entry = self.kp.find_entries(title=title, first=True)
            hist = entry.history
            self.assertTrue(len(hist) > 0)
            for item in hist:
                self.assertEqual(item.path, '[History of: {}]'.format(entry.title))

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
        results = self.kp.find_entries(path='sub_group/test_add_entry_title', first=True)
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

    # ---------- Entries name collision exception -----------

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
        results = self.kp.find_groups_by_path('/foobar_group/subgroup/')
        self.assertIsInstance(results, Group)
        results = self.kp.find_groups(path='/foobar_group/subgroup/', first=True)
        self.assertEqual(results.name, 'subgroup')
        results = self.kp.find_groups(path='foobar_group/group_entry')
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

        self.assertEqual(len(results), 6)

    # ---------- Adding/Deleting Groups -----------

    def test_add_delete_move_group(self):
        notes_text = "this is a note for a group!"
        base_group = self.kp.add_group(self.kp.root_group, 'base_group', notes=notes_text)
        sub_group = self.kp.add_group(base_group, 'sub_group')
        sub_group2 = self.kp.add_group(base_group, 'sub_group2')

        self.assertEqual(base_group.notes, notes_text)
        base_group.notes = ''
        self.assertEqual(base_group.notes, '')

        results = self.kp.find_groups(path='base_group/sub_group/', first=True)
        self.assertIsInstance(results, Group)
        self.assertEqual(results.name, sub_group.name)
        self.assertTrue(results.uuid != None)

        self.kp.move_group(sub_group2, sub_group)
        results = self.kp.find_groups(path='base_group/sub_group/sub_group2/', first=True)
        self.assertEqual(results.name, sub_group2.name)

        self.kp.delete_group(sub_group)
        results = self.kp.find_groups(path='base_group/sub_group/', first=True)
        self.assertIsNone(results)

        # ---------- Groups representation -----------

    def test_print_groups(self):
        self.assertIsInstance(self.kp.groups.__repr__(), str)


class EntryTests3(KDBX3Tests):

    def test_fields(self):
        time = datetime.now().replace(microsecond=0)
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

    def test_references(self):
        original_entry = self.kp.find_entries(title='foobar_entry', first=True)
        clone1 = self.kp.find_entries(title='foobar_entry - Clone', first=True)
        clone2 = self.kp.find_entries(title='foobar_entry - Clone of clone', first=True)
        prefixed = self.kp.find_entries(title='foobar_entry - Clone with prefix and suffix', first=True)
        self.assertEqual(self.kp.deref(clone2.username), original_entry.username)
        self.assertEqual(clone2.deref('username'), original_entry.username)
        self.assertEqual(clone2.deref('password'), original_entry.password)
        self.assertEqual(original_entry.ref('username'), clone1.username)
        self.assertEqual(prefixed.deref('username'), 'domain\\{}2'.format(original_entry.username))
        self.assertEqual(prefixed.deref('password'), 'A{}BC'.format(original_entry.password))

    def test_set_and_get_fields(self):
        time = datetime.now().replace(microsecond=0)
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
                self.assertEqual(item.path, '[History of: {}]'.format(entry.title))

        # here history items are expected
        res2 = self.kp.find_entries(title=prefix + 'title', history=True)
        self.assertEqual(len(res2), 6)
        for entry in res2:
            if entry not in res1:
                self.assertTrue(entry.is_a_history_entry)

        # change the active entries to test integrity of the history items
        backup = {}
        now = datetime.now()
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
                self.assertEqual(item.path, '[History of: {}]'.format(entry.title))

        res2 = self.kp.find_entries(title=changed + 'title', history=True)
        self.assertEqual(len(res2), 6)
        for entry in res2:
            if entry not in res1:
                self.assertTrue(entry.is_a_history_entry)


class GroupTests3(KDBX3Tests):

    def test_fields(self):
        self.assertEqual(self.kp.find_groups(name='subgroup2', first=True).path, 'foobar_group/subgroup/subgroup2/')


class AttachmentTests3(KDBX3Tests):
    # get some things ready before testing
    def setUp(self):
        shutil.copy(
            os.path.join(base_dir, self.database),
            os.path.join(base_dir, 'test_attachment.kdbx')
        )
        self.open()

    def open(self):
        self.kp = PyKeePass(
            os.path.join(base_dir, 'test_attachment.kdbx'),
            password=self.password,
            keyfile=os.path.join(base_dir, self.keyfile)
        )

    def test_create_delete_binary(self):
        with self.assertRaises(BinaryError):
            self.kp.delete_binary(999)
        with self.assertRaises(BinaryError):
            e = self.kp.entries[0]
            e.add_attachment(filename='foo.txt', id=123)
            e.attachments[0].binary

        binary_id = self.kp.add_binary(b'Ronald McDonald Trump')
        self.kp.save()
        self.open()
        self.assertEqual(self.kp.binaries[binary_id], b'Ronald McDonald Trump')
        self.assertEqual(len(self.kp.attachments), 1)

        num_attach = len(self.kp.binaries)
        self.kp.delete_binary(binary_id)
        self.kp.save()
        self.open()
        self.assertEqual(len(self.kp.binaries), num_attach - 1)

    def test_attachment_reference_decrement(self):
        e = self.kp.entries[0]

        binary_id1 = self.kp.add_binary(b'foobar')
        binary_id2 = self.kp.add_binary(b'foobar2')

        attachment1 = e.add_attachment(binary_id1, 'foo.txt')
        attachment2 = e.add_attachment(binary_id2, 'foo.txt')

        self.kp.delete_binary(binary_id1)

        self.assertEqual(attachment2.id, binary_id2 - 1)

    def test_fields(self):
        e = self.kp.entries[0]
        binary_id = self.kp.add_binary(b'foobar')
        a = e.add_attachment(filename='test.txt', id=binary_id)
        self.assertEqual(a.data, b'foobar')
        self.assertEqual(a.id, binary_id)
        self.assertEqual(a.filename, 'test.txt')

    def tearDown(self):
        os.remove(os.path.join(base_dir, 'test_attachment.kdbx'))


class PyKeePassTests3(KDBX3Tests):
    def setUp(self):
        shutil.copy(
            os.path.join(base_dir, self.database),
            os.path.join(base_dir, 'change_creds.kdbx')
        )
        self.kp = PyKeePass(
            os.path.join(base_dir, self.database),
            password=self.password,
            keyfile=os.path.join(base_dir, self.keyfile)
        )
        self.kp_tmp = PyKeePass(
            os.path.join(base_dir, 'change_creds.kdbx'),
            password=self.password,
            keyfile=os.path.join(base_dir, self.keyfile)
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

    def tearDown(self):
        os.remove(os.path.join(base_dir, 'change_creds.kdbx'))


class EntryFindTests4(KDBX4Tests, EntryFindTests3):
    pass


class GroupFindTests4(KDBX4Tests, GroupFindTests3):
    pass


class EntryTests4(KDBX4Tests, EntryTests3):
    pass


class GroupTests3(KDBX4Tests, GroupTests3):
    pass


class AttachmentTests4(KDBX4Tests, AttachmentTests3):
    pass


class PyKeePassTests4(KDBX4Tests, PyKeePassTests3):
    pass


class CtxManagerTests(unittest.TestCase):
    def test_ctx_manager(self):
        with PyKeePass(os.path.join(base_dir, 'test4.kdbx'), password='password', keyfile=base_dir + '/test4.key') as kp:
            results = kp.find_entries_by_username('foobar_user', first=True)
            self.assertEqual('foobar_user', results.username)


class KDBXTests(unittest.TestCase):

    def test_open_save(self):
        """try to open all databases, save them, then open the result"""

        databases = [
            'test3.kdbx',           # KDBX v3 test
            'test4.kdbx',           # KDBX v4 test
            'test4_aes.kdbx',       # KDBX v4 AES test
            'test4_aeskdf.kdbx',    # KDBX v3 AESKDF test
            'test4_chacha20.kdbx',  # KDBX v4 ChaCha test
            'test4_twofish.kdbx',   # KDBX v4 Twofish test
            'test4_hex.kdbx',       # legacy 64 byte hexadecimal keyfile test
            'test4_hex.kdbx',       # KDBX v4 transformed_key open test
        ]
        passwords = [
            'password',
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
            None,
            b'M\xb7\x08\xf6\xa7\xd1v\xb1{&\x06\x8f\xae\xe9\r\xeb\x9a\x1b\x02b\xce\xf2\x8aR\xaea)7\x1fs\xe9\xc0'
        ]
        keyfiles = [
            'test3.key',
            'test4.key',
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
            'aeskdf',
            'argon2',
            'argon2',
            'argon2',
            'argon2',
        ]
        versions = [
            (3, 1),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
            (4, 0),
        ]

        for (database, password, transformed_key,
             keyfile, encryption_algorithm, kdf_algorithm, version) in zip(
                 databases, passwords, transformed_keys,
                 keyfiles, encryption_algorithms, kdf_algorithms, versions
        ):

            kp = PyKeePass(
                os.path.join(base_dir, database),
                password,
                None if keyfile is None else os.path.join(base_dir, keyfile),
                transformed_key=transformed_key
            )
            self.assertEqual(kp.encryption_algorithm, encryption_algorithm)
            self.assertEqual(kp.kdf_algorithm, kdf_algorithm)
            self.assertEqual(kp.version, version)

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

