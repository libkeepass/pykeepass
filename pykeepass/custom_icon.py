# FIXME python2
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from future.utils import python_2_unicode_compatible

import uuid;
import base64;

import pykeepass.entry

# FIXME python2
@python_2_unicode_compatible
class CustomIcon(object):
    def __init__(self, element, kp=None):
        self._element = element
        self._kp = kp

    def __repr__(self):
        return "CustomIcon: '{}'".format(self.uuid)

    @property
    def uuid(self):
        field = self._element.find('UUID')
        if field is not None:
            uuid_bytes = base64.b64decode(field.text)
            custom_icon_uuid = uuid.UUID(bytes=uuid_bytes)
            return custom_icon_uuid
        return

    @uuid.setter
    def uuid(self, uuid):
        raise NotImplementedError()

    @property
    def data(self):
        field = self._element.find('Data')
        if field is not None:
            data_bytes = base64.b64decode(field.text)
            return data_bytes
        return

    @data.setter
    def data(self, filename):
        raise NotImplementedError()
