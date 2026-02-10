import enum

# Files
PDF_MIME_TYPE = 'application/pdf'
MS_WORD_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
MS_EXCEL_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


# Google Drive
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'


class BaseEnum(enum.StrEnum):
    @classmethod
    def to_list(cls, get_values=True):
        attr = 'name'
        if get_values:
            attr = 'value'
        return [getattr(_, attr) for _ in list(cls)]


class GoogleDriveUserTypes(BaseEnum):
    ANYONE = 'anyone'
    DOMAIN = 'domain'
    GROUP = 'group'
    USER = 'user'


class GoogleDriveRoles(BaseEnum):
    OWNER = 'owner'
    READER = 'reader'
    WRITER = 'writer'
