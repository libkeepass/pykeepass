from __future__ import unicode_literals
import unittest
from os.path import dirname, realpath, join
from tempfile import TemporaryFile

BASE_DIR = dirname(realpath(__file__))
DATABASES = {
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


class ReadTestCase(unittest.TestCase):

    def test_magic_strings(self):
        """Test whether magic strings are present in global package import."""
        from pykeepass import RAW_BYTES, BYTE_STREAM
        self.assertTrue(RAW_BYTES)
        self.assertTrue(BYTE_STREAM)

    def test_raw_bytes(self):
        """Test if can read all KDBX files as raw bytes."""
        from pykeepass.pykeepass import PyKeePass, RAW_BYTES

        for name, kdbx in DATABASES.items():
            with open(kdbx["filename"], "rb") as stream:
                raw_bytes = stream.read()

            obj = PyKeePass(
                RAW_BYTES, password=kdbx["password"],
                keyfile=kdbx["keyfile"], raw_bytes=raw_bytes
            )
            self.assertEqual(len(obj.entries), kdbx["total_entries"])

    def test_stream(self):
        """Test if can read all KDBX files from stream."""
        from pykeepass import PyKeePass, BYTE_STREAM
        for name, kdbx in DATABASES.items():
            with open(kdbx["filename"], "rb") as stream:

                obj = PyKeePass(
                    BYTE_STREAM, password=kdbx["password"],
                    keyfile=kdbx["keyfile"], stream=stream
                )
                self.assertEqual(len(obj.entries), kdbx["total_entries"])


class WriteTestCase(unittest.TestCase):
    def test_raw_bytes(self):
        """Test if can write all KDBX files as raw bytes."""
        from pykeepass.pykeepass import PyKeePass, RAW_BYTES

        for name, kdbx in DATABASES.items():
            with open(kdbx["filename"], "rb") as stream:
                raw_bytes = stream.read()

            obj = PyKeePass(
                RAW_BYTES, password=kdbx["password"],
                keyfile=kdbx["keyfile"], raw_bytes=raw_bytes
            )
            self.assertEqual(len(obj.entries), kdbx["total_entries"])

            data = obj.save(RAW_BYTES)

            obj = PyKeePass(
                RAW_BYTES, password=kdbx["password"],
                keyfile=kdbx["keyfile"], raw_bytes=data
            )
            self.assertEqual(len(obj.entries), kdbx["total_entries"])

    def test_stream(self):
        """Test if can write all KDBX files to stream."""
        from pykeepass import PyKeePass, BYTE_STREAM
        for name, kdbx in DATABASES.items():
            with open(kdbx["filename"], "rb") as stream:

                obj = PyKeePass(
                    BYTE_STREAM, password=kdbx["password"],
                    keyfile=kdbx["keyfile"], stream=stream
                )
                self.assertEqual(len(obj.entries), kdbx["total_entries"])

            with TemporaryFile() as temp:
                temp.seek(0)
                obj.save(BYTE_STREAM, stream=temp)

                temp.seek(0)
                obj = PyKeePass(
                    BYTE_STREAM, password=kdbx["password"],
                    keyfile=kdbx["keyfile"], stream=temp
                )
                self.assertEqual(len(obj.entries), kdbx["total_entries"])


class CreateTestCase(unittest.TestCase):
    def db_check(self, kdbx):
        self.assertEqual(len(kdbx.entries), 0)
        self.assertEqual(len(kdbx.groups), 1)
        self.assertEqual(kdbx.groups[0].name, "Root")

    def test_raw_bytes(self):
        """Test if can create a KDBX file as raw bytes."""
        from pykeepass.pykeepass import PyKeePass, RAW_BYTES, create_database

        obj, data = create_database(RAW_BYTES, password="pass")
        self.db_check(obj)

        obj = PyKeePass(RAW_BYTES, password="pass", raw_bytes=data)
        self.db_check(obj)

    def test_stream(self):
        """Test if can create a KDBX file to stream."""
        from pykeepass.pykeepass import PyKeePass, BYTE_STREAM, create_database

        with TemporaryFile() as temp:
            temp.seek(0)
            obj = create_database(BYTE_STREAM, password="pass", stream=temp)
            self.db_check(obj)

            temp.seek(0)
            obj = PyKeePass(BYTE_STREAM, password="pass", stream=temp)
            self.db_check(obj)


if __name__ == '__main__':
    unittest.main()
