from __future__ import unicode_literals
import xmlfactory


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
            v = str(value)
        else:
            el = xmlfactory.create_element(tag, value)
            self._element.append(el)

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

