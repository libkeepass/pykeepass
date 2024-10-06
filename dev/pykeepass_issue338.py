#!/usr/bin/env python3

import sys
from pykeepass import PyKeePass


def print_entries_tags(entries):
    for entry in entries:
        print(f"title={entry.title}")
        print(f"username={entry.username}")
        print(f"password={entry.password}")
        print(f"tags ({len(entry.tags or [])})")
        for tag in (entry.tags or []):
            print(f"{tag}")


xc = PyKeePass(filename="test_keepassxc.kdbx", password="test")
print("Database from KeepassXC ==========")
print_entries_tags(xc.entries)

print("Database from Keepass ==========")
kp = PyKeePass(filename="test_keepass.kdbx", password="test");
print_entries_tags(kp.entries)


