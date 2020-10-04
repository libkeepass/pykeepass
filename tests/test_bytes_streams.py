from __future__ import unicode_literals
import unittest
from os.path import dirname, realpath, join

BASE_DIR = dirname(realpath(__file__))


class ReadTestCase(unittest.TestCase):
    databases = {
        "v3": {
            "filename": join(BASE_DIR, "test3.kdbx"),
            "password": "password",
            "keyfile": join(BASE_DIR, "test3.key"),
            "total_entries": 13
        },
        "v4": {
            "filename": join(BASE_DIR, "test4.kdbx"),
            "password": "password",
            "keyfile": join(BASE_DIR, "test4.key"),
            "total_entries": 13
        }
    }

    def test_magic_strings(self):
        """Test whether magic strings are present in global package import."""
        from pykeepass import RAW_BYTES
        self.assertTrue(RAW_BYTES)

    def test_raw_bytes(self):
        """Test if can read all KDBX files as raw bytes."""
        from pykeepass.pykeepass import PyKeePass, RAW_BYTES

        for name, kdbx in self.databases.items():
            with open(kdbx["filename"], "rb") as stream:
                raw_bytes = stream.read()

            obj = PyKeePass(
                RAW_BYTES, password=kdbx["password"],
                keyfile=kdbx["keyfile"], raw_bytes=raw_bytes
            )
            self.assertEqual(len(obj.entries), kdbx["total_entries"])


if __name__ == '__main__':
    unittest.main()
