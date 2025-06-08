import os
import tempfile

from app.exceptions import FileEmptyError
from app.file_storages import LocalStorage
from tests.base.base_test import BaseTest


class TestLocalStorage(BaseTest):
    def setUp(self):
        super().setUp()
        self.local_storage = LocalStorage()

        fd, self.file_path = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_save_bytes_creates_file_and_returns_true(self):
        content = b'hello'

        self.assertTrue(self.local_storage.save_bytes(content, self.file_path, override=True))
        with open(self.file_path, 'rb') as f:
            self.assertEqual(f.read(), content)

    def test_save_bytes_raises_if_file_exists_and_no_override(self):
        with open(self.file_path, 'wb') as f:
            f.write(b'data')

        with self.assertRaises(FileExistsError):
            self.local_storage.save_bytes(b'other', self.file_path, override=False)

    def test_save_bytes_raises_empty_file_and_removes(self):
        with self.assertRaises(FileEmptyError):
            self.local_storage.save_bytes(b'', self.file_path, override=True)
        self.assertFalse(os.path.exists(self.file_path))

    def test_copy_file(self):
        src = self.file_path
        dst = self.file_path + '_copy'
        with open(src, 'wb') as f:
            f.write(b'abc')
        self.local_storage.copy_file(src, dst)

        with open(dst, 'rb') as f:
            self.assertEqual(f.read(), b'abc')
        os.remove(dst)

    def test_get_filesize(self):
        with open(self.file_path, 'wb') as f:
            f.write(b'12345')

        self.assertEqual(self.local_storage.get_filesize(self.file_path), 5)

    def test_get_basename(self):
        self.assertEqual(self.local_storage.get_basename('/tmp/myfile.txt'), 'myfile')
        self.assertEqual(
            self.local_storage.get_basename(f'{self.app.config["ROOT_DIRECTORY"]}/src/config.py'), 'config'
        )

    def test_rename(self):
        new_name = self.file_path + '_renamed'
        with open(self.file_path, 'wb') as f:
            f.write(b'data')

        self.local_storage.rename(self.file_path, new_name)
        self.assertTrue(os.path.exists(new_name))

        with open(new_name, 'rb') as f:
            self.assertEqual(f.read(), b'data')

        os.remove(new_name)

    def test_delete_file(self):
        with open(self.file_path, 'wb') as f:
            f.write(b'x')
        self.local_storage.delete_file(self.file_path)

        self.assertFalse(os.path.exists(self.file_path))
