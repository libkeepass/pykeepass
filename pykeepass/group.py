from __future__ import unicode_literals
from __future__ import absolute_import
from pykeepass.baseelement import BaseElement
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement
from lxml.builder import E
import pykeepass.entry


class Group(BaseElement):

    def __init__(self, name=None, element=None, icon=None, notes=None,
                 version=None, expires=None, expiry_time=None):

        assert type(version) is tuple, 'The provided version is not a tuple, but a {}'.format(
            type(version)
        )
        self._version = version


        if element is None:
            super(Group, self).__init__(
                element=Element('Group'),
                version=version,
                expires=expires,
                expiry_time=expiry_time,
                icon=icon
            )
            self._element.append(E.Name(name))
            if notes:
                self._element.append(E.Notes(notes))

        else:
            assert type(element) in [_Element, Element, ObjectifiedElement], \
                'The provided element is not an LXML Element, but {}'.format(
                    type(element)
                )
            assert element.tag == 'Group', 'The provided element is not a Group '\
                'element, but a {}'.format(element.tag)
            self._element = element

    @property
    def name(self):
        return self._get_subelement_text('Name')

    @name.setter
    def name(self, value):
        return self._set_subelement_text('Name', value)

    @property
    def notes(self):
        return self._get_subelement_text('Notes')

    @notes.setter
    def notes(self, value):
        return self._set_subelement_text('Notes', value)

    @property
    def entries(self):
        # FIXME
        # It may be better to keep a list of Entries as a (list) property
        # ... but that may become out of sync and what is supposed to happen
        # when an entry is updated?!
        # On the other side this would make things like "e in g.entries" work
        return [pykeepass.entry.Entry(element=x, version=self._version) for x in self._element.findall('Entry')]

    @property
    def subgroups(self):
        return [Group(element=x, version=self._version) for x in self._element.findall('Group')]

    @property
    def parentgroup(self):
        if self._element.getparent() is None:
            return None
        return Group(element=self._element.getparent(), version=self._version)

    @property
    def is_root_group(self):
        return self._element.getparent().tag == 'Root'

    @property
    def path(self):
        # The root group is an orphan
        if self.is_root_group or self.parentgroup is None:
            return '/'
        p = self.parentgroup
        ppath = ''
        while p is not None and not p.is_root_group:
            if p.name is not None: # dont make the root group appear
                ppath = '{}/{}'.format(p.name, ppath)
            p = p.parentgroup
        return '{}{}'.format(ppath, self.name)

    def append(self, entries):
        if type(entries) is list:
            for e in entries:
                self._element.append(e._element)
        else:
            self._element.append(entries._element)

    def __str__(self):
        return str('Group: "{}"'.format(self.path).encode('utf-8'))
