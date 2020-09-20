import logging
import os
from pathlib import Path
from shutil import copyfile

from app.utils import FileEmptyError

logger = logging.getLogger(__name__)


class FileStorage:
    def save_bytes(self, file_content: bytes, filename: str,
                   override: bool = False):
        try:
            if not override and os.path.exists(filename):
                raise FileExistsError(f'The file {filename} already exists!')
            else:
                with open(filename, 'wb') as f:
                    f.write(file_content)

                filesize = self.get_filesize(filename)
                if filesize == 0:
                    raise FileEmptyError(
                        f'The file {filename} was created empty'
                    )

                return True
        except Exception as e:
            logger.debug(e)
            if not isinstance(e, FileExistsError):
                if os.path.exists(filename):
                    os.remove(filename)
            raise e

    @staticmethod
    def copy_file(src: str, dst: str) -> None:
        copyfile(src, dst)

    @staticmethod
    def get_filesize(filename: str) -> int:
        p = Path(filename)
        return p.stat().st_size

    @staticmethod
    def get_basename(filename: str, include_path: bool = False) -> str:
        if include_path:
            basename = os.path.splitext(filename)[0]
        else:
            basename = os.path.splitext(os.path.basename(filename))[0]

        return basename

    @staticmethod
    def rename(src: str, dst: str) -> None:
        os.rename(src, dst)
