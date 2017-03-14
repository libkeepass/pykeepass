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
        return libkeepass.open(
            filename, password=password, keyfile=keyfile
        ).__enter__()

    def save(self, filename=None):
        # FIXME The *second* save operations creates gibberish passwords
        if not filename:
            filename = self.kdb_filename
        outfile = open(filename, 'w+').__enter__()
        self.kdb.write_to(outfile)
        return outfile

    @property
    def root_group(self):
        return self.find_groups_by_path('', tree=None, first=True)

    @property
    def groups(self):
        return self.find_groups_by_name('.*', regex=True)

    @property
    def entries(self):
        return self.find_entries_by_title('.*', regex=True)

    def dump_xml(self, outfile):
        '''
        Dump the content of the database to a file
        NOTE The file is unencrypted!
        '''
        with open(outfile, 'w+') as f:
            f.write(self.kdb.pretty_print())

    def __xpath(self, xpath_str, tree=None):
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
        return res

    #---------- Groups ----------

    def find_groups_by_name(self, group_name, tree=None, regex=False, first=False):
        if regex:
            xp = './/Group/Name[re:test(text(), "{}")]/..'.format(group_name)
        else:
            xp = './/Group/Name[text()="{}"]/..'.format(group_name)

        res = self.__xpath(xp, tree=tree)

        if first:
            res = res[0] if res else None

        return res

    def find_groups_by_path(self, group_path_str=None, regex=False, tree=None, first=False):
        logger.info('Looking for group {}'.format(group_path_str if group_path_str else 'Root'))
        xp = '/KeePassFile/Root/Group'

        # remove leading /
        group_path_str = group_path_str.lstrip('/')

        # if group_path_str is not set, assume we look for root dir
        if group_path_str:
            for s in group_path_str.split('/'):
                if regex:
                    xp += '/Group/Name[re:test(text(), "{}")]/..'.format(s)
                else:
                    xp += '/Group/Name[text()="{}"]/..'.format(s)
        res = self.__xpath(xp, tree=tree)
        
        if first:
            res = res[0] if res else None

        return res

    # creates a new group and all parent groups, if necessary
    def add_group(self, group_path):
        logger.info('Creating group {}'.format(group_path))

        path = ''
        for group_name in group_path.split('/'):
            group = self.find_groups_by_path(path + '/' + group_name, first=True)

            if not group:
                parent_group = self.find_groups_by_path(path, first=True)
                group = Group(name=group_name)
                parent_group.append(group)

            path += '/' + group_name

    #---------- Entries ----------

    def __find_entry_by(self, key, value, regex=False, tree=None, history=False, first=False):
        if regex:
            xp = './/Entry/String/Key[text()="{}"]/../Value[re:test(text(), "{}")]/../..'.format(
                key, value
            )
        else:
            xp = './/Entry/String/Key[text()="{}"]/../Value[text()="{}"]/../..'.format(
                key, value
            )
        res = self.__xpath(tree=tree, xpath_str=xp)
        if history == False:
            res = [item for item in res if not item.is_a_history_entry]

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    def find_entries_by_title(self, title, regex=False, tree=None, history=False, first=False):
        return self.__find_entry_by(
            key='Title',
            value=title,
            regex=regex,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_username(self, username, regex=False, tree=None, history=False, first=False):
        return self.__find_entry_by(
            key='UserName',
            value=username,
            regex=regex,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_password(self, password, regex=False, tree=None, history=False, first=False):
        return self.__find_entry_by(
            key='Password',
            value=password,
            regex=regex,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_url(self, url, regex=False, tree=None, history=False, first=False):
        return self.__find_entry_by(
            key='URL',
            value=url,
            regex=regex,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_notes(self, notes, regex=False, tree=None, history=False, first=False):
        return self.__find_entry_by(
            key='Notes',
            value=notes,
            regex=regex,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_path(self, path, regex=False, tree=None, history=False, first=False):
        entry_title = os.path.basename(path)
        group_path = os.path.dirname(path)
        group = self.find_groups_by_path(group_path, tree=tree, regex=regex, first=True)
        if group is not None:
            if regex:
                res = [x for x in group.entries if re.match(entry_title, x.title)]
            else:
                res = [x for x in group.entries if x.title == entry_title]

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    def add_entry(self, group_path, title, username,
                  password, url=None, notes=None,
                  tags=None, icon=None, force_creation=False,
                  regex=False):
        if isinstance(group_path, Group):
            destination_group = group_path
        else:
            destination_group = self.find_groups_by_path(group_path, regex=regex, first=True)
        if not destination_group:
            logging.info(
                'Could not find destination group {}. Create it.'.format(
                    group_path
                )
            )
            destination_group = self.add_group(group_path)
        entries = self.find_entries_by_title(
            tree=destination_group._element,
            title=title,
            regex=regex
        )
        if entries and not force_creation:
            logger.warning(
                'An entry "{}" already exists in "{}". Update it.'.format(
                    title, group_path
                )
            )
            entry = entries[0]
            entry.save_history()
            entry.title = title
            entry.username = username
            entry.password = password
            entry.url = url
            if notes:
                entry.notes = notes
            if url:
                entry.url = url
            if icon:
                entry.icon = icon
            if tags:
                entry.tags = tags
            # Update mtime
            entry.touch(modify=True)
        else:
            logger.info('Create a new entry')
            entry = Entry(
                title=title,
                username=username,
                password=password,
                notes=notes,
                url=url,
                tags=tags,
                icon=icon
            )
            destination_group.append(entry)

        return entry
