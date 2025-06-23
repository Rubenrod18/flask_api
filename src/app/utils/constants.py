from enum import Enum

# Files
PDF_MIME_TYPE = 'application/pdf'
MS_WORD_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
MS_EXCEL_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


# Google Drive
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'


class GoogleDriveUserTypes(Enum):
    ANYONE = 'anyone'
    DOMAIN = 'domain'
    GROUP = 'group'
    USER = 'user'


class GoogleDriveRoles(Enum):
    OWNER = 'owner'
    READER = 'reader'
    WRITER = 'writer'
