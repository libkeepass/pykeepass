from lxml.builder import E
from lxml.etree import Element, _Element
from lxml.objectify import ObjectifiedElement

from .baseelement import BaseElement
from .entry import Entry


class Group(BaseElement):

    def __init__(self, name=None, element=None, icon=None, notes=None,
                 kp=None, expires=None, expiry_time=None):

        self._kp = kp

        if element is None:
            super().__init__(
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
    def _first_entry(self):
        children = self._element.getchildren()
        first_element = next(e for e in children if e.tag == "Entry")
        return children.index(first_element)

    @property
    def name(self):
        """str: get or set group name"""
        return self._get_subelement_text('Name')

    @name.setter
    def name(self, value):
        return self._set_subelement_text('Name', value)

    @property
    def notes(self):
        """str: get or set group notes"""
        return self._get_subelement_text('Notes')

    @notes.setter
    def notes(self, value):
        return self._set_subelement_text('Notes', value)

    @property
    def entries(self):
        """:obj:`list` of :obj:`Entry`: get list of entries in this group"""
        return [Entry(element=x, kp=self._kp) for x in self._element.findall('Entry')]

    @property
    def subgroups(self):
        """:obj:`list` of :obj:`Group`: get list of groups in this group"""
        return [Group(element=x, kp=self._kp) for x in self._element.findall('Group')]

    @property
    def is_root_group(self):
        """bool: return True if this is the database root"""
        return self._element.getparent().tag == 'Root'

    @property
    def path(self):
        """:obj:`list` of (:obj:`str` or None): a list containing names of all parent groups, not including root"""
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
        """Add copy of an entry to this group

        Args:
            entries (:obj:`Entry` or :obj:`list` of :obj:`Entry`)
        """
        if isinstance(entries, list):
            for e in entries:
                self._element.append(e._element)
        else:
            self._element.append(entries._element)

    def __str__(self):
        # filter out NoneTypes and join into string
        pathstr = '/'.join('' if p is None else p for p in self.path)
        return 'Group: "{}"'.format(pathstr)
