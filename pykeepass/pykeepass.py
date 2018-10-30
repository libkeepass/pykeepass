#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
import base64
import logging
import os
import re
from uuid import UUID
from io import BytesIO
from pykeepass.kdbx_parsing.kdbx import KDBX
from pykeepass.kdbx_parsing.kdbx4 import kdf_uuids
from lxml import etree

from pykeepass.entry import Entry
from pykeepass.group import Group

logger = logging.getLogger(__name__)


class PyKeePass(object):

    def __init__(self, filename, password=None, keyfile=None):
        self.filename = filename

        self.read(password=password, keyfile=keyfile)

    def read(self, filename=None, password=None, keyfile=None):
        self.password = password
        self.keyfile = keyfile
        if not filename:
            filename = self.filename

        self.kdbx = KDBX.parse_file(
            filename,
            password=password,
            keyfile=keyfile
        )


    def save(self, filename=None):
        if not filename:
            filename = self.filename

        with open(filename, 'wb') as f:
            f.write(
                KDBX.build(
                    self.kdbx,
                    password=self.password,
                    keyfile=self.keyfile
                )
            )

    @property
    def version(self):
        return (
            self.kdbx.header.value.major_version,
            self.kdbx.header.value.minor_version
        )

    @property
    def encryption_algorithm(self):
        return self.kdbx.header.value.dynamic_header.cipher_id.data

    @property
    def kdf_algorithm(self):
        if self.version == (3, 1):
            return 'aeskdf'
        elif self.version == (4, 0):
            kdf_parameters = self.kdbx.header.value.dynamic_header.kdf_parameters.data.dict
            if kdf_parameters['$UUID'].value == kdf_uuids['argon2']:
                return 'argon2'
            elif kdf_parameters['$UUID'].value == kdf_uuids['aeskdf']:
                return 'aeskdf'

    @property
    def tree(self):
        return self.kdbx.body.payload.xml

    @property
    def root_group(self):
        return self.find_groups_by_path('', group=None, first=True)

    @property
    def groups(self):
        return self.find_groups_by_name('.*', regex=True)

    @property
    def entries(self):
        return self.find_entries_by_title('.*', regex=True)

    @property
    def meta(self):
        return self.tree.find('Meta')

    def dump_xml(self, outfile):
        '''
        Dump the content of the database to a file
        NOTE The file is unencrypted!
        '''
        with open(outfile, 'wb') as f:
            f.write(
                etree.tostring(
                    self.tree,
                    pretty_print=True,
                    standalone=True,
                    encoding='utf-8'
                )
            )

    def _xpath(self, xpath_str, tree=None):
        if tree is None:
            tree = self.tree
        logger.debug(xpath_str)
        result = tree.xpath(
            xpath_str, namespaces={'re': 'http://exslt.org/regular-expressions'}
        )
        # Typed result array
        res = []
        for r in result:
            if r.tag == 'Entry':
                res.append(Entry(element=r, version=self.version, meta=self.meta))
            elif r.tag == 'Group':
                res.append(Group(element=r, version=self.version, meta=self.meta))
            else:
                res.append(r)
        return res


    def _find(self, keys_xp, regex=False, flags=None, group=None,
              history=False, first=False, **kwargs):

        regex_string = '[re:test(text(), "{}", "{}")]'
        match_string = '[text()="{}"]'

        group_xp = '/Group/Name{}/..'
        entry_xp = '/Entry/String/Key[text()="Title"]/../Value{}/../..'

        xp = ''

        # resolve path before handling any other keys
        if 'path' in kwargs.keys():
            xp += '/KeePassFile/Root/Group'
            # split provided path into group and entry
            group_path = os.path.dirname(kwargs['path']).lstrip('/')
            entry = os.path.basename(kwargs['path'])
            # build xpath from group_path and entry
            if group_path:
                for element in group_path.split('/'):
                    if regex:
                        xp += group_xp.format(regex_string).format(element, flags)
                    else:
                        xp += group_xp.format(match_string).format(element)
            if entry:
                if regex:
                    xp += (entry_xp.format(regex_string)).format(entry, flags)
                else:
                    xp += (entry_xp.format(match_string)).format(entry)

            kwargs.pop('path')
        elif group is not None:
            xp += '.'

        if kwargs.keys():
            xp += keys_xp['prefix']

            # handle searching custom string fields
            if 'string' in kwargs.keys():
                for key, value in kwargs['string'].items():
                    if regex:
                        xp += (keys_xp['string'].format(key, regex_string)).format(value, flags)
                    else:
                        xp += (keys_xp['string'].format(key, match_string)).format(value, flags)

                kwargs.pop('string')

            # build xpath to filter results with specified attributes
            for key, value in kwargs.items():
                if key not in keys_xp.keys():
                    raise TypeError('Invalid keyword argument "{}"'.format(key))

                if regex:
                    xp += (keys_xp[key].format(regex_string)).format(value, flags)
                else:
                    xp += (keys_xp[key].format(match_string)).format(value, flags)

        res = self._xpath(xp, tree=group._element if group else None)

        return res

    #---------- Groups ----------

    def find_groups(self, first=False, recursive=True, **kwargs):

        keys_xp = {
            'prefix': '//Group' if recursive else '/Group',
            'name': '/Name{}/..',
            'uuid': '/UUID{}/..',
            'notes': '/Notes{}/..',
        }

        res = self._find(keys_xp, **kwargs)
        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res


    def find_groups_by_path(self, group_path_str=None, regex=False, flags=None,
                            group=None, first=False):

        return self.find_groups(name=group_name,
                                regex=regex,
                                flags=flags,
                                group=group,
                                first=first
        )


    def find_groups_by_name(self, group_name, regex=False, flags=None,
                            group=None, first=False):

        return self.find_groups(name=group_name,
                                regex=regex,
                                flags=flags,
                                group=group,
                                first=first
        )


    def find_groups_by_path(self, group_path_str=None, regex=False, flags=None,
                            group=None, first=False):

        return self.find_groups(path=group_path_str,
                                regex=regex,
                                flags=flags,
                                group=group,
                                first=first
        )

    def find_groups_by_uuid(self, uuid, regex=False, flags=None,
                              group=None, history=False, first=False):

        return self.find_groups(
            uuid=uuid,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )

    def find_groups_by_notes(self, notes, regex=False, flags=None,
                              group=None, history=False, first=False):

        return self.find_groups(
            notes=notes,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )

    # creates a new group and all parent groups, if necessary
    def add_group(self, destination_group, group_name, icon=None, customicon=None, notes=None):
        logger.debug('Creating group {}'.format(group_name))

        if customicon:
            group = Group(name=group_name, customicon=customicon, notes=notes, version=self.version, meta=self.meta)
        elif icon:
            group = Group(name=group_name, icon=icon, notes=notes, version=self.version)
        else:
            group = Group(name=group_name, notes=notes, version=self.version)
        destination_group.append(group)

        return group

    def delete_group(self, group):
        group.delete()

    def move_group(self, group, destination_group):
        destination_group.append(group)

    #---------- Entries ----------

    def find_entries(self, history=False, first=False, recursive=True, **kwargs):

        keys_xp = {
            'prefix': '//Entry' if recursive else '/Entry',
            'title': '/String/Key[text()="Title"]/../Value{}/../..',
            'username': '/String/Key[text()="UserName"]/../Value{}/../..',
            'password': '/String/Key[text()="Password"]/../Value{}/../..',
            'url': '/String/Key[text()="URL"]/../Value{}/../..',
            'notes': '/String/Key[text()="Notes"]/../Value{}/../..',
            'uuid': '/UUID{}/..',
            'string': '/String/Key[text()="{}"]/../Value{}/../..',
        }


        res = self._find(keys_xp, **kwargs)

        if history is False:
            res = [item for item in res if item._element.getparent().tag != 'History']

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res


    def find_entries_by_title(self, title, regex=False, flags=None,
                              group=None, history=False, first=False):
        return self.find_entries(
            title=title,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )

    def find_entries_by_username(self, username, regex=False, flags=None,
                                 group=None, history=False, first=False):
        return self.find_entries(
            username=username,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )

    def find_entries_by_password(self, password, regex=False, flags=None,
                                 group=None, history=False, first=False):
        return self.find_entries(
            password=password,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def find_entries_by_url(self, url, regex=False, flags=None,
                            group=None, history=False, first=False):
        return self.find_entries(
            url=url,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def find_entries_by_notes(self, notes, regex=False, flags=None,
                              group=None, history=False, first=False):
        return self.find_entries(
            notes=notes,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def find_entries_by_path(self, path, regex=False, flags=None,
                             group=None, history=False, first=False):
        return self.find_entries(
            path=path,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def find_entries_by_uuid(self, uuid, regex=False, flags=None,
                              group=None, history=False, first=False):
        return self.find_entries(
            uuid=uuid,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def find_entries_by_string(self, string, regex=False, flags=None,
                              group=None, history=False, first=False):
        return self.find_entries(
            string=string,
            regex=regex,
            flags=flags,
            group=group,
            history=history,
            first=first
        )


    def add_entry(self, destination_group, title, username,
                  password, url=None, notes=None, expiry_time=None,
                  tags=None, icon=None, customicon=None, force_creation=False):

        entries = self.find_entries(
            title=title,
            username=username,
            first=True,
            group=destination_group,
            recursive=False
        )

        if entries and not force_creation:
            raise Exception(
                'An entry "{}" already exists in "{}"'.format(
                    title, destination_group
                )
            )
        else:
            logger.debug('Creating a new entry')
            entry = Entry(
                title=title,
                username=username,
                password=password,
                notes=notes,
                url=url,
                tags=tags,
                expires=True if expiry_time else False,
                expiry_time=expiry_time,
                icon=icon,
                customicon=customicon,
                version=self.version,
                meta=self.meta
            )
            destination_group.append(entry)

        return entry


    def delete_entry(self, entry):
        entry.delete()

    def move_entry(self, entry, destination_group):
        destination_group.append(entry)
