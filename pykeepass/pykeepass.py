from __future__ import annotations

import base64
import logging
import os
import re
import shutil
import struct
import uuid
import zlib
from binascii import Error as BinasciiError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union, cast, overload
from xml.etree.ElementTree import Element, ElementTree

from construct import (
    CheckError,
    ChecksumError,
    Container,
)
from lxml import etree
from lxml.builder import E

from .attachment import Attachment
from .entry import Entry
from .exceptions import (
    BinaryError,
    CredentialsError,
    HeaderChecksumError,
    PayloadChecksumError,
    UnableToSendToRecycleBin,
)
from .group import Group
from .kdbx_parsing import KDBX, kdf_uuids
from .xpath import attachment_xp, entry_xp, group_xp, path_xp

logger = logging.getLogger(__name__)

BLANK_DATABASE_FILENAME = "blank_database.kdbx"
BLANK_DATABASE_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), BLANK_DATABASE_FILENAME
)
BLANK_DATABASE_PASSWORD = "password"


if TYPE_CHECKING:
    from construct import Context, FilenameType, StreamType
else:
    FilenameType = Any
    StreamType = Any

Xpath_Result = Union[Group, Entry, Attachment, Element]


class PyKeePass:
    """Open a KeePass database

    Args:
        filename (`str`, optional): path to database or stream object.
            If None, the path given when the database was opened is used.
        password (`str`, optional): database password.  If None,
            database is assumed to have no password
        keyfile (`str`, optional): path to keyfile.  If None,
            database is assumed to have no keyfile
        transformed_key (`bytes`, optional): precomputed transformed
            key.
        decrypt (`bool`, optional): whether to decrypt XML payload.
            Set `False` to access outer header information without decrypting
            database.

    Raises:
        `CredentialsError`: raised when password/keyfile or transformed key
            are wrong
        `HeaderChecksumError`: raised when checksum in database header is
            is wrong.  e.g. database tampering or file corruption
        `PayloadChecksumError`: raised when payload blocks checksum is wrong,
            e.g. corruption during database saving

    """

    # TODO: raise, no filename provided, database not open

    filename: FilenameType | StreamType
    _password: str | None
    _keyfile: FilenameType | None
    kdbx: Container[Any]

    def __init__(
        self,
        filename: FilenameType | StreamType,
        password: str | None = None,
        keyfile: FilenameType | None = None,
        transformed_key: bytes | None = None,
        decrypt: bool = True,
    ) -> None:
        self.read(
            filename=filename,
            password=password,
            keyfile=keyfile,
            transformed_key=transformed_key,
            decrypt=decrypt,
        )

    def __enter__(self) -> "PyKeePass":
        return self

    def __exit__(self, typ: Any, value: Any, tb: Any) -> None:
        # see issue 137
        pass

    def read(
        self,
        filename: FilenameType | StreamType | None = None,
        password: str | None = None,
        keyfile: FilenameType | None = None,
        transformed_key: bytes | None = None,
        decrypt: bool = True,
    ) -> None:
        """
        See class docstring.
        """

        # TODO: - raise, no filename provided, database not open
        self._password = password
        self._keyfile = keyfile
        if filename:
            self.filename = filename
        else:
            filename = self.filename

        try:
            if hasattr(filename, "read"):
                self.kdbx = KDBX.parse_stream(
                    cast(StreamType, filename),
                    password=password,
                    keyfile=keyfile,
                    transformed_key=transformed_key,
                    decrypt=decrypt,
                )
            else:
                self.kdbx = KDBX.parse_file(
                    cast(FilenameType, filename),
                    password=password,
                    keyfile=keyfile,
                    transformed_key=transformed_key,
                    decrypt=decrypt,
                )

        except CheckError as e:
            if e.path == "(parsing) -> header -> sig_check":
                raise HeaderChecksumError("Not a KeePass database")
            else:
                raise

        # body integrity/verification
        except ChecksumError as e:
            if e.path in (
                "(parsing) -> body -> cred_check",  # KDBX4
                "(parsing) -> cred_check",  # KDBX3
            ):
                raise CredentialsError("Invalid credentials")
            elif e.path == "(parsing) -> body -> sha256":
                raise HeaderChecksumError("Corrupted database")
            elif e.path in (
                "(parsing) -> body -> payload -> hmac_hash",  # KDBX4
                "(parsing) -> xml -> block_hash",  # KDBX3
            ):
                raise PayloadChecksumError("Error reading database contents")
            else:
                raise

    def reload(self):
        """Reload current database using previously given credentials"""

        self.read(self.filename, self.password, self.keyfile)

    def save(
        self,
        filename: FilenameType | StreamType | None = None,
        transformed_key: bytes | None = None,
    ) -> None:
        """Save current database object to disk.

        Args:
            filename (`str`, optional): path to database or stream object.
                If None, the path given when the database was opened is used.
                PyKeePass.filename is unchanged.
            transformed_key (`bytes`, optional): precomputed transformed
                key.
        """

        if not filename:
            filename = self.filename

        if hasattr(filename, "write"):
            KDBX.build_stream(
                self.kdbx,
                cast(StreamType, filename),
                password=self.password,
                keyfile=self.keyfile,
                transformed_key=transformed_key,
                decrypt=True,
            )
        else:
            # save to temporary file to prevent database clobbering
            # see issues 223, 101
            filename_tmp = Path(cast(str, filename)).with_suffix(".tmp")
            try:
                KDBX.build_file(
                    self.kdbx,
                    filename_tmp,
                    password=self.password,
                    keyfile=self.keyfile,
                    transformed_key=transformed_key,
                    decrypt=True,
                )
            except Exception as e:
                os.remove(filename_tmp)
                raise e
            shutil.move(filename_tmp, cast(str, filename))

    @property
    def version(self) -> tuple[int, int]:
        """`tuple` of `int`: Length 2 tuple of ints containing major and minor versions.
        Generally (3, 1) or (4, 0)."""
        return (
            self.kdbx.header.value.major_version,
            self.kdbx.header.value.minor_version,
        )

    @property
    def encryption_algorithm(
        self,
    ) -> Union[Literal["aes256"], Literal["chacha20"], Literal["twofish"]]:
        """`str`: encryption algorithm used by database during decryption.
        Can be one of 'aes256', 'chacha20', or 'twofish'."""
        return self.kdbx.header.value.dynamic_header.cipher_id.data

    @property
    def kdf_algorithm(
        self,
    ) -> Union[None, Literal["aeskdf"], Literal["argon2"], Literal["argon2id"]]:
        """`str`: key derivation algorithm used by database during decryption.
        Can be one of 'aeskdf', 'argon2', or 'argon2id'"""
        if self.version == (3, 1):
            return "aeskdf"
        elif self.version == (4, 0):
            kdf_parameters = (
                self.kdbx.header.value.dynamic_header.kdf_parameters.data.dict
            )
            if kdf_parameters["$UUID"].value == kdf_uuids["argon2"]:
                return "argon2"
            elif kdf_parameters["$UUID"].value == kdf_uuids["argon2id"]:
                return "argon2id"
            elif kdf_parameters["$UUID"].value == kdf_uuids["aeskdf"]:
                return "aeskdf"

    @property
    def transformed_key(self) -> bytes:
        """`bytes`: transformed key used in database decryption.  May be cached
        and passed to `open` for faster database opening"""
        return self.kdbx.body.transformed_key

    @property
    def database_salt(self) -> bytes:
        """`bytes`: salt of database kdf. This can be used for adding additional
        credentials which are used in extension to current keyfile."""

        if self.version == (3, 1):
            return self.kdbx.header.value.dynamic_header.transform_seed.data

        kdf_parameters = self.kdbx.header.value.dynamic_header.kdf_parameters.data.dict
        return kdf_parameters["S"].value

    @property
    def payload(self) -> Context:
        """`construct.Container`: Encrypted payload of keepass database"""

        # check if payload is decrypted
        if self.kdbx.body.payload is None:
            raise ValueError("Database is not decrypted")
        else:
            return self.kdbx.body.payload

    @property
    def tree(self) -> ElementTree:
        """`lxml.etree._ElementTree`: database XML payload"""
        return self.payload.xml

    @property
    def root_group(self) -> Group | None:
        """`Group`: root Group of database"""
        return self.find_groups(path="", first=True)

    @property
    def recyclebin_group(self) -> Group | None:
        """`Group`: RecycleBin Group of database"""
        elem = self._xpath("/KeePassFile/Meta/RecycleBinUUID", first=True)
        if elem is None or elem.text is None:
            return None
        recyclebin_uuid = uuid.UUID(bytes=base64.b64decode(elem.text))
        return self.find_groups(uuid=recyclebin_uuid, first=True)

    @property
    def groups(self) -> list[Group]:
        """`list` of `Group`: all groups in database"""
        return self.find_groups()

    @property
    def entries(self) -> list[Entry]:
        """`list` of `Entry`: all entries in database,
        excluding history"""
        return self.find_entries()

    @property
    def database_name(self) -> str | None:
        """`str`: Name of database"""
        elem = self._xpath("/KeePassFile/Meta/DatabaseName", first=True)
        return elem.text if elem is not None else None

    @database_name.setter
    def database_name(self, name: str) -> None:
        item = self._xpath("/KeePassFile/Meta/DatabaseName", first=True)
        if item is not None:
            item.text = str(name)

    @property
    def database_description(self) -> str | None:
        """`str`: Description of the database"""
        elem = self._xpath("/KeePassFile/Meta/DatabaseDescription", first=True)
        return elem.text if elem is not None else None

    @database_description.setter
    def database_description(self, name: str) -> None:
        item = self._xpath("/KeePassFile/Meta/DatabaseDescription", first=True)
        if item is not None:
            item.text = str(name)

    @property
    def default_username(self) -> str | None:
        """`str` or `None`: default user.  `None` if not set"""
        elem = self._xpath("/KeePassFile/Meta/DefaultUserName", first=True)
        return elem.text if elem is not None else None

    @default_username.setter
    def default_username(self, name: str) -> None:
        item = self._xpath("/KeePassFile/Meta/DefaultUserName", first=True)
        if item is not None:
            item.text = str(name)

    def xml(self) -> bytes:
        """Get XML part of database as string

        Returns:
            `str`: XML content of database
        """
        return etree.tostring(  # pyright: ignore[reportUnknownVariableType, reportCallIssue]
            self.tree,  # pyright: ignore[reportArgumentType]
            pretty_print=True,
            standalone=True,
            encoding="utf-8",
        )

    def dump_xml(self, filename: FilenameType) -> None:
        """Dump the contents of the database to file as XML

        Args:
            filename (`str`): path to output file
        """
        with open(filename, "wb") as f:
            f.write(self.xml())

    @overload
    def xpath(
        self,
        xpath_str: str,
        tree: Any = None,
        *,
        first: Literal[True],
        cast: bool = False,
        **kwargs: Any,
    ) -> Xpath_Result | None: ...

    @overload
    def xpath(
        self,
        xpath_str: str,
        tree: Any = None,
        *,
        first: Literal[False] = False,
        cast: bool = False,
        **kwargs: Any,
    ) -> list[Xpath_Result]: ...

    def xpath(
        self,
        xpath_str: str,
        tree: Any = None,
        first: bool | None = False,
        cast: bool = False,
        **kwargs: Any,
    ) -> list[Xpath_Result] | Xpath_Result | None:
        """Look up elements in the XML payload and return corresponding object.

        Internal function which searches the payload lxml ElementTree for
        elements via XPath.  Matched entry, group, and attachment elements are
        automatically cast to their corresponding objects, otherwise an error
        is raised.

        Args:
            xpath_str (`str`): XPath query for finding element(s)
            tree (`_ElementTree`, `Element`, optional): use this
                element as root node when searching
            first (`bool`): If True, function returns first result or None.  If
                False, function returns list of matches or empty list.
                    (default `False`).
            cast (`bool`): If True, matches are instead instantiated as
                pykeepass Group, Entry, or Attachment objects.  An exception
                is raised if a match cannot be cast.  (default `False`)

        Returns:
            `list` of `Group`, `Entry`, `Attachment`, or `lxml.etree.Element`
        """

        if tree is None:
            tree = self.tree
        logger.debug("xpath query: " + xpath_str)
        elements = tree.xpath(
            xpath_str, namespaces={"re": "http://exslt.org/regular-expressions"}
        )

        res: list[Union[Group, Entry, Attachment, Element]] = []
        for e in elements:
            if cast:
                if e.tag == "Entry":
                    res.append(Entry(element=e, kp=self))
                elif e.tag == "Group":
                    res.append(Group(element=e, kp=self))
                elif e.tag == "Binary" and e.getparent().tag == "Entry":
                    res.append(Attachment(element=e, kp=self))
                else:
                    raise Exception("Could not cast element {}".format(e))
            else:
                res.append(e)

        # return first object in list or None
        if first:
            return res[0] if res else None
        return res

    _xpath = xpath

    @overload
    def _find(
        self,
        prefix: str,
        keys_xp: dict[bool, dict[str, str]],
        path: list[str] | str | None = None,
        tree: Any = None,
        *,
        first: Literal[True],
        history: bool = False,
        regex: bool = False,
        flags: str | None = None,
        **kwargs: Any,
    ) -> Xpath_Result | None: ...

    @overload
    def _find(
        self,
        prefix: str,
        keys_xp: dict[bool, dict[str, str]],
        path: list[str] | str | None = None,
        tree: Any = None,
        *,
        first: Literal[False] = False,
        history: bool = False,
        regex: bool = False,
        flags: str | None = None,
        **kwargs: Any,
    ) -> list[Xpath_Result]: ...

    def _find(
        self,
        prefix: str,
        keys_xp: dict[bool, dict[str, str]],
        path: list[str] | str | None = None,
        tree: "Group | None" = None,
        first: bool = False,
        history: bool = False,
        regex: bool = False,
        flags: str | None = None,
        **kwargs: Any,
    ) -> list[Xpath_Result] | Xpath_Result | None:
        """Internal function for converting a search into an XPath string"""

        xp = ""

        if not history:
            prefix += "[not(ancestor::History)]"

        if path is not None:
            first = True

            xp += "/KeePassFile/Root/Group"
            # split provided path into group and element
            group_path = path[:-1]
            element = path[-1] if len(path) > 0 else ""
            # build xpath from group_path and element
            for group in group_path:
                xp += path_xp[regex]["group"].format(group, flags=flags)
            if "Entry" in prefix:
                xp += path_xp[regex]["entry"].format(element, flags=flags)
            elif element and "Group" in prefix:
                xp += path_xp[regex]["group"].format(element, flags=flags)

        else:
            if tree is not None:
                xp += "."

            xp += prefix

            # handle searching custom string fields
            if "string" in kwargs:
                for key, value in kwargs["string"].items():
                    xp += keys_xp[regex]["string"].format(key, value, flags=flags)

                kwargs.pop("string")

            # convert uuid to base64 form before building xpath
            if "uuid" in kwargs:
                kwargs["uuid"] = base64.b64encode(kwargs["uuid"].bytes).decode("utf-8")

            # convert tags to semicolon separated string before building xpath
            # FIXME: this isn't a reliable way to search tags.  e.g. searching ['tag1', 'tag2'] will match 'tag1tag2
            if "tags" in kwargs:
                kwargs["tags"] = " and ".join(
                    f'contains(text(),"{t}")' for t in kwargs["tags"]
                )

            # build xpath to filter results with specified attributes
            for key, value in kwargs.items():
                if key not in keys_xp[regex]:
                    raise TypeError('Invalid keyword argument "{}"'.format(key))
                if value is not None:
                    xp += keys_xp[regex][key].format(value, flags=flags)

        return self._xpath(
            xp,
            tree=tree._element if tree else None,  # pyright: ignore[reportPrivateUsage]
            first=first,
            cast=True,
            **kwargs,
        )

    def _can_be_moved_to_recyclebin(self, entry_or_group: "Group | Entry") -> bool:
        if entry_or_group == self.root_group:
            return False
        recyclebin_group = self.recyclebin_group
        if recyclebin_group is None:
            return True
        uuid_str = base64.b64encode(entry_or_group.uuid.bytes).decode("utf-8")
        elem = self._xpath(
            './UUID[text()="{}"]/..'.format(uuid_str),
            tree=recyclebin_group._element,  # pyright: ignore[reportPrivateUsage]
            first=True,
            cast=False,
        )
        return elem is None

    # ---------- Groups ----------

    from .deprecated import (
        find_groups_by_name,
        find_groups_by_notes,
        find_groups_by_path,
        find_groups_by_uuid,
    )

    @overload
    def find_groups(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        group: "Group | None" = None,
        *,
        first: Literal[True],
        **kwargs: Any,
    ) -> Group | None: ...
    @overload
    def find_groups(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        group: "Group | None" = None,
        *,
        first: Literal[False] = False,
        **kwargs: Any,
    ) -> list[Group]: ...
    def find_groups(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        group: "Group | None" = None,
        **kwargs: Any,
    ) -> list[Group] | Group | None:
        """Find groups in a database

        [XSLT style]: https://www.xml.com/pub/a/2003/06/04/tr.html
        [flags]: https://www.w3.org/TR/xpath-functions/#flags

        Args:
            name (`str`): name of group
            first (`bool`): return first result instead of list (default `False`)
            recursive (`bool`): do a recursive search of all groups/subgroups
            path (`list` of `str`): do group search starting from path
            group (`Group`): search underneath group
            uuid (`uuid.UUID`): group UUID
            regex (`bool`): whether `str` search arguments contain [XSLT style][XSLT style] regular expression
            flags (`str`): XPath [flags][flags]

        The `path` list is a full path to a group (ex. `['foobar_group', 'sub_group']`).  This implies `first=True`.  All other arguments are ignored when this is given.  This is useful for handling user input.

        The `group` argument determines what `Group` to search under, and the `recursive` boolean controls whether to search recursively.

        The `first` (default `False`) boolean controls whether to return the first matched item, or a list of matched items.

        - if `first=False`, the function returns a list of `Group` or `[]` if there are no matches
        - if `first=True`, the function returns the first `Group` match, or `None` if there are no matches

        Returns:
            `list` of `Group` if `first=False`
            or (`Group` or `None`) if `first=True`

        Examples:
        ``` python
        >>> kp.find_groups(name='foo', first=True)
        Group: "foo"

        >>> kp.find_groups(name='foo.*', regex=True)
        [Group: "foo", Group "foobar"]

        >>> kp.find_groups(path=['social'], regex=True)
        [Group: "social", Group: "social/foo_subgroup"]

        >>> kp.find_groups(name='social', first=True).subgroups
        [Group: "social/foo_subgroup"]
        ```
        """

        prefix = "//Group" if recursive else "/Group"
        return self._find(
            prefix,
            group_xp,
            path=path,
            tree=group,
            **kwargs,
        )  # pyright: ignore[reportUnknownVariableType]

    def add_group(
        self,
        destination_group: "Group",
        group_name: str,
        icon: str | None = None,
        notes: str | None = None,
    ) -> "Group":
        """Create a new group and all parent groups, if necessary

        Args:
            destination_group (`Group`): parent group to add a new group to
            group_name (`str`): name of new group
            icon (`str`): icon name from `icons`
            notes (`str`): group notes

        Returns:
            `Group`: newly added group
        """
        logger.debug("Creating group {}".format(group_name))

        if icon:
            group = Group(name=group_name, icon=icon, notes=notes, kp=self)
        else:
            group = Group(name=group_name, notes=notes, kp=self)
        destination_group.append(group)

        return group

    def delete_group(self, group: "Group") -> None:
        group.delete()

    def move_group(self, group: "Group", destination_group: "Group") -> None:
        """Move a group"""
        destination_group.append(group)

    def _create_or_get_recyclebin_group(self, **kwargs: Any) -> "Group":
        existing_group = self.recyclebin_group
        if existing_group is not None:
            return existing_group
        kwargs.setdefault("group_name", "Recycle Bin")
        root = cast(Group, self.root_group)
        group = self.add_group(root, **kwargs)
        elem = self._xpath("/KeePassFile/Meta/RecycleBinUUID", first=True)
        if elem is not None:
            elem.text = base64.b64encode(group.uuid.bytes).decode("utf-8")
        return group

    def trash_group(self, group: "Group") -> None:
        """Move a group to the RecycleBin

        The recycle bin is created if it does not exit. ``group`` must be an empty Group.

        Args:
            group (`Group`): Group to send to the RecycleBin
        """
        if not self._can_be_moved_to_recyclebin(group):
            raise UnableToSendToRecycleBin
        recyclebin_group = self._create_or_get_recyclebin_group()
        self.move_group(group, recyclebin_group)

    def empty_group(self, group: "Group") -> None:
        """Delete all entries and subgroups of a group.

        This does not delete the group itself

        Args:
            group (`Group`): Group to empty
        """
        while len(group.subgroups):
            self.delete_group(group.subgroups[0])
        while len(group.entries):
            self.delete_entry(group.entries[0])

    # ---------- Entries ----------

    from .deprecated import (
        find_entries_by_notes,
        find_entries_by_password,
        find_entries_by_path,
        find_entries_by_string,
        find_entries_by_title,
        find_entries_by_url,
        find_entries_by_username,
        find_entries_by_uuid,
    )

    @overload
    def find_entries(
        self,
        recursive: bool = True,
        path: list[str] | None = None,
        group: "Group | None" = None,
        *,
        first: Literal[True],
        **kwargs: Any,
    ) -> Entry | None: ...
    @overload
    def find_entries(
        self,
        recursive: bool = True,
        path: list[str] | None = None,
        group: "Group | None" = None,
        *,
        first: Literal[False] = False,
        **kwargs: Any,
    ) -> list[Entry]: ...
    def find_entries(
        self,
        recursive: bool = True,
        path: list[str] | None = None,
        group: "Group | None" = None,
        **kwargs: Any,
    ) -> list[Entry] | Entry | None:
        """Returns entries which match all provided parameters
        Args:
            path (`list` of (`str` or `None`), optional): full path to an entry
                (eg. `['foobar_group', 'foobar_entry']`).  This implies `first=True`.
                All other arguments are ignored when this is given.  This is useful for
                handling user input.
            title (`str`, optional): title of entry to find
            username (`str`, optional): username of entry to find
            password (`str`, optional): password of entry to find
            url (`str`, optional): url of entry to find
            notes (`str`, optional): notes of entry to find
            otp (`str`, optional): otp string of entry to find
            string (`dict`): custom string fields.
                (eg. `{'custom_field1': 'custom value', 'custom_field2': 'custom value'}`)
            uuid (`uuid.UUID`): entry UUID
            tags (`list` of `str`): entry tags
            autotype_enabled (`bool`, optional): autotype string is enabled
            autotype_sequence (`str`, optional): autotype string
            autotype_window (`str`, optional): autotype target window filter string
            group (`Group` or `None`, optional): search under this group
            first (`bool`, optional): return first match or `None` if no matches.
                Otherwise return list of `Entry` matches. (default `False`)
            history (`bool`): include history entries in results. (default `False`)
            recursive (`bool`): search recursively
            regex (`bool`): interpret search strings given above as
                [XSLT style](https://www.xml.com/pub/a/2003/06/04/tr.html) regexes
            flags (`str`): regex [search flags](https://www.w3.org/TR/xpath-functions/#flags)

        Returns:
            `list` of `Entry` if `first=False`
            or (`Entry` or `None`) if `first=True`

        Examples:

        ``` python
        >>> kp.find_entries(title='gmail', first=True)
        Entry: "social/gmail (myusername)"

        >>> kp.find_entries(title='foo.*', regex=True)
        [Entry: "foo_entry (myusername)", Entry: "foobar_entry (myusername)"]

        >>> entry = kp.find_entries(title='foo.*', url='.*facebook.*', regex=True, first=True)
        >>> entry.url
        'facebook.com'
        >>> entry.title
        'foo_entry'
        >>> entry.title = 'hello'

        >>> group = kp.find_group(name='social', first=True)
        >>> kp.find_entries(title='facebook', group=group, recursive=False, first=True)
        Entry: "social/facebook (myusername)"
        ```
        """

        prefix = "//Entry" if recursive else "/Entry"
        return self._find(
            prefix,
            entry_xp,
            path=path,
            tree=group,
            **kwargs,
        )  # pyright: ignore[reportUnknownVariableType]

    def add_entry(
        self,
        destination_group: "Group",
        title: str | None,
        username: str | None,
        password: str | None,
        url: str | None = None,
        notes: str | None = None,
        expiry_time: datetime | None = None,
        tags: list[str] | str | None = None,
        otp: str | None = None,
        icon: str | None = None,
        force_creation: bool = False,
    ) -> "Entry":
        """Create a new entry

        Args:
            destination_group (`Group`): parent group to add a new entry to
            title (`str`, or `None`): title of new entry
            username (`str` or `None`): username of new entry
            password (`str` or `None`): password of new entry
            url (`str` or `None`): URL of new entry
            notes (`str` or `None`): notes of new entry
            expiry_time (`datetime.datetime`): time of entry expiration
            tags (`list` of `str` or `None`): entry tags
            otp (`str` or `None`): OTP code of object
            icon (`str`, optional): icon name from `icons`
            force_creation (`bool`): create entry even if one with identical
                title exists in this group (default `False`)

        If ``expiry_time`` is a naive datetime object
        (i.e. ``expiry_time.tzinfo`` is not set), the timezone is retrieved from
        ``dateutil.tz.gettz()``.


        Returns:
            `Group`: newly added group
        """

        entries = self.find_entries(
            title=title,
            username=username,
            first=True,
            group=destination_group,
            recursive=False,
        )

        if entries and not force_creation:
            raise Exception(
                'An entry "{}" already exists in "{}"'.format(title, destination_group)
            )
        else:
            logger.debug("Creating a new entry")
            entry = Entry(
                title=title,
                username=username,
                password=password,
                notes=notes,
                otp=otp,
                url=url,
                tags=tags,
                expires=True if expiry_time else False,
                expiry_time=expiry_time,
                icon=icon,
                kp=self,
            )
            destination_group.append(entry)

        return entry

    def delete_entry(self, entry: "Entry") -> None:
        """Delete entry

        Args:
            entry (`Entry`): entry to delete
        """
        entry.delete()

    def move_entry(self, entry: "Entry", destination_group: "Group") -> None:
        """Move entry to group

        Args:
            entry (`Entry`): entry to move
            destination_group (`Group`): group to move to
        """
        destination_group.append(entry)

    def trash_entry(self, entry: "Entry") -> None:
        """Move an entry to the RecycleBin

        The recycle bin is created if it does not exit.

        Args:
            entry (`Entry`): Entry to send to the RecycleBin
        """
        if not self._can_be_moved_to_recyclebin(entry):
            raise UnableToSendToRecycleBin
        recyclebin_group = self._create_or_get_recyclebin_group()
        self.move_entry(entry, recyclebin_group)

    # ---------- Attachments ----------

    @overload
    def find_attachments(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        element: "Entry | None" = None,
        *,
        first: Literal[True],
        **kwargs: Any,
    ) -> Attachment | None: ...
    @overload
    def find_attachments(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        element: "Entry | None" = None,
        *,
        first: Literal[False] = False,
        **kwargs: Any,
    ) -> list[Attachment]: ...
    def find_attachments(
        self,
        recursive: bool = True,
        path: list[str] | str | None = None,
        element: "Entry | None" = None,
        **kwargs: Any,
    ) -> list[Attachment] | Attachment | None:
        """Find attachments in database

        Args:
            id (`int` or `None`): attachment ID to match
            filename (`str` or `None`): filename to match
            element (`Entry` or `Group` or `None`): entry or group to search under
            recursive (`bool`): search recursively (default `True`)
            regex (`bool`): whether `str` search arguments contain [XSLT style][XSLT style] regular expression
            flags (`str`): XPath [flags][flags]
            history (`bool`): search under history entries. (default `False`)
            first (`bool`): If True, function returns first result or None.  If
                False, function returns list of matches or empty list.  (default
                `False`).
        """

        prefix = "//Binary" if recursive else "/Binary"
        return self._find(
            prefix,
            attachment_xp,
            path=path,
            tree=element,
            **kwargs,
        )  # pyright: ignore[reportUnknownVariableType]

    @property
    def attachments(self) -> list[Attachment]:
        """`list` of `Attachment`: all attachments in database"""
        return self.find_attachments(filename=".*", regex=True)

    @property
    def binaries(self) -> list[bytes]:
        """`list` of `bytes`: all attachment binaries in database.  The position
        within this list indicates the binary's ID"""
        if self.version >= (4, 0):
            # first byte is a prepended flag
            binaries = [a.data[1:] for a in self.payload.inner_header.binary]
        else:
            binaries: list[bytes] = []
            for elem in self._xpath("/KeePassFile/Meta/Binaries/Binary"):
                elem = cast(Element, elem)
                if elem.text is not None:
                    if elem.get("Compressed") == "True":
                        data = zlib.decompress(
                            base64.b64decode(elem.text), zlib.MAX_WBITS | 32
                        )
                    else:
                        data = base64.b64decode(elem.text)
                else:
                    data = b""
                binaries.insert(int(elem.attrib["ID"]), data)

        return binaries

    def add_binary(
        self, data: bytes, compressed: bool = True, protected: bool = True
    ) -> int:
        """Add binary data to database.  Note this does not create an attachment (see `Entry.add_attachment`)

        Args:
            data (`bytes`): binary data
            compressed (`bool`): whether binary data should be compressed.
                (default `True`).  Applies only to KDBX3
            protected (`bool`): whether protected flag should be set.  (default `True`).  Note
                Applies only to KDBX4

        Returns:
            id (`int`): ID of binary in database
        """
        if self.version >= (4, 0):
            # add protected flag byte
            data = b"\x01" + data if protected else b"\x00" + data
            # add binary element to inner header
            c = Container(type="binary", data=data)
            self.payload.inner_header.binary.append(c)
        else:
            binaries = self._xpath("/KeePassFile/Meta/Binaries", first=True)
            if binaries is not None:
                binaries = cast(Element, binaries)
                if compressed:
                    # gzip compression
                    compressor = zlib.compressobj(
                        zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, zlib.MAX_WBITS | 16
                    )
                    data = compressor.compress(data)
                    data += compressor.flush()
                data_str = base64.b64encode(data).decode()

                # set ID for Binary Element
                binary_id = len(self.binaries)

                # add binary element to XML
                binaries.append(
                    cast(
                        Any,
                        E.Binary(
                            data_str, ID=str(binary_id), Compressed=str(compressed)
                        ),
                    )
                )

        # return binary id
        return len(self.binaries) - 1

    def delete_binary(self, id: int) -> None:
        """Remove a binary from database and deletes attachments that reference it

        Since attachments reference binaries by their positional index,
        attachments that reference binaries with ID > `id` will automatically be decremented

        Args:
            id (`int`): ID of binary to remove

        Raises:
            `IndexError`: raised when binary with given ID does not exist
        """
        try:
            if self.version >= (4, 0):
                # remove binary element from inner header
                self.payload.inner_header.binary.pop(id)
            else:
                # remove binary element from XML
                binaries = self._xpath("/KeePassFile/Meta/Binaries", first=True)
                if binaries is not None:
                    binaries = cast(Element, binaries)
                    binaries.remove(list(binaries)[id])
                else:
                    raise IndexError()
        except IndexError:
            raise BinaryError("No such binary with id {}".format(id))

        # remove all entry references to this attachment
        for reference in self.find_attachments(id=id):
            reference.delete()

        # decrement references greater than this id
        binaries_gt = cast(
            list[Attachment],
            self._xpath('//Binary/Value[@Ref > "{}"]/..'.format(id), cast=True),
        )
        for reference in binaries_gt:
            reference.id = reference.id - 1

    # ---------- Misc ----------

    def deref(self, value: str) -> str | None:
        """Dereference [field reference][fieldref] of Entry

        Args:
            value (`str`): KeePass reference string to another field

        Returns:
            `str`, `uuid.UUID` or `None` if no match found

        [fieldref]: https://keepass.info/help/base/fieldrefs.html
        """
        if not value:
            return value
        references = set(re.findall(r"({REF:([TUPANI])@([TUPANI]):([^}]+)})", value))
        if not references:
            return value
        field_to_attribute = {
            "T": "title",
            "U": "username",
            "P": "password",
            "A": "url",
            "N": "notes",
            "I": "uuid",
        }
        for ref, wanted_field, search_in, search_value in references:
            wanted_field = field_to_attribute[wanted_field]
            search_in = field_to_attribute[search_in]
            if search_in == "uuid":
                search_value = uuid.UUID(search_value)
            kwargs: Any = {search_in: search_value}
            ref_entry = self.find_entries(first=True, **kwargs)
            if ref_entry is None:
                return None
            value = value.replace(ref, getattr(ref_entry, wanted_field))
        return self.deref(value)

    # ---------- Credential Changing and Expiry ----------

    @property
    def password(self) -> str | None:
        """`str` or `None`: Get or set database password"""
        return self._password

    @password.setter
    def password(self, password: str | None) -> None:
        self._password = password
        self.credchange_date = datetime.now(timezone.utc)

    @property
    def keyfile(self) -> FilenameType | None:
        """`str` or `pathlib.Path` or `None`: get or set database keyfile"""
        return self._keyfile

    @keyfile.setter
    def keyfile(self, keyfile: FilenameType | None) -> None:
        self._keyfile = keyfile
        self.credchange_date = datetime.now(timezone.utc)

    @property
    def credchange_required_days(self) -> int | None:
        """`int`: Days until password update should be required"""
        e = self._xpath("/KeePassFile/Meta/MasterKeyChangeForce", first=True)
        if e is not None:
            return int(e.text)  # pyright: ignore[reportArgumentType]

    @property
    def credchange_recommended_days(self) -> int | None:
        """`int`: Days until password update should be recommended"""
        e = self._xpath("/KeePassFile/Meta/MasterKeyChangeRec", first=True)
        if e is not None:
            return int(e.text)  # pyright: ignore[reportArgumentType]

    @credchange_required_days.setter
    def credchange_required_days(self, days: int) -> None:
        path = "/KeePassFile/Meta/MasterKeyChangeForce"
        item = self._xpath(path, first=True)
        if item is not None:
            item.text = str(days)

    @credchange_recommended_days.setter
    def credchange_recommended_days(self, days: int) -> None:
        path = "/KeePassFile/Meta/MasterKeyChangeRec"
        item = self._xpath(path, first=True)
        if item is not None:
            item.text = str(days)

    @property
    def credchange_date(self) -> datetime | None:
        """`datetime.datetime`: get or set UTC time of last credential change"""
        e = self._xpath("/KeePassFile/Meta/MasterKeyChanged", first=True)
        if e is not None:
            return self._decode_time(e.text)  # pyright: ignore[reportArgumentType]

    @credchange_date.setter
    def credchange_date(self, date: datetime) -> None:
        mk_time = self._xpath("/KeePassFile/Meta/MasterKeyChanged", first=True)
        if mk_time is not None:
            mk_time.text = self._encode_time(date)

    @property
    def credchange_required(self) -> bool:
        """`bool`: Check if credential change is required"""
        change_date = self.credchange_date
        required_days = self.credchange_required_days
        if change_date is None or required_days is None or required_days == -1:
            return False
        now_date = datetime.now(timezone.utc)
        return (now_date - change_date).days > required_days

    @property
    def credchange_recommended(self) -> bool:
        """`bool`: Check if credential change is recommended"""
        change_date = self.credchange_date
        recommended_days = self.credchange_recommended_days
        if change_date is None or recommended_days is None or recommended_days == -1:
            return False
        now_date = datetime.now(timezone.utc)
        return (now_date - change_date).days > recommended_days

    # ---------- Datetime Functions ----------

    def _encode_time(self, value: datetime) -> str:
        """`bytes` or `str`: Convert datetime to base64 or plaintext string"""

        if self.version >= (4, 0):
            diff_seconds = int(
                (
                    value - datetime(year=1, month=1, day=1, tzinfo=timezone.utc)
                ).total_seconds()
            )
            return base64.b64encode(struct.pack("<Q", diff_seconds)).decode("utf-8")
        else:
            return value.isoformat()

    def _decode_time(self, text: str) -> datetime:
        """`datetime.datetime`: Convert base64 time or plaintext time to datetime"""

        if self.version >= (4, 0):
            # decode KDBX4 date from b64 format
            try:
                return datetime(
                    year=1, month=1, day=1, tzinfo=timezone.utc
                ) + timedelta(seconds=struct.unpack("<Q", base64.b64decode(text))[0])
            except BinasciiError:
                return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(
                    tzinfo=timezone.utc
                )
        else:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(
                tzinfo=timezone.utc
            )


def create_database(
    filename: FilenameType | StreamType,
    password: str | None = None,
    keyfile: FilenameType | None = None,
    transformed_key: bytes | None = None,
) -> PyKeePass:
    """
    Create a new database at ``filename`` with supplied credentials.

    Args:
        filename (`str`, optional): path to database or stream object.
            If None, the path given when the database was opened is used.
        password (`str`, optional): database password.  If None,
            database is assumed to have no password
        keyfile (`str`, optional): path to keyfile.  If None,
            database is assumed to have no keyfile
        transformed_key (`bytes`, optional): precomputed transformed
            key.

    Returns:
        `PyKeePass`
    """
    keepass_instance = PyKeePass(BLANK_DATABASE_LOCATION, BLANK_DATABASE_PASSWORD)

    keepass_instance.filename = filename
    keepass_instance.password = password
    keepass_instance.keyfile = keyfile

    keepass_instance.save(transformed_key=transformed_key)
    return keepass_instance


def debug_setup() -> None:
    """Convenience function to quickly enable debug messages"""

    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
