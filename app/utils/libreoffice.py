import os
import sys
import subprocess
import re
import logging

logger = logging.getLogger(__name__)


def convert_to(folder: str, source: str) -> str:
    logger.debug('Folder: %s' % folder)
    logger.debug('Word file: %s' % source)

    if not os.path.isdir(folder):
        raise FileNotFoundError('%s directory not found' % source)

    if not os.path.isfile(source):
        raise FileNotFoundError('%s file not found' % source)

    args = [
        libreoffice_exec(),
        '--headless',
        '--convert-to',
        'pdf:writer_pdf_Export',
        '--outdir',
        folder,
        source,
    ]

    process = subprocess.run(args, stdout=subprocess.PIPE,
                             env={'$HOME': os.getenv('HOME')})
    logger.debug(process)
    filename = re.search('-> (.*?) using filter',
                         process.stdout.decode('utf-8'))

    if filename is None:
        raise LibreOfficeError(process.stdout.decode('utf-8'))
    else:
        return filename.group(1)


def libreoffice_exec() -> str:
    # TODO: Provide support for more platforms
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


if __name__ == '__main__':
    print('Converted to ' + convert_to(sys.argv[1], sys.argv[2]))
