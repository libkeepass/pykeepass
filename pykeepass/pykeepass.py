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
from lxml.builder import E
import zlib
from construct import Container

from pykeepass.entry import Entry
from pykeepass.xpath import entry_xp, group_xp, attachment_xp, path_xp
from pykeepass.group import Group
from pykeepass.attachment import Attachment
from pykeepass.exceptions import *

logger = logging.getLogger(__name__)

class PyKeePass(object):

    def __init__(self, filename, password=None, keyfile=None,
                 transformed_key=None):
        self.filename = filename

        self.read(
            password=password,
            keyfile=keyfile,
            transformed_key=transformed_key
        )

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        del self.kdbx

    def read(self, filename=None, password=None, keyfile=None,
             transformed_key=None):
        self.password = password
        self.keyfile = keyfile
        if not filename:
            filename = self.filename

        self.kdbx = KDBX.parse_file(
            filename,
            password=password,
            keyfile=keyfile,
            transformed_key=transformed_key
        )


    def save(self, filename=None, transformed_key=None):
        if not filename:
            filename = self.filename

        with open(filename, 'wb') as f:
            f.write(
                KDBX.build(
                    self.kdbx,
                    password=self.password,
                    keyfile=self.keyfile,
                    transformed_key=transformed_key
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
    def transformed_key(self):
        return self.kdbx.body.transformed_key

    @property
    def tree(self):
        return self.kdbx.body.payload.xml

    @property
    def root_group(self):
        return self.find_groups(path='', first=True)

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
                res.append(Entry(element=r, kp=self))
            elif r.tag == 'Group':
                res.append(Group(element=r, kp=self))
            elif r.tag == 'Binary' and r.getparent().tag == 'Entry':
                res.append(Attachment(element=r, kp=self))
            else:
                res.append(r)
        return res


    def _find(self, prefix, keys_xp, path=None, tree=None, history=False, first=False,
              regex=False, flags=None, **kwargs):

        xp = ''

        # resolve path before handling any keys
        if path is not None:

            xp += '/KeePassFile/Root/Group'
            # split provided path into group and entry
            group_path = os.path.dirname(path).lstrip('/')
            entry = os.path.basename(path)
            # build xpath from group_path and entry
            if group_path:
                for group in group_path.split('/'):
                    xp += path_xp[regex]['group'].format(group, flags=flags)
            if entry:
                xp += path_xp[regex]['entry'].format(entry, flags=flags)

        elif tree is not None:
            xp += '.'
            
        # FIXME: ideally, this should be 'if kwargs.keys() or path is not None'
        #        but this is a breaking change. Pending issue 127
        if kwargs.keys():
            xp += prefix

        # handle searching custom string fields
        if 'string' in kwargs.keys():
            for key, value in kwargs['string'].items():
                xp += keys_xp[regex]['string'].format(key, value, flags=flags)

            kwargs.pop('string')

        # build xpath to filter results with specified attributes
        for key, value in kwargs.items():
            if key not in keys_xp[regex].keys():
                raise TypeError('Invalid keyword argument "{}"'.format(key))

            xp += keys_xp[regex][key].format(value, flags=flags)

        res = self._xpath(xp, tree=tree._element if tree else None)

        return res

    #---------- Groups ----------

    def find_groups(self, first=False, recursive=True, path=None, group=None,
                    **kwargs):

        prefix = '//Group' if recursive else '/Group'
        res = self._find(prefix, group_xp, path=path, tree=group, **kwargs)

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
    def add_group(self, destination_group, group_name, icon=None, notes=None):
        logger.debug('Creating group {}'.format(group_name))

        if icon:
            group = Group(name=group_name, icon=icon, notes=notes, kp=self)
        else:
            group = Group(name=group_name, notes=notes, kp=self)
        destination_group.append(group)

        return group

    def delete_group(self, group):
        group.delete()

    def move_group(self, group, destination_group):
        destination_group.append(group)

    #---------- Entries ----------

    def find_entries(self, history=False, first=False, recursive=True,
                     path=None, group=None, **kwargs):

        prefix = '//Entry' if recursive else '/Entry'
        res = self._find(prefix, entry_xp, path=path, tree=group, **kwargs)

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
                  tags=None, icon=None, force_creation=False):

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
                kp=self
            )
            destination_group.append(entry)

        return entry

    def delete_entry(self, entry):
        entry.delete()

    def move_entry(self, entry, destination_group):
        destination_group.append(entry)

    #---------- Attachments ----------

    def find_attachments(self, history=False, first=False, recursive=True,
                         path=None, element=None, **kwargs):

        prefix = '//Binary' if recursive else '/Binary'
        res = self._find(prefix, attachment_xp, path=path, tree=element, **kwargs)

        if history is False:
            res = [item for item in res if item._element.getparent().getparent().tag != 'History']
        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    @property
    def attachments(self):
        self.find_attachments(filename='.*', regex=True)

    @property
    def binaries(self):
        if self.version >= (4, 0):
            # first byte is a prepended flag
            attachments = [a.data[1:] for a in self.kdbx.body.payload.inner_header.binary]
        else:
            attachments = []
            for elem in self._xpath('/KeePassFile/Meta/Binaries/Binary'):
                if elem.attrib['Compressed'] == 'True':
                    data = zlib.decompress(
                        base64.b64decode(elem.text),
                        zlib.MAX_WBITS | 32
                    )
                else:
                    data = base64.b64decode(elem.text)
                attachments.append(data)

        return attachments

    def add_binary(self, data, compressed=True, protected=True):
        if self.version >= (4, 0):
            # add protected flag byte
            if protected:
                data = b'\x01' + data
            else:
                data = b'\x00' + data
            # add binary element to inner header
            c = Container(type='binary', data=data)
            self.kdbx.body.payload.inner_header.binary.append(c)
        else:
            binaries = self._xpath('/KeePassFile/Meta/Binaries')[0]
            if compressed:
                # gzip compression
                data = zlib.compress(data)
            data = base64.b64encode(data).decode

            # add binary element to XML
            binaries.append(
                E.Binary(data, Compressed=str(compressed))
            )

        # return attachment id
        return len(self.binaries)

    def delete_binary(self, id):
        try:
            if self.version >= (4, 0):
                # remove binary element from inner header
                self.kdbx.body.payload.inner_header.binary.pop(id)
            else:
                # remove binary element from XML
                binaries = self._xpath('/KeePassFile/Meta/Binaries')[0]
                binaries.remove(binaries.getchildren()[id])
        except IndexError:
            raise AttachmentError('No such attachment with id {}'.format(id))

        # remove all entry references to this attachment
        for reference in self.find_attachments(id=id):
            reference.delete()

        # decrement references greater than this id
        for reference in self._xpath('//Binary/Value[@Ref > "{}"]/..'.format(id)):
            reference.id = reference.id - 1
