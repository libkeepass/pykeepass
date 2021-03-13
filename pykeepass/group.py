# FIXME python2
from __future__ import absolute_import, unicode_literals
from future.utils import python_2_unicode_compatible

from lxml.builder import E
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement

import pykeepass.entry
from pykeepass.baseelement import BaseElement


# FIXME python2
@python_2_unicode_compatible
class Group(BaseElement):

    def __init__(self, name=None, element=None, icon=None, notes=None,
                 kp=None, expires=None, expiry_time=None):

        self._kp = kp

        if element is None:
            super(Group, self).__init__(
                element=Element('Group'),
                kp=kp,
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
        return [pykeepass.entry.Entry(element=x, kp=self._kp) for x in self._element.findall('Entry')]

    @property
    def subgroups(self):
        return [Group(element=x, kp=self._kp) for x in self._element.findall('Group')]

    @property
    def is_root_group(self):
        return self._element.getparent().tag == 'Root'

    @property
    def path(self):
        # The root group is an orphan
        if self.is_root_group or self.parentgroup is None:
            return []
        p = self.parentgroup
        path = [self.name]
        while p is not None and not p.is_root_group:
            if p.name is not None:  # dont make the root group appear
                path.insert(0, p.name)
            p = p.parentgroup
        return path

    def append(self, entries):
        if type(entries) is list:
            for e in entries:
                self._element.append(e._element)
        else:
            self._element.append(entries._element)

    def __str__(self):
        # filter out NoneTypes and join into string
        pathstr = '/'.join('' if p==None else p for p in self.path)
        return 'Group: "{}"'.format(pathstr)
