from __future__ import unicode_literals
from __future__ import absolute_import
from pykeepass.baseelement import BaseElement
from copy import deepcopy
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement
import logging
import pykeepass.xmlfactory as xmlfactory
import pykeepass.group
from datetime import datetime, timedelta
import dateutil.parser, dateutil.tz as tz
import base64

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
        if element is None:
            element = Element('Entry')
            title = xmlfactory.create_title_element(title)
            uuid = xmlfactory.create_uuid_element()
            username = xmlfactory.create_username_element(username)
            password = xmlfactory.create_password_element(password)
            times = xmlfactory.create_times_element(expires, expiry_time)
            if url:
                url_el = xmlfactory.create_url_element(url)
                element.append(url_el)
            if notes:
                notes_el = xmlfactory.create_notes_element(notes)
                element.append(notes_el)
            if tags:
                tags_el = xmlfactory.create_tags_element(tags)
                element.append(tags_el)
            if icon:
                icon_el = xmlfactory.create_icon_element(icon)
                element.append(icon_el)
            element.append(title)
            element.append(uuid)
            element.append(username)
            element.append(password)
            element.append(times)
        assert type(element) in [_Element, Element, ObjectifiedElement], \
            'The provided element is not an LXML Element, but a {}'.format(
                type(element)
            )
        assert element.tag == 'Entry', 'The provided element is not an Entry '\
            'element, but a {}'.format(element.tag)
        assert type(version) is tuple, 'The provided version is not a tuple, but a {}'.format(
            type(version)
        )

        self._element = element
        self.version = version

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
        el = xmlfactory._create_string_element(key, value)
        self._element.append(el)

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

    def _get_times_property(self, prop):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                if self.version >= (4, 0):
                    # decode KDBX4 date from b64 format
                    return (
                        datetime(year=1, month=1, day=1) +
                        timedelta(
                            seconds=int.from_bytes(
                                base64.b64decode(prop.text), 'little'
                            )
                        )
                    )
                else:
                    return dateutil.parser.parse(
                        prop.text,
                        tzinfos={'UTC':tz.gettz('UTC')}
                    )

    def _set_times_property(self, prop, value):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                if self.version >= (4, 0):
                    # encode KDBX4 date to b64 format
                    diff_seconds = (
                        xmlfactory.datetime_to_utc(value).isoformat() -
                        datetime(year=1, month=1, day=1)
                    ).total_seconds()
                    prop.text = base64.b64encode(
                        struct.pack('<Q', diff_seconds),
                        'big'
                    )
                else:
                    prop.text = xmlfactory.datetime_to_utc(value).isoformat()

    @property
    def expires(self):
        times = self._element.find('Times')
        d = times.find('Expires').text
        if d is not None:
            return d == 'True'

    @expires.setter
    def expires(self, value):
        d = self._element.find('Times').find('Expires')
        d.text = 'True' if value else 'False'

    @property
    def expired(self):
        return self.expires and (datetime.utcnow() > self.expiry_time)


    @property
    def expiry_time(self):
        return self._get_times_property('ExpiryTime')

    @expiry_time.setter
    def expiry_time(self, value):
        self._set_times_property('ExpiryTime', value)

    @property
    def ctime(self):
        return self._get_times_property('CreationTime')

    @ctime.setter
    def ctime(self, value):
        self._set_times_property('CreationTime', value)

    @property
    def atime(self):
        return self._get_times_property('LastAccessTime')

    @atime.setter
    def atime(self, value):
        self._set_times_property('LastAccessTime', value)

    @property
    def mtime(self):
        return self._get_times_property('LastModificationTime')

    @mtime.setter
    def mtime(self, value):
        self._set_times_property('LastModificationTime', value)

    @property
    def history(self):
        if self._element.find('History') is not None:
            return [Entry(element=x, version=self.version) for x in self._element.find('History').findall('Entry')]

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
            return pykeepass.group.Group(element=ancestor, version=self.version)

    @property
    def path(self):
        # The root group is an orphan
        if self.is_a_history_entry:
            pentry = Entry(
                element=self._element.getparent().getparent(),
                version=self.version
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

    def delete(self):
        self._element.getparent().remove(self._element)

    def __str__(self):
        return str(
            'Entry: "{} ({})"'.format(self.path, self.username).encode('utf-8')
        )

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            (self.title, self.username, self.password, self.url,
             self.notes, self.icon, self.tags, self.atime, self.ctime,
             self.mtime, self.expires, self.uuid) ==
            (other.title, other.username, other.password, other.url,
             other.notes, other.icon, other.tags, other.atime, other.ctime,
             other.mtime, other.expires, other.uuid)
        )
