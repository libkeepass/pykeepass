#!/usr/bin/env python
# coding: utf-8


from __future__ import print_function
from __future__ import unicode_literals
from entry import Entry
from group import Group
import libkeepass
import logging
import os
import re


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PyKeePass():

    def __init__(self, filename, password=None, keyfile=None):
        self.kdb_filename = filename
        self.kdb = self.read(filename, password, keyfile)

    def read(self, filename=None, password=None, keyfile=None):
        if not filename:
            filename = self.kdb_filename
        assert filename, 'Filename should not be empty'
        logger.info('Open file {}'.format(filename))
        self.kdb = libkeepass.open(
            filename, password=password, keyfile=keyfile
        ).__enter__()
        return self.kdb

    def save(self, filename=None):
        if not filename:
            filename = self.kdb_filename
        outfile = open(filename, 'w+').__enter__()
        self.kdb.write_to(outfile)
        return outfile

    @property
    def root_group(self):
        return self.get_root_group()

    @property
    def groups(self):
        return self.__xpath('.//Group', first_match_only=False)

    @property
    def entries(self):
        res = self.__xpath('.//Entry', first_match_only=False)
        return [x for x in res if not x.is_a_history_entry]

    def dump_xml(self, outfile):
        '''
        Dump the content of the database to a file
        NOTE The file is unencrypted!
        '''
        with open(outfile, 'w+') as f:
            f.write(self.kdb.pretty_print())

    def __xpath(self, xpath_str, first_match_only=True, tree=None):
        if tree is None:
            tree = self.kdb.tree
        result = tree.xpath(
            xpath_str, namespaces={'re': 'http://exslt.org/regular-expressions'}
        )
        # Typed result array
        res = []
        for r in result:
            if r.tag == 'Entry':
                res.append(Entry(element=r))
            elif r.tag == 'Group':
                res.append(Group(element=r))
            else:
                res.append(r)
        if len(res) > 0:
            return res[0] if first_match_only else res

    def find_groups_by_path(self, group_path_str=None, regex=False, tree=None):
        logger.info('Look for group {}'.format(group_path_str if group_path_str else 'ROOT'))
        if not tree:
            tree = self.kdb.tree
        xp = '/KeePassFile/Root/Group'
        # if group_path_str is not set, assume we look for root dir
        if group_path_str:
            for s in group_path_str.split('/'):
                if regex:
                    xp += '/Group/Name[re:test(text(), "{}")]/..'.format(s)
                else:
                    xp += '/Group/Name[text()="{}"]/..'.format(s)
        return self.__xpath(xp, first_match_only=False, tree=tree)

    def find_group_by_path(self, group_path_str, regex=False, tree=None):
        res = self.find_groups_by_path(
            group_path_str=group_path_str,
            regex=regex,
            tree=tree
        )
        if res is not None and len(res) > 0:
            return res[0]

    def get_root_group(self, tree=None):
        return self.find_group_by_path()

    def find_groups_by_name(self, group_name, tree=None, regex=False):
        if regex:
            xp = './/Group/Name[re:test(text(), "{}")]/..'.format(group_name)
        else:
            xp = './/Group/Name[text()="{}"]/..'.format(group_name)
        return self.__xpath(xp, tree=tree, first_match_only=False)

    def find_group_by_name(self, group_name, tree=None):
        gname = os.path.dirname(group_name) if '/' in group_name else group_name
        res = self.find_groups_by_name(gname)
        if len(res) > 0:
            return res[0]

    def create_group_path(self, group_path, tree=None):
        if not tree:
            tree = self.kdb.tree
        logger.info('Create group {}'.format(group_path))
        group = self.get_root_group(tree)
        path = ''
        for gn in group_path.split('/'):
            group = self.__create_group_at_path(tree, path.rstrip('/'), gn)
            path += gn + '/'
        return group

    def __create_group_at_path(self, tree, group_path, group_name):
        logger.info(
            'Create group {} at {}'.format(
                group_name,
                group_path if group_path else 'root dir'
            )
        )
        parent_group = self.find_group_by_path(group_path, tree)
        if parent_group:
            group = Group(element=group_name)
            parent_group.append(group)
            return group
        else:
            logger.error('Could not find group at {}'.format(group_path))

    def __find_entry_by(self, key, value, regex=False, first_match_only=False, tree=None):
        if regex:
            xp = './/Entry/String/Key[text()="{}"]/../Value[re:test(text(), "{}")]/../..'.format(
                key, value
            )
        else:
            xp = './/Entry/String/Key[text()="{}"]/../Value[text()="{}"]/../..'.format(
                key, value
            )
        return self.__xpath(tree=tree, xpath_str=xp, first_match_only=first_match_only)

    def find_entry_by_title(self, title, regex=False, tree=None):
        return self.__find_entry_by(
            key='Title',
            value=title,
            regex=regex,
            first_match_only=True,
            tree=tree
        )

    def find_entries_by_title(self, title, regex=False, tree=None):
        return self.__find_entry_by(
            key='Title',
            value=title,
            regex=regex,
            first_match_only=False,
            tree=tree
        )

    def find_entries_by_username(self, username, regex=False, tree=None):
        return self.__find_entry_by(
            key='UserName',
            value=username,
            regex=regex,
            first_match_only=False,
            tree=tree
        )

    def find_entry_by_username(self, username, regex=False, tree=None):
        return self.__find_entry_by(
            key='UserName',
            value=username,
            regex=regex,
            first_match_only=True,
            tree=tree
        )

    def find_entry_by_password(self, password, regex=False, tree=None):
        return self.__find_entry_by(
            key='Password',
            value=password,
            regex=regex,
            first_match_only=True,
            tree=tree
        )

    def find_entries_by_password(self, password, regex=False, tree=None):
        return self.__find_entry_by(
            key='Password',
            value=password,
            regex=regex,
            first_match_only=False,
            tree=tree
        )

    def find_entries_by_url(self, url, regex=False, tree=None):
        return self.__find_entry_by(
            key='URL',
            value=url,
            regex=regex,
            first_match_only=False,
            tree=tree
        )

    def find_entry_by_url(self, url, regex=False, tree=None):
        return self.__find_entry_by(
            key='URL',
            value=url,
            regex=regex,
            first_match_only=True,
            tree=tree
        )

    def find_entries_by_notes(self, notes, regex=False, tree=None):
        return self.__find_entry_by(
            key='Notes',
            value=notes,
            regex=regex,
            first_match_only=False,
            tree=tree
        )

    def find_entry_by_notes(self, notes, regex=False, tree=None):
        return self.__find_entry_by(
            key='Notes',
            value=notes,
            regex=regex,
            first_match_only=True,
            tree=tree
        )

    def find_entry_by_path(self, path, regex=False, tree=None):
        res = self.find_entries_by_path(path=path, regex=regex, tree=tree)
        if len(res) > 0:
            return res[0]

    def find_entries_by_path(self, path, regex=False, tree=None):
        entry_title = os.path.basename(path)
        group_path = os.path.dirname(path)
        group = self.find_group_by_path(group_path, tree=tree, regex=regex)
        if group is not None:
            if regex:
                return [x for x in group.entries if re.match(entry_title, x.title)]
            else:
                return [x for x in group.entries if x.title == entry_title]

    def add_entry(self, group_path, entry_title, entry_username,
                  entry_password, entry_url=None, entry_notes=None,
                  entry_tags=None, entry_icon=None, force_creation=False,
                  regex=False):
        destination_group = self.find_group_by_path(group_path, regex=regex)
        if not destination_group:
            logging.info(
                'Could not find destination group {}. Create it.'.format(
                    group_path
                )
            )
            destination_group = self.create_group_path(group_path)
        e = self.find_entry_by_title(
            tree=destination_group._element,
            title=entry_title,
            regex=regex
        )
        if e and not force_creation:
            logger.warning(
                'An entry "{}" already exists in "{}". Update it.'.format(
                    entry_title, group_path
                )
            )
            e.save_history()
            e.title = entry_title
            e.username = entry_username
            e.password = entry_password
            e.url = entry_url
            if entry_notes:
                e.notes = entry_notes
            if entry_url:
                e.url = entry_url
            if entry_icon:
                e.icon = entry_icon
            if entry_tags:
                e.tags = entry_tags
            # Update mtime
            e.touch(modify=True)
        else:
            logger.info('Create a new entry')
            e = Entry(
                title=entry_title,
                username=entry_username,
                password=entry_password,
                notes=entry_notes,
                url=entry_url,
                tags=entry_tags,
                icon=entry_icon
            )
            destination_group.append(e)
