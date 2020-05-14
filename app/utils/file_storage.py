import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class FileStorage():
    def save_bytes(self, file_content: bytes, filename: str, override: bool = False):
        try:
            if not override and os.path.exists(filename):
                raise FileExistsError(f'The file {filename} already exists!')
            else:
                with open(filename, 'wb') as f:
                    f.write(file_content)

                filesize = self.get_filesize(filename)
                if filesize == 0:
                    raise Exception(f'The file {filename} was created empty')

                return True
        except Exception as e:
            logger.debug(e)
            if not isinstance(e, FileExistsError):
                if os.path.exists(filename):
                    os.remove(filename)
            raise e

    @staticmethod
    def get_filesize(filename: str) -> int:
        p = Path(filename)
        return p.stat().st_size