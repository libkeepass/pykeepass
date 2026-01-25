"""
.. include:: ../README.md
"""

from __future__ import annotations

from .attachment import Attachment
from .entry import Entry
from .group import Group
from .icons import icons
from .pykeepass import PyKeePass, create_database
from .version import __version__

__all__ = [
    "__version__",
    "PyKeePass",
    "Entry",
    "Group",
    "Attachment",
    "icons",
    "create_database",
]
