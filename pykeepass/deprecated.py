# ---------- Find functions ---------------
# Use find_entries()/find_groups() instead

from typing import TYPE_CHECKING, Literal, Union, overload
from uuid import UUID

if TYPE_CHECKING:
    from .entry import Entry
    from .group import Group
    from .pykeepass import PyKeePass


@overload
def find_groups_by_name(
    self: "PyKeePass",
    group_name: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    *,
    first: Literal[True],
) -> "Group": ...


@overload
def find_groups_by_name(
    self: "PyKeePass",
    group_name: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    *,
    first: Literal[False] = False,
) -> list["Group"]: ...


def find_groups_by_name(
    self: "PyKeePass",
    group_name: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    first: bool = False,
) -> Union[list["Group"], "Group", None]:
    """@private"""
    return self.find_groups(
        name=group_name, regex=regex, flags=flags, group=group, first=first
    )


@overload
def find_groups_by_path(
    self: "PyKeePass",
    group_path_str: Union[list[str], None] = None,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    *,
    first: Literal[True],
) -> "Group": ...


@overload
def find_groups_by_path(
    self: "PyKeePass",
    group_path_str: Union[list[str], None] = None,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    *,
    first: Literal[False] = False,
) -> list["Group"]: ...


def find_groups_by_path(
    self: "PyKeePass",
    group_path_str: Union[list[str], None] = None,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    first: bool = False,
) -> Union[list["Group"], "Group", None]:
    """@private"""
    return self.find_groups(
        path=group_path_str, regex=regex, flags=flags, group=group, first=first
    )


@overload
def find_groups_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Group": ...


@overload
def find_groups_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Group"]: ...


def find_groups_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Group"], "Group", None]:
    """@private"""
    return self.find_groups(
        uuid=uuid, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_groups_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Group": ...


@overload
def find_groups_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Group"]: ...


def find_groups_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Group"], "Group", None]:
    """@private"""
    return self.find_groups(
        notes=notes, regex=regex, flags=flags, group=group, history=history, first=first
    )


# =========================
# Entries
# =========================


@overload
def find_entries_by_title(
    self: "PyKeePass",
    title: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_title(
    self: "PyKeePass",
    title: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_title(
    self: "PyKeePass",
    title: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        title=title, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_entries_by_username(
    self: "PyKeePass",
    username: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_username(
    self: "PyKeePass",
    username: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_username(
    self: "PyKeePass",
    username: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        username=username,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first,
    )


@overload
def find_entries_by_password(
    self: "PyKeePass",
    password: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_password(
    self: "PyKeePass",
    password: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_password(
    self: "PyKeePass",
    password: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        password=password,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first,
    )


@overload
def find_entries_by_url(
    self: "PyKeePass",
    url: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_url(
    self: "PyKeePass",
    url: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_url(
    self: "PyKeePass",
    url: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        url=url, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_entries_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_notes(
    self: "PyKeePass",
    notes: str,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        notes=notes, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_entries_by_path(
    self: "PyKeePass",
    path: Union[list[str], None],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_path(
    self: "PyKeePass",
    path: Union[list[str], None],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_path(
    self: "PyKeePass",
    path: Union[list[str], None],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        path=path, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_entries_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_uuid(
    self: "PyKeePass",
    uuid: UUID,
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        uuid=uuid, regex=regex, flags=flags, group=group, history=history, first=first
    )


@overload
def find_entries_by_string(
    self: "PyKeePass",
    string: dict[str, str],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[True],
) -> "Entry": ...


@overload
def find_entries_by_string(
    self: "PyKeePass",
    string: dict[str, str],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    *,
    first: Literal[False] = False,
) -> list["Entry"]: ...


def find_entries_by_string(
    self: "PyKeePass",
    string: dict[str, str],
    regex: bool = False,
    flags: Union[str, None] = None,
    group: Union["Group", None] = None,
    history: bool = False,
    first: bool = False,
) -> Union[list["Entry"], "Entry", None]:
    """@private"""
    return self.find_entries(
        string=string,
        regex=regex,
        flags=flags,
        group=group,
        history=history,
        first=first,
    )
