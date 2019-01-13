from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import pykeepass.entry
from collections import namedtuple

class Attachment(object):
    def __init__(self, element=None, kp=None, id=None, filename=None):
        self._element = element
        self._kp = kp

    def __repr__(self):
        return "Attachment: '{}' -> {}".format(self.filename, self.id)

    @property
    def id(self):
        return int(self._element.find('Value').attrib['Ref'])

    @id.setter
    def id(self, id):
        self._element.find('Value').attrib['Ref'] = str(id)

    @property
    def filename(self):
        return self._element.find('Key').text

    @filename.setter
    def filename(self, filename):
        self._element.find('Key').text = filename

    @property
    def entry(self):
        ancestor = self._element.getparent()
        return pykeepass.entry.Entry(element=ancestor, kp=self._kp)

    @property
    def data(self):
        try:
            return self._kp.binaries[self.id]
        except IndexError:
            raise AttachmentError('No such attachment id')

    def delete(self):
        self._element.getparent().remove(self._element)
