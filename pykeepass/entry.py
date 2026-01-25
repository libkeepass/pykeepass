from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING, cast

from lxml.builder import E
from lxml.etree import Element, _Element  # pyright: ignore[reportPrivateUsage]
from lxml.objectify import ObjectifiedElement

from . import attachment
from .baseelement import BaseElement

if TYPE_CHECKING:
    from .pykeepass import PyKeePass

logger = logging.getLogger(__name__)
reserved_keys = [
    "Title",
    "UserName",
    "Password",
    "URL",
    "Tags",
    "IconID",
    "Times",
    "History",
    "Notes",
    "otp",
]


class Entry(BaseElement):
    _kp: "PyKeePass | None"

    def __init__(
        self,
        title: str | None = None,
        username: str | None = None,
        password: str | None = None,
        url: str | None = None,
        notes: str | None = None,
        otp: str | None = None,
        tags: list[str] | str | None = None,
        expires: bool = False,
        expiry_time: datetime | None = None,
        icon: str | None = None,
        autotype_sequence: str | None = None,
        autotype_enabled: bool = True,
        autotype_window: str | None = None,
        element: Element | _Element | ObjectifiedElement | None = None,
        kp: "PyKeePass | None" = None,
    ) -> None:
        self._kp = kp

        if element is None:
            super().__init__(
                element=Element("Entry"),
                kp=kp,
                expires=expires,
                expiry_time=expiry_time,
                icon=icon,
            )
            self._element.append(E.String(E.Key("Title"), E.Value(title or "")))
            self._element.append(E.String(E.Key("UserName"), E.Value(username or "")))
            self._element.append(
                E.String(E.Key("Password"), E.Value(password or "", Protected="True"))
            )
            if url:
                self._element.append(E.String(E.Key("URL"), E.Value(url)))
            if notes:
                self._element.append(E.String(E.Key("Notes"), E.Value(notes)))
            if otp:
                self._element.append(
                    E.String(E.Key("otp"), E.Value(otp, Protected="True"))
                )
            if tags:
                self._element.append(
                    E.Tags(";".join(tags) if isinstance(tags, list) else tags)
                )
            self._element.append(
                E.AutoType(
                    E.Enabled(str(autotype_enabled)),
                    E.DataTransferObfuscation("0"),
                    E.DefaultSequence(
                        str(autotype_sequence) if autotype_sequence else ""
                    ),
                    E.Association(
                        E.Window(str(autotype_window) if autotype_window else ""),
                        E.KeystrokeSequence(""),
                    ),
                )
            )
            # FIXME: include custom_properties in constructor

        else:
            assert type(element) in [_Element, Element, ObjectifiedElement], (
                "The provided element is not an LXML Element, but a {}".format(
                    type(element)
                )
            )
            assert element.tag == "Entry", (
                "The provided element is not an Entry element, but a {}".format(
                    element.tag
                )
            )
            self._element = element

    def _get_string_field(self, key: str) -> str | None:
        """Get a string field from an entry

        Args:
            key (`str`): name of field

        Returns:
            `str` or `None`: field value
        """

        field = self._xpath(
            'String/Key[text()="{}"]/../Value'.format(key), history=True, first=True
        )
        if field is not None:
            return field.text

    def _set_string_field(
        self, key: str, value: str, protected: bool | None = None
    ) -> None:
        """Create or overwrite a string field in an Entry

        Args:
            key (`str`): name of field
            value (`str`): value of field
            protected (`bool` or `None`): mark whether the field should be protected in memory
                in other tools.  If `None`, value is either copied from existing field or field
                is created with protected property unset.

        Note: pykeepass does not support memory protection
        """
        field = cast(
            Element | None,
            self._xpath(
                'String/Key[text()="{}"]/..'.format(key), history=True, first=True
            ),
        )

        protected_str: str | None = None
        if protected is None:
            protected_field = cast(
                Element | None,
                self._xpath('String/Key[text()="{}"]/../Value'.format(key), first=True),
            )
            if protected_field is not None:
                protected_str = protected_field.attrib.get("Protected")
        else:
            protected_str = str(protected)

        if field is not None:
            self._element.remove(field)

        if protected_str is None:
            self._element.append(E.String(E.Key(key), E.Value(value)))
        else:
            self._element.append(
                E.String(E.Key(key), E.Value(value, Protected=protected_str))
            )

    def _get_string_field_keys(
        self, exclude_reserved: bool = False
    ) -> list[str | None]:
        results: list[str | None] = []
        for x in self._element.findall("String"):
            key_elem = x.find("Key")
            if key_elem is not None:
                results.append(key_elem.text)
            else:
                results.append(None)
        if exclude_reserved:
            return [x for x in results if x not in reserved_keys]
        else:
            return results

    @property
    def index(self) -> int:
        """`int`: index of a entry within a group"""
        group = self.group
        if group is None:
            raise ValueError("Entry has no parent group")
        group_elem = group._element
        children = list(group_elem)
        first_index = group._first_entry  # pyright: ignore[reportPrivateUsage]
        index = children.index(self._element)
        return index - first_index

    def reindex(self, new_index: int) -> None:
        """Move entry to a new index within a group

        Args:
            new_index (`int`): new index for the entry starting at 0
        """
        group = self.group
        if group is None:
            raise ValueError("Entry has no parent group")
        group_elem = group._element
        first_index = group._first_entry  # pyright: ignore[reportPrivateUsage]
        group_elem.remove(self._element)
        group_elem.insert(new_index + first_index, self._element)

    @property
    def attachments(self) -> list["attachment.Attachment"]:
        """`list` of `Attachment`: attachments associated with entry"""
        if self._kp is None:
            return []
        attachments_result = self._kp.find_attachments(
            element=self, filename=".*", regex=True, recursive=False
        )
        return [a for a in attachments_result]

    def add_attachment(self, id: int, filename: str) -> "attachment.Attachment":
        """Add attachment to entry

        The existence of a binary with the given `id` is not checked

        Args:
            id (`int`): ID of attachment in database
            filename (`str`): filename to assign to this attachment data

        Returns:
            `Attachment`
        """
        element = E.Binary(E.Key(filename), E.Value(Ref=str(id)))
        self._element.append(element)

        return attachment.Attachment(element=element, kp=self._kp)

    def delete_attachment(self, attachment_obj: "attachment.Attachment") -> None:
        """remove an attachment from entry.  Does not remove binary data"""
        attachment_obj.delete()

    def deref(self, attribute: str) -> str | None:
        """See `PyKeePass.deref`"""
        if self._kp is None:
            return None
        result = self._kp.deref(getattr(self, attribute))
        return result

    @property
    def title(self) -> str | None:
        """get or set entry title"""
        return self._get_string_field("Title")

    @title.setter
    def title(self, value: str | None) -> None:
        return self._set_string_field("Title", value or "")

    @property
    def username(self) -> str | None:
        """`str`: get or set entry username"""
        return self._get_string_field("UserName")

    @username.setter
    def username(self, value: str | None) -> None:
        return self._set_string_field("UserName", value or "")

    @property
    def password(self) -> str | None:
        """`str`: get or set entry password"""
        return self._get_string_field("Password")

    @password.setter
    def password(self, value: str | None) -> None:
        if self.password:
            return self._set_string_field("Password", value or "", True)
        else:
            return self._set_string_field("Password", value or "", True)

    @property
    def url(self) -> str | None:
        """str: get or set entry URL"""
        return self._get_string_field("URL")

    @url.setter
    def url(self, value: str | None) -> None:
        return self._set_string_field("URL", value or "")

    @property
    def notes(self) -> str | None:
        """`str`: get or set entry notes"""
        return self._get_string_field("Notes")

    @notes.setter
    def notes(self, value: str | None) -> None:
        return self._set_string_field("Notes", value or "")

    @property
    def icon(self) -> str | None:
        """`str`: get or set entry icon. See `icons`"""
        return self._get_subelement_text("IconID")

    @icon.setter
    def icon(self, value: str | None) -> None:
        return self._set_subelement_text("IconID", value or "")

    @property
    def tags(self) -> list[str]:
        """`str`: get or set entry tags"""
        val = self._get_subelement_text("Tags")
        return val.replace(",", ";").split(";") if val else []

    @tags.setter
    def tags(self, value: list[str] | str, sep: str = ";") -> None:
        # Accept both str or list
        v = sep.join(value if isinstance(value, list) else [value])
        return self._set_subelement_text("Tags", v)

    @property
    def otp(self) -> str | None:
        """`str`: get or set entry OTP text. (defacto standard)"""
        return self._get_string_field("otp")

    @otp.setter
    def otp(self, value: str | None) -> None:
        if self.otp:
            return self._set_string_field("otp", value or "", True)
        else:
            return self._set_string_field("otp", value or "", True)

    @property
    def history(self) -> list["HistoryEntry"]:
        """`list` of `HistoryEntry`: get entry history"""
        history_elem = self._element.find("History")
        if history_elem is not None:
            return [
                HistoryEntry(element=x, kp=self._kp)
                for x in history_elem.findall("Entry")
            ]
        else:
            return []

    @history.setter
    def history(self, value: object) -> None:
        raise NotImplementedError()

    @property
    def autotype_enabled(self) -> bool | None:
        """bool: get or set autotype enabled state.  Determines whether `autotype_sequence` should be used"""
        enabled = self._element.find("AutoType/Enabled")
        if enabled is not None and enabled.text is not None:
            return enabled.text == "True"
        return None

    @autotype_enabled.setter
    def autotype_enabled(self, value: bool | None) -> None:
        enabled = self._element.find("AutoType/Enabled")
        if enabled is not None:
            if value is not None:
                enabled.text = str(value)
            else:
                enabled.text = None

    @property
    def autotype_sequence(self) -> str | None:
        """str: get or set [autotype string](https://keepass.info/help/base/autotype.html)"""
        sequence = self._element.find("AutoType/DefaultSequence")
        if sequence is None or sequence.text == "":
            return None
        return sequence.text

    @autotype_sequence.setter
    def autotype_sequence(self, value: str | None) -> None:
        sequence = self._element.find("AutoType/DefaultSequence")
        if sequence is not None:
            sequence.text = value

    @property
    def autotype_window(self) -> str | None:
        """`str`: get or set [autotype target window filter](https://keepass.info/help/base/autotype.html#autowindows)"""
        window = self._element.find("AutoType/Association/Window")
        if window is None or window.text == "":
            return None
        return window.text

    @autotype_window.setter
    def autotype_window(self, value: str | None) -> None:
        window = self._element.find("AutoType/Association/Window")
        if window is not None:
            window.text = value

    @property
    def is_a_history_entry(self) -> bool:
        """`bool`: check if entry is History entry"""
        parent = self._element.getparent()
        if parent is not None:
            return parent.tag == "History"
        return False

    @property
    def path(self) -> list[str | None] | None:
        """`list` of (`str` or `None`): Path of entry.  List contains all parent group names
        ending with entry title. May contain `None` for unnamed/untitled groups/entries."""

        # The root group is an orphan
        if self.parentgroup is None:
            return None
        p = self.parentgroup
        path = [self.title]
        while p is not None and not p.is_root_group:
            if p.name is not None:  # dont make the root group appear
                path.insert(0, p.name)
            p = p.parentgroup
        return path

    def set_custom_property(self, key: str, value: str, protect: bool = False) -> None:
        assert key not in reserved_keys, "{} is a reserved key".format(key)
        return self._set_string_field(key, value, protect)

    def get_custom_property(self, key: str) -> str | None:
        assert key not in reserved_keys, "{} is a reserved key".format(key)
        return self._get_string_field(key)

    def delete_custom_property(self, key: str) -> None:
        if key not in self._get_string_field_keys(exclude_reserved=True):
            raise AttributeError("No such key: {}".format(key))
        prop = cast(
            Element | None,
            self._xpath('String/Key[text()="{}"]/..'.format(key), first=True),
        )
        if prop is None:
            raise AttributeError("Could not find property element")
        self._element.remove(prop)

    def is_custom_property_protected(self, key: str) -> bool:
        """Whether a custom property is protected.

        Return False if the entry does not have a custom property with the
        specified key.

        Args:
            key (`str`): key of the custom property to check.

        Returns:
            `bool`: Whether the custom property is protected.

        """
        assert key not in reserved_keys, "{} is a reserved key".format(key)
        return self._is_property_protected(key)

    def _is_property_protected(self, key: str) -> bool:
        """Whether a property is protected."""
        field = cast(
            Element | None,
            self._xpath('String/Key[text()="{}"]/../Value'.format(key), first=True),
        )
        if field is not None:
            return field.attrib.get("Protected", "False") == "True"
        return False

    @property
    def custom_properties(self) -> dict[str, str | None]:
        keys = self._get_string_field_keys(exclude_reserved=True)
        props: dict[str, str | None] = {}
        for k in keys:
            if k is not None:
                props[k] = self._get_string_field(k)
        return props

    def ref(self, attribute: str) -> str:
        """Create reference to an attribute of this element.

        Args:
            attribute (`str`): one of 'title', 'username', 'password', 'url', 'notes', or 'uuid'

        Returns:
            `str`: [field reference][fieldref] to this field of this entry

        [fieldref]: https://keepass.info/help/base/fieldrefs.html
        """
        attribute_to_field = {
            "title": "T",
            "username": "U",
            "password": "P",
            "url": "A",
            "notes": "N",
            "uuid": "I",
        }
        return "{{REF:{}@I:{}}}".format(
            attribute_to_field[attribute], self.uuid.hex.upper()
        )

    def save_history(self) -> None:
        """
        Save the entry in its history.  History is not created unless this function is
        explicitly called.
        """
        archive = deepcopy(self._element)
        hist = archive.find("History")
        if hist is not None:
            archive.remove(hist)
            history_elem = self._element.find("History")
            if history_elem is not None:
                history_elem.append(archive)
        else:
            history = Element("History")
            history.append(archive)
            self._element.append(history)

    def delete_history(
        self, history_entry: "Entry | None" = None, all: bool = False
    ) -> None:
        """
        Delete entries from history

        Args:
            history_entry (`Entry`): history item to delete
            all (`bool`): delete all entries from history.  Default is False
        """

        if all:
            history_elem = self._element.find("History")
            if history_elem is not None:
                self._element.remove(history_elem)
        else:
            history_elem = self._element.find("History")
            if history_elem is not None and history_entry is not None:
                history_elem.remove(history_entry._element)

    def __str__(self) -> str:
        # filter out NoneTypes and join into string
        path = self.path
        if path is None:
            pathstr = ""
        else:
            pathstr = "/".join("" if p is None else p for p in path)
        return 'Entry: "{} ({})"'.format(pathstr, self.username)


class HistoryEntry(Entry):
    def __str__(self) -> str:
        pathstr = super().__str__()
        return "HistoryEntry: {}".format(pathstr)

    def __hash__(self) -> int:
        # All history items share the same UUID with themselves and their
        # parent, so consider the mtime also
        return hash((self.uuid, self.mtime))
