from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal, overload

from lxml import etree
from lxml.builder import E
from lxml.etree import Element

from .exceptions import BinaryError

if TYPE_CHECKING:
    from . import Attachment, Entry
    from .group import Group
    from .pykeepass import PyKeePass


class BaseElement:
    """Entry and Group inherit from this class"""

    _element: Element
    _kp: "PyKeePass | None"
    text: str | None

    def __init__(
        self,
        element: Element,
        kp: "PyKeePass | None" = None,
        icon: str | None = None,
        expires: bool | None = False,
        expiry_time: datetime | None = None,
    ) -> None:
        self._element = element
        self._kp = kp
        self._element.append(
            E.UUID(base64.b64encode(uuid.uuid1().bytes).decode("utf-8"))
        )
        if icon:
            self._element.append(E.IconID(icon))
        if self._kp is None:
            raise BinaryError("BaseElement has no associated database")
        current_time_str = self._kp._encode_time(datetime.now(timezone.utc))  # pyright: ignore[reportPrivateUsage]
        if expiry_time:
            expiry_time_str = self._kp._encode_time(  # pyright: ignore[reportPrivateUsage]
                expiry_time.astimezone(timezone.utc)
            )
        else:
            expiry_time_str = current_time_str

        self._element.append(
            E.Times(
                E.CreationTime(current_time_str),
                E.LastModificationTime(current_time_str),
                E.LastAccessTime(current_time_str),
                E.ExpiryTime(expiry_time_str),
                E.Expires(str(expires if expires is not None else False)),
                E.UsageCount(str(0)),
                E.LocationChanged(current_time_str),
            )
        )

    @overload
    def _xpath(
        self, xpath: str, *, first: Literal[True], **kwargs: Any
    ) -> "Group | Entry | Attachment | Element | None": ...

    @overload
    def _xpath(
        self, xpath: str, *, first: Literal[False] = False, **kwargs: Any
    ) -> list["Group | Entry | Attachment | Element"]: ...

    def _xpath(
        self, xpath: str, *, first: bool = False, **kwargs: Any
    ) -> "Group | Entry | Attachment | Element | list[Group | Entry | Attachment | Element] | None":
        if self._kp is None:
            return [] if not first else None
        return self._kp._xpath(xpath, tree=self._element, first=first, **kwargs)  # pyright: ignore[reportReturnType, reportPrivateUsage]

    def _get_subelement_text(self, tag: str) -> str | None:
        v = self._element.find(tag)
        if v is not None:
            return v.text
        return None

    def _set_subelement_text(self, tag: str, value: str) -> None:
        v = self._element.find(tag)
        if v is not None:
            self._element.remove(v)
        self._element.append(getattr(E, tag)(value))

    @property
    def group(self) -> "Group | None":
        return self._xpath("(ancestor::Group)[last()]", first=True, cast=True)  # pyright: ignore[reportReturnType]

    parentgroup = group

    def dump_xml(self, pretty_print: bool = False) -> bytes:
        return etree.tostring(self._element, pretty_print=pretty_print)

    @property
    def uuid(self) -> uuid.UUID:
        """Returns uuid of this element as a uuid.UUID object"""
        b64_uuid = self._get_subelement_text("UUID")
        if b64_uuid is None:
            raise ValueError("UUID element not found")
        return uuid.UUID(bytes=base64.b64decode(b64_uuid))

    @uuid.setter
    def uuid(self, uuid_obj: uuid.UUID) -> None:
        """Set element uuid. `uuid_obj` is a uuid.UUID object"""
        b64_uuid = base64.b64encode(uuid_obj.bytes).decode("utf-8")
        return self._set_subelement_text("UUID", b64_uuid)

    @property
    def icon(self) -> str | None:
        return self._get_subelement_text("IconID")

    @icon.setter
    def icon(self, value: str) -> None:
        return self._set_subelement_text("IconID", value)

    @property
    def _path(self) -> str:
        return self._element.getroottree().getpath(self._element)

    def _get_times_property(self, prop: str) -> datetime | None:
        times = self._element.find("Times")
        if times is not None:
            prop_elem = times.find(prop)
            if prop_elem is not None and prop_elem.text is not None:
                if self._kp is None:
                    return None
                return self._kp._decode_time(prop_elem.text)  # pyright: ignore[reportPrivateUsage]
        return None

    def _set_times_property(self, prop: str, value: datetime) -> None:
        if self._kp is None:
            return
        times = self._element.find("Times")
        if times is not None:
            prop_elem = times.find(prop)
            if prop_elem is not None:
                prop_elem.text = self._kp._encode_time(value)  # pyright: ignore[reportPrivateUsage]

    @property
    def expires(self) -> bool:
        times = self._element.find("Times")
        if times is None:
            return False
        d = times.find("Expires")
        if d is None or d.text is None:
            return False
        return d.text == "True"

    @expires.setter
    def expires(self, value: bool) -> None:
        d = self._element.find("Times")
        if d is not None:
            expires_elem = d.find("Expires")
            if expires_elem is not None:
                expires_elem.text = "True" if value else "False"

    @property
    def expired(self) -> bool:
        if self.expires:
            expiry = self.expiry_time
            if expiry is not None:
                return datetime.now(timezone.utc) > expiry
        return False

    @property
    def expiry_time(self) -> datetime | None:
        return self._get_times_property("ExpiryTime")

    @expiry_time.setter
    def expiry_time(self, value: datetime) -> None:
        self._set_times_property("ExpiryTime", value)

    @property
    def ctime(self) -> datetime | None:
        """(datetime.datetime): Creation time."""
        return self._get_times_property("CreationTime")

    @ctime.setter
    def ctime(self, value: datetime) -> None:
        self._set_times_property("CreationTime", value)

    @property
    def atime(self) -> datetime | None:
        """(datetime.datetime): Access time. Update with touch()"""
        return self._get_times_property("LastAccessTime")

    @atime.setter
    def atime(self, value: datetime) -> None:
        self._set_times_property("LastAccessTime", value)

    @property
    def mtime(self) -> datetime | None:
        """(datetime.datetime): Access time. Update with touch(modify=True)"""
        return self._get_times_property("LastModificationTime")

    @mtime.setter
    def mtime(self, value: datetime) -> None:
        self._set_times_property("LastModificationTime", value)

    def delete(self) -> None:
        parent = self._element.getparent()
        if parent is not None:
            parent.remove(self._element)

    def __unicode__(self) -> str:
        return self.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return hash((self.uuid,))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseElement):
            return hash(self) == hash(other)
        return NotImplemented

    def touch(self, modify: bool = False) -> None:
        """
        Update last access time of an entry/group

        Args:
            modify (bool): update access time as well a modification time
        """
        now = datetime.now(timezone.utc)
        self.atime = now
        if modify:
            self.mtime = now
