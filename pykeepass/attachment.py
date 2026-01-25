from __future__ import annotations

from typing import TYPE_CHECKING

from lxml.etree import Element

from . import entry
from .baseelement import BaseElement
from .exceptions import BinaryError

if TYPE_CHECKING:
    from construct import FilenameType, StreamType

    from .pykeepass import PyKeePass


class Attachment(BaseElement):
    """Binary data attached to an `Entry`.

    *Binary* refers to the bytes of the attached data
    (stored at the root level of the database), while *attachment* is a
    reference to a binary (stored in an entry).  A binary can be referenced
    by none, one or many attachments.
    A piece of binary data may be attached to multiple entries

    """

    _element: Element
    _kp: "PyKeePass | None"

    def __init__(
        self,
        element: Element,
        kp: "PyKeePass | None",
        id: int | None = None,
        filename: FilenameType | StreamType | None = None,
    ) -> None:
        self._element = element
        self._kp = kp

    def __repr__(self) -> str:
        return "Attachment: '{}' -> {}".format(self.filename, self.id)

    @property
    def id(self) -> int:
        """`int`: get or set id of binary the attachment points to"""
        value_elem = self._element.find("Value")
        if value_elem is None:
            raise ValueError("Value element not found")
        ref = value_elem.attrib.get("Ref")
        if ref is None:
            raise ValueError("Ref attribute not found")
        return int(ref)

    @id.setter
    def id(self, id: int) -> None:
        value_elem = self._element.find("Value")
        if value_elem is None:
            raise ValueError("Value element not found")
        value_elem.attrib["Ref"] = str(id)

    @property
    def filename(self) -> str | None:
        """`str`: get or set filename string"""
        key_elem = self._element.find("Key")
        if key_elem is None:
            return None
        return key_elem.text

    @filename.setter
    def filename(self, filename: str) -> None:
        key_elem = self._element.find("Key")
        if key_elem is None:
            raise ValueError("Key element not found")
        key_elem.text = filename

    @property
    def entry(self) -> "entry.Entry":
        """`Entry`: entry this attachment is associated with"""
        parent = self._element.getparent()
        if parent is None:
            raise ValueError("Parent element not found")
        return entry.Entry(element=parent, kp=self._kp)

    @property
    def binary(self) -> bytes:
        """`bytes`: binary data this attachment points to"""
        if self._kp is None:
            raise BinaryError("Attachment has no associated database")
        try:
            return self._kp.binaries[self.id]
        except IndexError:
            raise BinaryError("No such binary with id {}".format(self.id))

    data = binary

    def delete(self) -> None:
        """delete this attachment"""
        parent = self._element.getparent()
        if parent is None:
            raise ValueError("Parent element not found")
        parent.remove(self._element)
