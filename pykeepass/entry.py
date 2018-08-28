from __future__ import unicode_literals
from __future__ import absolute_import
from pykeepass.baseelement import BaseElement
from copy import deepcopy
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement
from lxml.builder import E
import logging
import pykeepass.group
from datetime import datetime

logger = logging.getLogger(__name__)
reserved_keys = [
    'Title',
    'UserName',
    'Password',
    'URL',
    'Tags',
    'IconID',
    'Times',
    'History'
]


class Entry(BaseElement):

    def __init__(self, title=None, username=None, password=None, url=None,
                 notes=None, tags=None, expires=False, expiry_time=None,
                 icon=None, element=None, version=None):

        assert type(version) is tuple, 'The provided version is not a tuple, but a {}'.format(
            type(version)
        )
        self._version = version

        if element is None:
            super(Entry, self).__init__(
                element=Element('Entry'),
                version=version,
                expires=expires,
                expiry_time=expiry_time,
                icon=icon
            )
            self._element.append(E.String(E.Key('Title'), E.Value(title)))
            self._element.append(E.String(E.Key('UserName'), E.Value(username)))
            self._element.append(
                E.String(E.Key('Password'), E.Value(password, protected="False"))
            )
            if url:
                self._element.append(E.String(E.Key('URL'), E.Value(url)))
            if notes:
                self._element.append(E.String(E.Key('Notes'), E.Value(notes)))
            if tags:
                self._element.append(
                    E.Tags(';'.join(tags) if type(tags) is list else tags)
                )

        else:
            assert type(element) in [_Element, Element, ObjectifiedElement], \
                'The provided element is not an LXML Element, but a {}'.format(
                    type(element)
                )
            assert element.tag == 'Entry', 'The provided element is not an Entry '\
                'element, but a {}'.format(element.tag)
            self._element = element

    def _get_string_field(self, key):
        results = self._element.xpath('String/Key[text()="{}"]/../Value'.format(key))
        if results:
            return results[0].text

    def _set_string_field(self, key, value):
        results = self._element.xpath('String/Key[text()="{}"]/..'.format(key))
        if results:
            logger.debug('There is field named {}. Remove it and create again.'.format(key))
            self._element.remove(results[0])
        else:
            logger.debug('No field named {}. Create it.'.format(key))
        self._element.append(E.String(E.Key(key), E.Value(value)))

    def _get_string_field_keys(self, exclude_reserved=False):
        results = [x.find('Key').text for x in self._element.findall('String')]
        if exclude_reserved:
            return [x for x in results if x not in reserved_keys]
        else:
            return results

    @property
    def title(self):
        return self._get_string_field('Title')

    @title.setter
    def title(self, value):
        return self._set_string_field('Title', value)

    @property
    def username(self):
        return self._get_string_field('UserName')

    @username.setter
    def username(self, value):
        return self._set_string_field('UserName', value)

    @property
    def password(self):
        return self._get_string_field('Password')

    @password.setter
    def password(self, value):
        return self._set_string_field('Password', value)

    @property
    def url(self):
        return self._get_string_field('URL')

    @url.setter
    def url(self, value):
        return self._set_string_field('URL', value)

    @property
    def notes(self):
        return self._get_string_field('Notes')

    @notes.setter
    def notes(self, value):
        return self._set_string_field('Notes', value)

    @property
    def icon(self):
        return self._get_subelement_text('IconID')

    @icon.setter
    def icon(self, value):
        return self._set_subelement_text('IconID', value)

    @property
    def tags(self):
        val =  self._get_subelement_text('Tags')
        return val.split(';') if val else val

    @tags.setter
    def tags(self, value):
        # Accept both str or list
        v = ';'.join(value if type(value) is list else [value])
        return self._set_subelement_text('Tags', v)

    @property
    def history(self):
        if self._element.find('History') is not None:
            return [Entry(element=x, version=self._version) for x in self._element.find('History').findall('Entry')]

    @history.setter
    def history(self, value):
        raise NotImplementedError()

    @property
    def is_a_history_entry(self):
        parent = self._element.getparent()
        if parent is not None:
            return parent.tag == 'History'
        return False

    @property
    def parentgroup(self):
        if self.is_a_history_entry:
            ancestor = self._element.getparent().getparent()
        else:
            ancestor = self._element.getparent()
        if ancestor is not None:
            return pykeepass.group.Group(element=ancestor, version=self._version)

    @property
    def path(self):
        # The root group is an orphan
        if self.is_a_history_entry:
            pentry = Entry(
                element=self._element.getparent().getparent(),
                version=self._version
            ).title
            return '[History of: {}]'.format(pentry)
        if self.parentgroup is None:
            return None
        p = self.parentgroup
        ppath = ''
        while p is not None and not p.is_root_group:
            if p.name is not None: # dont make the root group appear
                ppath = '{}/{}'.format(p.name, ppath)
            p = p.parentgroup
        return '{}{}'.format(ppath, self.title)

    def set_custom_property(self, key, value):
        assert key not in reserved_keys, '{} is a reserved key'.format(key)
        return self._set_string_field(key, value)

    def get_custom_property(self, key):
        assert key not in reserved_keys, '{} is a reserved key'.format(key)
        return self._get_string_field(key)

    def delete_custom_property(self, key):
        if key not in self._get_string_field_keys(exclude_reserved=True):
            raise AttributeError('No such key: {}'.format(key))
        prop = self._element.xpath('String/Key[text()="{}"]/..'.format(key))
        if len(prop) < 1:
            raise AttributeError('Could not find property element')
        self._element.remove(prop[0])

    @property
    def custom_properties(self):
        keys = self._get_string_field_keys(exclude_reserved=True)
        props = {}
        for k in keys:
            props[k] = self._get_string_field(k)
        return props

    def touch(self, modify=False):
        '''
        Update last access time of an entry
        '''
        self._element.Times.LastAccessTime = datetime.utcnow()
        if modify:
            self._element.Times.LastModificationTime = datetime.utcnow()

    def save_history(self):
        '''
        Save the entry in its history
        '''
        archive = deepcopy(self._element)
        if self._element.find('History') is not None:
            archive.remove(archive.History)
            self._element.History.append(archive)
        else:
            history = Element('History')
            history.append(archive)
            self._element.append(history)

    def __str__(self):
        return str(
            'Entry: "{} ({})"'.format(self.path, self.username).encode('utf-8')
        )

    def __eq__(self, other):
        return (
            (self.title, self.username, self.password, self.url,
             self.notes, self.icon, self.tags, self.atime, self.ctime,
             self.mtime, self.expires, self.uuid) ==
            (other.title, other.username, other.password, other.url,
             other.notes, other.icon, other.tags, other.atime, other.ctime,
             other.mtime, other.expires, other.uuid)
        )
