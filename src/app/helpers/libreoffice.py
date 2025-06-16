import logging
import os
import re
import subprocess
import sys
import uuid

logger = logging.getLogger(__name__)


def convert_to(folder: str, source: str) -> str:
    logger.debug(f'Folder: {folder}')
    logger.debug(f'Word file: {source}')

    if not os.path.isdir(folder):
        raise FileNotFoundError(f'{source} directory not found')

    if not os.path.isfile(source):
        raise FileNotFoundError(f'{source} file not found')

    args = [
        libreoffice_exec(),
        '--headless',
        # NOTE: This isolates the user profile for LibreOffice to avoid race conditions and file locks
        #       when running multiple instances (e.g., in parallel tests or Celery tasks).
        #       Without this, LibreOffice may fail or hang due to profile conflicts.
        f'-env:UserInstallation=file:///tmp/lo_profile_{uuid.uuid4().hex}',
        '--convert-to',
        'pdf:writer_pdf_Export',
        '--outdir',
        folder,
        source,
    ]

    process = subprocess.run(args, capture_output=True, env={'HOME': os.getenv('HOME')}, check=False)
    logger.debug(f'STDOUT: {process.stdout.decode()}')
    logger.debug(f'STDERR: {process.stderr.decode()}')
    logger.debug(f'RETURNCODE: {process.returncode}')
    filename = re.search('-> (.*?) using filter', process.stdout.decode('utf-8'))

    if filename is None:
        raise LibreOfficeError(
            f'LibreOffice failed.\nSTDOUT:\n{process.stdout.decode()}\nSTDERR:\n{process.stderr.decode()}'
        )
    else:
        return filename.group(1)


def libreoffice_exec() -> str:
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


if __name__ == '__main__':
    print('Converted to ' + convert_to(sys.argv[1], sys.argv[2]))  # noqa: T201
