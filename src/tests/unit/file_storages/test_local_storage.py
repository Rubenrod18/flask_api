import os

import pytest
from flask import current_app

from app.exceptions import FileEmptyError
from app.file_storages import LocalStorage


@pytest.fixture
def setup(tmp_path):
    local_storage = LocalStorage()
    file_path = tmp_path / 'tempfile'

    yield local_storage, file_path


class TestLocalStorage:
    def test_save_bytes_creates_file_and_returns_true(self, setup):
        local_storage, file_path = setup
        content = b'hello'

        assert local_storage.save_bytes(content, file_path, override=True)
        with open(file_path, 'rb') as f:
            assert f.read() == content

    def test_save_bytes_raises_if_file_exists_and_no_override(self, setup):
        local_storage, file_path = setup

        with open(file_path, 'wb') as f:
            f.write(b'data')

        with pytest.raises(FileExistsError):
            local_storage.save_bytes(b'other', file_path, override=False)

    def test_save_bytes_raises_empty_file_and_removes(self, setup):
        local_storage, file_path = setup

        with pytest.raises(FileEmptyError):
            local_storage.save_bytes(b'', file_path, override=True)

        assert not os.path.exists(file_path)

    def test_copy_file(self, setup):
        local_storage, file_path = setup

        src = str(file_path)
        dst = str(file_path) + '_copy'
        with open(src, 'wb') as f:
            f.write(b'abc')
        local_storage.copy_file(src, dst)

        with open(dst, 'rb') as f:
            assert f.read() == b'abc'
        os.remove(dst)

    def test_get_filesize(self, setup):
        local_storage, file_path = setup

        with open(file_path, 'wb') as f:
            f.write(b'12345')

        assert local_storage.get_filesize(file_path) == 5

    def test_get_basename(self, app, setup):
        local_storage, file_path = setup

        assert local_storage.get_basename('/tmp/myfile.txt') == 'myfile'
        assert local_storage.get_basename(f'{current_app.config["ROOT_DIRECTORY"]}/src/config.py') == 'config'

    def test_rename(self, setup):
        local_storage, file_path = setup

        new_name = str(file_path) + '_renamed'
        with open(file_path, 'wb') as f:
            f.write(b'data')

        local_storage.rename(file_path, new_name)
        assert os.path.exists(new_name)

        with open(new_name, 'rb') as f:
            assert f.read() == b'data'

        os.remove(new_name)

    def test_delete_file(self, setup):
        local_storage, file_path = setup

        with open(file_path, 'wb') as f:
            f.write(b'x')
        local_storage.delete_file(file_path)

        assert not os.path.exists(file_path)
