from datetime import datetime
from typing import TYPE_CHECKING

from lxml.builder import E
from lxml.etree import Element, _Element  # pyright: ignore[reportPrivateUsage]
from lxml.objectify import ObjectifiedElement

from .baseelement import BaseElement
from .entry import Entry

if TYPE_CHECKING:
    from .pykeepass import PyKeePass


class Group(BaseElement):
    def __init__(
        self,
        name: str | None = None,
        element: Element | _Element | ObjectifiedElement | None = None,
        icon: str | None = None,
        notes: str | None = None,
        kp: "PyKeePass | None" = None,
        expires: bool | None = None,
        expiry_time: datetime | None = None,
    ) -> None:
        self._kp = kp

        if element is None:
            super().__init__(
                element=Element("Group"),
                kp=kp,
                expires=expires,
                expiry_time=expiry_time,
                icon=icon,
            )
            if name is not None:
                self._element.append(E.Name(name))
            if notes:
                self._element.append(E.Notes(notes))

        else:
            assert type(element) in [_Element, Element, ObjectifiedElement], (
                "The provided element is not an LXML Element, but {}".format(
                    type(element)
                )
            )
            assert element.tag == "Group", (
                "The provided element is not a Group element, but a {}".format(
                    element.tag
                )
            )
            self._element = element

    @property
    def _first_entry(self) -> int:
        children = list(self._element)
        first_element = next(e for e in children if e.tag == "Entry")
        return children.index(first_element)

    @property
    def name(self) -> str | None:
        """`str`: get or set group name"""
        return self._get_subelement_text("Name")

    @name.setter
    def name(self, value: str) -> None:
        return self._set_subelement_text("Name", value)

    @property
    def notes(self) -> str | None:
        """`str`: get or set group notes"""
        return self._get_subelement_text("Notes")

    @notes.setter
    def notes(self, value: str) -> None:
        return self._set_subelement_text("Notes", value)

    @property
    def entries(self) -> list[Entry]:
        """`list` of `Entry`: get list of entries in this group"""
        return [Entry(element=x, kp=self._kp) for x in self._element.findall("Entry")]

    @property
    def subgroups(self) -> list["Group"]:
        """`list` of `Group`: get list of groups in this group"""
        return [Group(element=x, kp=self._kp) for x in self._element.findall("Group")]

    @property
    def is_root_group(self) -> bool:
        """`bool`: return True if this is the database root"""
        parent = self._element.getparent()
        return parent is not None and parent.tag == "Root"

    @property
    def path(self) -> list[str | None]:
        """`list` of (`str` or `None`): names of all parent groups, not including root"""
        # The root group is an orphan
        if self.is_root_group or self.parentgroup is None:
            return []
        p = self.parentgroup
        path: list[str | None] = [self.name]
        while p is not None and not p.is_root_group:
            if p.name is not None:  # dont make the root group appear
                path.insert(0, p.name)
            p = p.parentgroup
        return path

    def append(self, entries: "Entry | Group | list[Entry] | list[Group]") -> None:
        """Add copy of an entry or group to this group

        Args:
            entries (`Entry`, `Group` or `list` of `Entry`/`Group`)
        """
        # FIXME: check if `entries` is iterable instead of list
        if isinstance(entries, list):
            for e in entries:
                self._element.append(e._element)
        else:
            self._element.append(entries._element)

    def __str__(self) -> str:
        # filter out NoneTypes and join into string
        pathstr = "/".join("" if p is None else p for p in self.path)
        return 'Group: "{}"'.format(pathstr)
