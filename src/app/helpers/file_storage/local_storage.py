import logging
import os
from shutil import copyfile

from app.exceptions import FileEmptyError
from app.helpers.file_storage.storage_interface import IFileStorage

logger = logging.getLogger(__name__)


class LocalStorage(IFileStorage):
    def save_bytes(self, file_content: bytes, filename: str, override: bool = False):
        try:
            if not override and os.path.exists(filename):
                raise FileExistsError(f'The file {filename} already exists!')
            else:
                with open(filename, 'wb') as f:
                    f.write(file_content)

                filesize = self.get_filesize(filename)
                if filesize == 0:
                    raise FileEmptyError(f'The file {filename} was created empty')

                return True
        except Exception as e:
            logger.debug(e)
            if not isinstance(e, FileExistsError):
                if os.path.exists(filename):
                    os.remove(filename)
            raise e

    def copy_file(self, src: str, dst: str) -> None:
        copyfile(src, dst)

    def get_filesize(self, filepath: str) -> int:
        return os.path.getsize(filepath)

    def get_basename(self, filename: str, include_path: bool = False) -> str:
        if include_path:
            basename = os.path.splitext(filename)[0]
        else:
            basename = os.path.splitext(os.path.basename(filename))[0]

        return basename

    def rename(self, src: str, dst: str) -> None:
        os.rename(src, dst)

    def delete_file(self, filepath: str) -> None:
        if os.path.exists(filepath):
            os.remove(filepath)
