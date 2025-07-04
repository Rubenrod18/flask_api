import os
from shutil import copyfile

from app.exceptions import FileEmptyError

from .base import BaseFileStorage


class LocalStorage(BaseFileStorage):
    def save_bytes(self, file_content: bytes, filename: str, override: bool = False):
        try:
            if not override and os.path.exists(filename):
                raise FileExistsError('The file already exists!')
            else:
                with open(filename, 'wb') as f:
                    f.write(file_content)

                filesize = self.get_filesize(filename)
                if filesize == 0:
                    raise FileEmptyError('The file is empty!')

                return True
        except (FileExistsError, FileEmptyError) as e:
            if not isinstance(e, FileExistsError):
                if os.path.exists(filename):
                    os.remove(filename)
            raise e

    def copy_file(self, src: str, dst: str) -> None:
        copyfile(src, dst)

    def get_filesize(self, filepath: str) -> int:
        return os.path.getsize(filepath)

    def get_basename(self, filename: str) -> str:
        return os.path.splitext(os.path.basename(filename))[0]

    @staticmethod
    def get_filename(filename: str) -> str:
        # HACK: what is the diff between get_basename and get_filename?
        return os.path.basename(filename)

    def rename(self, src: str, dst: str) -> None:
        os.rename(src, dst)

    def delete_file(self, filepath: str) -> None:
        if os.path.exists(filepath):
            os.remove(filepath)
