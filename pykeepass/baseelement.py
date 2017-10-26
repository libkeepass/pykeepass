from __future__ import unicode_literals
from __future__ import absolute_import
import pykeepass.xmlfactory as xmlfactory
import lxml


class BaseElement(object):

    def __init__(self, element=None):
        self._element = element

    def _get_subelement_text(self, tag):
        v = self._element.find(tag)
        if v is not None:
            return v.text

    def _set_subelement_text(self, tag, value):
        v = self._element.find(tag)
        if v is not None:
            self._element.remove(v)
        el = xmlfactory.create_element(tag, value)
        self._element.append(el)

    def dump_xml(self, pretty_print=False):
        return lxml.etree.tostring(self._element, pretty_print=pretty_print)

    @property
    def uuid(self):
        return self._get_subelement_text('UUID')

    @uuid.setter
    def uuid(self, value):
        # Ignore the provided value to avoid an uuid collision
        return self._set_subelement_text('UUID', xmlfactory._generate_uuid())

    @property
    def _path(self):
        return self._element.getroottree().getpath(self._element)

