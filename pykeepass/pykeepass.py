#!/usr/bin/env python
# coding: utf-8

# FIXME python2
from __future__ import absolute_import, print_function, unicode_literals
from future.utils import python_2_unicode_compatible

import base64
import logging
import os
import re
import uuid
import zlib
from copy import deepcopy

from construct import Container, ChecksumError
from lxml import etree
from lxml.builder import E

from pykeepass.attachment import Attachment
from pykeepass.entry import Entry
from pykeepass.exceptions import *
from pykeepass.group import Group
from pykeepass.kdbx_parsing.kdbx import KDBX
from pykeepass.kdbx_parsing.kdbx4 import kdf_uuids
from pykeepass.xpath import attachment_xp, entry_xp, group_xp, path_xp

logging.basicConfig()
logger = logging.getLogger(__name__)


BLANK_DATABASE_FILENAME = "blank_database.kdbx"
BLANK_DATABASE_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), BLANK_DATABASE_FILENAME)
BLANK_DATABASE_PASSWORD = "password"


# FIXME python2
@python_2_unicode_compatible
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
        # see issue 137
        pass

    def read(self, filename=None, password=None, keyfile=None,
             transformed_key=None):
        self.password = password
        self.keyfile = keyfile
        if not filename:
            filename = self.filename

        try:
            self.kdbx = KDBX.parse_file(
                filename,
                password=password,
                keyfile=keyfile,
                transformed_key=transformed_key
            )
        except ChecksumError:
            raise CredentialsIntegrityError

    def save(self, filename=None, transformed_key=None):
        if not filename:
            filename = self.filename

        KDBX.build_file(
            self.kdbx,
            filename,
            password=self.password,
            keyfile=self.keyfile,
            transformed_key=transformed_key
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

    def xml(self):
        return etree.tostring(
            self.tree,
            pretty_print=True,
            standalone=True,
            encoding='unicode'
        )

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

    def _xpath(self, xpath_str, tree=None, first=False, history=False,
               cast=False, **kwargs):

        if tree is None:
            tree = self.tree
        logger.debug(xpath_str)
        elements = tree.xpath(
            xpath_str, namespaces={'re': 'http://exslt.org/regular-expressions'}
        )

        res = []
        for e in elements:
            if history or e.getparent().tag != 'History':
                if cast:
                    if e.tag == 'Entry':
                        res.append(Entry(element=e, kp=self))
                    elif e.tag == 'Group':
                        res.append(Group(element=e, kp=self))
                    elif e.tag == 'Binary' and e.getparent().tag == 'Entry':
                        res.append(Attachment(element=e, kp=self))
                    else:
                        raise Exception('Could not cast element {}'.format(e))
                else:
                    res.append(e)

        # return first object in list or None
        if first:
            res = res[0] if res else None

        return res

    def _find(self, prefix, keys_xp, path=None, tree=None, first=False,
              history=False, regex=False, flags=None, **kwargs):

        xp = ''

        if path is not None:

            first = True

            xp += '/KeePassFile/Root/Group'
            path = path.strip('/')
            # split provided path into group and element
            group_path = os.path.dirname(path)
            element = os.path.basename(path)
            # build xpath from group_path and element
            if group_path:
                for group in group_path.split('/'):
                    xp += path_xp[regex]['group'].format(group, flags=flags)
            if 'Entry' in prefix:
                xp += path_xp[regex]['entry'].format(element, flags=flags)
            elif element and 'Group' in prefix:
                xp += path_xp[regex]['group'].format(element, flags=flags)

        else:
            if tree is not None:
                xp += '.'

            if kwargs.keys():
                xp += prefix

            # handle searching custom string fields
            if 'string' in kwargs.keys():
                for key, value in kwargs['string'].items():
                    xp += keys_xp[regex]['string'].format(key, value, flags=flags)

                kwargs.pop('string')

            # convert uuid to base64 form before building xpath
            if 'uuid' in kwargs.keys():
                kwargs['uuid'] = base64.b64encode(kwargs['uuid'].bytes).decode('utf-8')

            # convert tags to semicolon separated string before building xpath
            if 'tags' in kwargs.keys():
                kwargs['tags'] = ';'.join(kwargs['tags'])

            # build xpath to filter results with specified attributes
            for key, value in kwargs.items():
                if key not in keys_xp[regex].keys():
                    raise TypeError('Invalid keyword argument "{}"'.format(key))

                xp += keys_xp[regex][key].format(value, flags=flags)

        res = self._xpath(
            xp,
            tree=tree._element if tree else None,
            first=first,
            history=history,
            cast=True,
            **kwargs
        )

        return res

    # ---------- Groups ----------

    def find_groups(self, recursive=True, path=None, group=None, **kwargs):

        prefix = '//Group' if recursive else '/Group'
        res = self._find(prefix, group_xp, path=path, tree=group, **kwargs)
        return res

    def find_groups_by_name(self, group_name, regex=False, flags=None,
                            group=None, first=False):
        return self.find_groups(
            name=group_name,
            regex=regex,
            flags=flags,
            group=group,
            first=first
        )

    def find_groups_by_path(self, group_path_str=None, regex=False, flags=None,
                            group=None, first=False):
        return self.find_groups(
            path=group_path_str,
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

    def deref(self, value):
        if not value:
            return value
        references = set(re.findall(r'({REF:([TUPANI])@([TUPANI]):([^}]+)})', value))
        if not references:
            return value
        field_to_attribute = {
            'T': 'title',
            'U': 'username',
            'P': 'password',
            'A': 'url',
            'N': 'notes',
            'I': 'uuid',
        }
        for ref, wanted_field, search_in, search_value in references:
            wanted_field = field_to_attribute[wanted_field]
            search_in = field_to_attribute[search_in]
            if search_in == 'uuid':
                search_value = uuid.UUID(search_value)
            ref_entry = self.find_entries(first=True, **{search_in: search_value})
            value = value.replace(ref, getattr(ref_entry, wanted_field))
        return self.deref(value)

    def move_group(self, group, destination_group):
        destination_group.append(group)

    # ---------- Entries ----------

    def find_entries(self, recursive=True, path=None, group=None, **kwargs):

        prefix = '//Entry' if recursive else '/Entry'
        res = self._find(prefix, entry_xp, path=path, tree=group, **kwargs)

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

    # ---------- Attachments ----------

    def find_attachments(self, recursive=True, path=None, element=None, **kwargs):

        prefix = '//Binary' if recursive else '/Binary'
        res = self._find(prefix, attachment_xp, path=path, tree=element, **kwargs)

        return res

    @property
    def attachments(self):
        return self.find_attachments(filename='.*', regex=True)

    @property
    def binaries(self):
        if self.version >= (4, 0):
            # first byte is a prepended flag
            binaries = [a.data[1:] for a in self.kdbx.body.payload.inner_header.binary]
        else:
            binaries = []
            for elem in self._xpath('/KeePassFile/Meta/Binaries/Binary'):
                if elem.get('Compressed') == 'True':
                    data = zlib.decompress(
                        base64.b64decode(elem.text),
                        zlib.MAX_WBITS | 32
                    )
                else:
                    data = base64.b64decode(elem.text)
                binaries.insert(int(elem.attrib['ID']), data)

        return binaries

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
            binaries = self._xpath(
                '/KeePassFile/Meta/Binaries',
                first=True
            )
            if compressed:
                # gzip compression
                compressor = zlib.compressobj(
                    zlib.Z_DEFAULT_COMPRESSION,
                    zlib.DEFLATED,
                    zlib.MAX_WBITS | 16
                )
                data = compressor.compress(data)
                data += compressor.flush()
            data = base64.b64encode(data).decode()

            # set ID for Binary Element
            binary_id = len(self.binaries)

            # add binary element to XML
            binaries.append(
                E.Binary(data, ID=str(binary_id), Compressed=str(compressed))
            )

        # return binary id
        return len(self.binaries) - 1

    def delete_binary(self, id):
        try:
            if self.version >= (4, 0):
                # remove binary element from inner header
                self.kdbx.body.payload.inner_header.binary.pop(id)
            else:
                # remove binary element from XML
                binaries = self._xpath('/KeePassFile/Meta/Binaries', first=True)
                binaries.remove(binaries.getchildren()[id])
        except IndexError:
            raise BinaryError('No such binary with id {}'.format(id))

        # remove all entry references to this attachment
        for reference in self.find_attachments(id=id):
            reference.delete()

        # decrement references greater than this id
        binaries_gt = self._xpath(
            '//Binary/Value[@Ref > "{}"]/..'.format(id),
            cast=True
        )
        for reference in binaries_gt:
            reference.id = reference.id - 1


def create_database(filename, password=None, keyfile=None, transformed_key=None):
    keepass_instance = PyKeePass(BLANK_DATABASE_LOCATION, BLANK_DATABASE_PASSWORD)

    keepass_instance.filename = filename
    keepass_instance.password = password
    keepass_instance.keyfile = keyfile

    keepass_instance.save(transformed_key)

    return keepass_instance
