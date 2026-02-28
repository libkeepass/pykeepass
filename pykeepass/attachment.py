from . import entry
from .exceptions import BinaryError


class Attachment:
    """Binary data attached to an `Entry`.

    *Binary* refers to the bytes of the attached data
    (stored at the root level of the database), while *attachment* is a
    reference to a binary (stored in an entry).  A binary can be referenced
    by none, one or many attachments.
    A piece of binary data may be attached to multiple entries

    """
    def __init__(self, element=None, kp=None, id=None, filename=None):
        self._element = element
        self._kp = kp

    def __repr__(self):
        return "Attachment: '{}' -> {}".format(self.filename, self.id)

    @property
    def id(self):
        """`str`: get or set id of binary the attachment points to"""
        return int(self._element.find('Value').attrib['Ref'])

    @id.setter
    def id(self, id):
        self._element.find('Value').attrib['Ref'] = str(id)

    @property
    def filename(self):
        """`str`: get or set filename string"""
        return self._element.find('Key').text

    @filename.setter
    def filename(self, filename):
        self._element.find('Key').text = filename

    @property
    def entry(self):
        """`Entry`: entry this attachment is associated with"""
        ancestor = self._element.getparent()
        return entry.Entry(element=ancestor, kp=self._kp)

    @property
    def binary(self):
        """`bytes`: binary data this attachment points to"""
        try:
            return self._kp.binaries[self.id]
        except IndexError:
            raise BinaryError('No such binary with id {}'.format(self.id))

    data = binary

    def delete(self):
        """delete this attachment"""
        self._element.getparent().remove(self._element)
