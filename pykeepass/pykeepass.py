#!/usr/bin/env python
# coding: utf-8


from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
import base64
import libkeepass
import logging
import os
import re
from uuid import UUID

from pykeepass.entry import Entry
from pykeepass.group import Group

logger = logging.getLogger(__name__)


class PyKeePass(object):

    def __init__(self, filename, password=None, keyfile=None):
        self.kdb_filename = filename
        self.kdb = self.read(filename, password, keyfile)

    def read(self, filename=None, password=None, keyfile=None):
        if not filename:
            filename = self.kdb_filename
        credentials = {}
        if password:
            credentials['password'] = password
        if keyfile:
            credentials['keyfile'] = keyfile
        assert filename, 'Filename should not be empty'
        logger.info('Open file {}'.format(filename))
        return libkeepass.open(
            filename, **credentials
        ).__enter__()

    def save(self, filename=None):
        # FIXME The *second* save operations creates gibberish passwords
        # FIXME the save operation should be moved to libkeepass at some point
        #       we shouldn't need to open another fd here just to write
        if not filename:
            filename = self.kdb_filename
        with open(filename, 'wb+') as outfile:
            self.kdb.write_to(outfile)

    # clear and set the database credentials
    def set_credentials(self, password=None, keyfile=None):
        if password or keyfile:
            credentials = {}
            if password:
                credentials['password'] = password
            if keyfile:
                credentials['keyfile'] = keyfile
            self.kdb.clear_credentials()
            self.kdb.add_credentials(**credentials)
        else:
            logger.error("You must specify a password or keyfile")

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

    def _xpath(self, xpath_str, tree=None):
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

    def find_groups_by_name(self, group_name, regex=False, flags=None,
                            tree=None, first=False):
        if regex:
            xp = './/Group/Name[re:match(text(), "{}", "{}")]/..'.format(group_name, flags)
        else:
            xp = './/Group/Name[text()="{}"]/..'.format(group_name)

        res = self._xpath(xp, tree=tree)

        if first:
            res = res[0] if res else None

        return res

    def find_groups_by_path(self, group_path_str=None, regex=False, flags=None,
                            tree=None, first=False):
        logger.info('Looking for group {}'.format(
            group_path_str if group_path_str else 'Root'))
        xp = '/KeePassFile/Root/Group'

        # remove leading and trailing /
        group_path_str = group_path_str.lstrip('/').rstrip('/')

        # if group_path_str is not set, assume we look for root dir
        if group_path_str:
            for s in group_path_str.split('/'):
                if regex:
                    xp += '/Group/Name[re:match(text(), "{}", "{}")]/..'.format(s, flags)
                else:
                    xp += '/Group/Name[text()="{}"]/..'.format(s)
        res = self._xpath(xp, tree=tree)

        if first:
            res = res[0] if res else None

        return res

    # creates a new group and all parent groups, if necessary
    def add_group(self, destination_group, group_name, icon=None):
        logger.info('Creating group {}'.format(group_name))

        if icon:
            group = Group(name=group_name, icon=icon)
        else:
            group = Group(name=group_name)
        destination_group.append(group)

        return group

    def delete_group(self, group):
        group.delete()

    #---------- Entries ----------

    def _find_entry_by(self, key, value, regex=False, flags=None,
                       tree=None, history=False, first=False):
        if regex:
            xp = './/Entry/String/Key[text()="{}"]/../Value[re:match(text(), "{}", "{}")]/../..'.format(
                key, value, flags
            )
        else:
            xp = './/Entry/String/Key[text()="{}"]/../Value[text()="{}"]/../..'.format(
                key, value
            )
        res = self._xpath(tree=tree, xpath_str=xp)
        if history is False:
            res = [item for item in res if not item.is_a_history_entry]

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    def _find_exact_entry(self, title, username, tree=None, history=False):
        xp = ('.//Entry/String/Key[text()="Title"]/../Value[text()="{}"]'
              '/../../String/Key[text()="UserName"]/../Value[text()="{}"]/../..').format(
            title, username)
        res = self._xpath(tree=tree, xpath_str=xp)
        if history is False:
            res = [item for item in res if not item.is_a_history_entry]

        return res

    def find_entries_by_title(self, title, regex=False, flags=None,
                              tree=None, history=False, first=False):
        return self._find_entry_by(
            key='Title',
            value=title,
            regex=regex,
            flags=flags,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_username(self, username, regex=False, flags=None,
                                 tree=None, history=False, first=False):
        return self._find_entry_by(
            key='UserName',
            value=username,
            regex=regex,
            flags=flags,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_password(self, password, regex=False, flags=None,
                                 tree=None, history=False, first=False):
        return self._find_entry_by(
            key='Password',
            value=password,
            regex=regex,
            flags=flags,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_url(self, url, regex=False, flags=None,
                            tree=None, history=False, first=False):
        return self._find_entry_by(
            key='URL',
            value=url,
            regex=regex,
            flags=flags,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_notes(self, notes, regex=False, flags=None,
                              tree=None, history=False, first=False):
        return self._find_entry_by(
            key='Notes',
            value=notes,
            regex=regex,
            flags=flags,
            tree=tree,
            history=history,
            first=first
        )

    def find_entries_by_path(self, path, regex=False, flags=None,
                             tree=None, history=False, first=False):
        ##FIXME we should adapt this function to use _xpath instead of using
        #  find_group_by_path and then iterating with ugly regex code
        entry_title = os.path.basename(path)
        group_path = os.path.dirname(path)
        group = self.find_groups_by_path(group_path,
                                         tree=tree,
                                         regex=regex,
                                         flags=flags,
                                         first=True)

        if group is not None:
            if regex:
                res = [x for x in group.entries
                       if re.match(('(?{})'.format(flags) if flags else None) + entry_title,
                                   x.title)]
            else:
                res = [x for x in group.entries if x.title == entry_title]
        else:
            return

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    def find_entry_by_uuid(self, uuid, tree=None, history=False):

        uuid_base64 = base64.b64encode(UUID(uuid).bytes).decode()

        xp = './/Entry/UUID[text()="{}"]/..'.format(uuid_base64)

        res = self._xpath(tree=tree, xpath_str=xp)

        if history is False:
            res = res[0]

        return res

    def add_entry(self, destination_group, title, username,
                  password, url=None, notes=None, expiry_time=None,
                  tags=None, icon=None, force_creation=False):

        entries = self._find_exact_entry(
            title=title,
            username=username,
            tree=destination_group._element,
        )

        if entries and not force_creation:
            raise Exception(
                'An entry "{}" already exists in "{}"'.format(
                    title, destination_group
                )
            )
        else:
            logger.info('Creating a new entry')
            entry = Entry(
                title=title,
                username=username,
                password=password,
                notes=notes,
                url=url,
                tags=tags,
                expires=True if expiry_time else False,
                expiry_time=expiry_time,
                icon=icon
            )
            destination_group.append(entry)

        return entry

    def delete_entry(self, entry):
        entry.delete()
