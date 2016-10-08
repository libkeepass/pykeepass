from baseelement import BaseElement
from lxml.etree import Element
import xmlfactory
import entry


class Group(BaseElement):
    def __init__(self, name=None, element=None):
        if element is None:
            element = Element('Group')
            name = xmlfactory.create_name_element(name)
            uuid = xmlfactory.create_uuid_element()
            element.append(uuid)
            element.append(name)
        self._element = element

    @property
    def name(self):
        return self._get_subelement_text('Name')

    @name.setter
    def name(self, value):
        return self._set_subelement_text('Name', value)

    @property
    def entries(self):
        # FIXME
        # It may be better to keep a list of Entries as a (list) property
        # ... but that may become out of sync and what is supposed to happen
        # when an entry is updated?!
        # On the other side this would make things like "e in g.entries" work
        return [entry.Entry(element=x) for x in self._element.findall('Entry')]

    @property
    def subgroups(self):
        return [Group(element=x) for x in self._element.findall('Group')]

    @property
    def parentgroup(self):
        if self._element.getparent() is None:
            return None
        return Group(element=self._element.getparent())

    def append(self, entries):
        if type(entries) is list:
            for e in entries:
                self._element.append(e._element)
        else:
            self._element.append(entries._element)

    def __str__(self):
        return 'Group: {} at {}'.format(self.name, self.path)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()
