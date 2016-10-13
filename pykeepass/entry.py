from __future__ import unicode_literals
from baseelement import BaseElement
from copy import deepcopy
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement
import logging
import xmlfactory
import group


logger = logging.getLogger(__name__)


class Entry(BaseElement):

    def __init__(self, title=None, username=None, password=None, url=None,
                 notes=None, tags=None, expires=None, expiration=None,
                 icon=None, element=None):
        if element is None:
            element = Element('Entry')
            title = xmlfactory.create_title_element(title)
            uuid = xmlfactory.create_uuid_element()
            username = xmlfactory.create_username_element(username)
            password = xmlfactory.create_password_element(password)
            times = xmlfactory.create_times_element(expires, expiration)
            if url:
                url = xmlfactory.create_url_element(url)
                element.append(url)
            if notes:
                notes = xmlfactory.create_notes_element(notes)
                element.append(notes)
            if tags:
                tags = xmlfactory.create_tags_element(tags)
                element.append(tags)
            if icon:
                icon = xmlfactory.create_icon_element(icon)
                element.append(icon)
            element.append(title)
            element.append(uuid)
            element.append(username)
            element.append(password)
            element.append(times)
        assert type(element) in [_Element, Element, ObjectifiedElement], \
            'The provided element is not an LXML Element, but {}'.format(
                type(element)
            )
        assert element.tag == 'Entry', 'The provided element is not an Entry '\
            'element, but a {}'.format(element.tag)

        self._element = element

    def __get_string_field(self, key):
        results = self._element.xpath('String/Key[text()="{}"]/../Value'.format(key))
        if results:
            return results[0].text

    def __set_string_field(self, key, value):
        results = self._element.xpath('String/Key[text()="{}"]/..'.format(key))
        if results:
            results[0].Value = value
        else:
            logger.debug('No field named {}. Create it.'.format(key))
            el = xmlfactory._create_string_element(key, value)
            self._element.append(el)

    @property
    def title(self):
        return self.__get_string_field('Title')

    @title.setter
    def title(self, value):
        return self.__set_string_field('Title', value)

    @property
    def username(self):
        return self.__get_string_field('UserName')

    @username.setter
    def username(self, value):
        return self.__set_string_field('UserName', value)

    @property
    def password(self):
        return self.__get_string_field('Password')

    @password.setter
    def password(self, value):
        return self.__set_string_field('Password', value)

    @property
    def url(self):
        return self.__get_string_field('URL')

    @url.setter
    def url(self, value):
        return self.__set_string_field('URL', value)

    @property
    def notes(self):
        return self.__get_string_field('Notes')

    @notes.setter
    def notes(self, value):
        return self.__set_string_field('Notes', value)

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

    def __get_times_property(self, prop):
        times = self._element.find('Times')
        if times is not None:
            prop = times.find(prop)
            if prop is not None:
                return prop.text

    @property
    def expires(self):
        d = self.__get_times_property('Expires')
        if d is not None:
            return d == 'True'

    @property
    def expiry_time(self):
        d = self.__get_times_property('ExpiryTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def ctime(self):
        d = self.__get_times_property('CreationTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def atime(self):
        d = self.__get_times_property('LastAccessTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def mtime(self):
        d = self.__get_times_property('LastModificationTime')
        if d is not None:
            return xmlfactory._date_from_str(d)

    @property
    def history(self):
        if self._element.find('History') is not None:
            return [Entry(element=x) for x in self._element.find('History').findall('Entry')]

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
            return group.Group(element=ancestor)

    @property
    def path(self):
        # The root group is an orphan
        if self.is_a_history_entry:
            pentry = Entry(element=self._element.getparent().getparent()).title
            return '[History of: {}]'.format(pentry)
        if self.parentgroup is None:
            return None
        p = self.parentgroup
        ppath = ''
        while p is not None and not p.is_root_group:
            if p.name is not None: # dont make the root group appear
                ppath += '{}/'.format(p.name)
            p = p.parentgroup
        return '{}{}'.format(ppath, self.title)

    def touch(self, modify=False):
        '''
        Update last access time of an entry
        '''
        self._element.Times.LastAccessTime = xmlfactory._dateformat()
        if modify:
            self._element.Times.LastModificationTime = xmlfactory._dateformat()

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
        return 'Entry: "{}" at "{}"'.format(self.title, self.path)

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
