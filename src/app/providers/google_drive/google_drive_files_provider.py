from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

from app.decorators.handle_gdrive_errors import handle_gdrive_errors
from app.providers.google_drive._google_drive_base_provider import _GoogleDriveBaseProvider
from app.utils.constants import FOLDER_MIME_TYPE


# pylint: disable=no-member
class GoogleDriveFilesProvider(_GoogleDriveBaseProvider):
    def __init__(self, credentials: service_account.Credentials = None):
        super().__init__(credentials)
        self.service = self.service.files()

    @handle_gdrive_errors()
    def create_folder(self, name: str, parent_id: str = None, fields: str = None) -> dict:
        fields = fields or 'id, name'
        folder_metadata = {'name': name, 'mimeType': FOLDER_MIME_TYPE}

        if parent_id:
            folder_metadata['parents'] = [parent_id]

        return self.service.create(body=folder_metadata, fields=fields).execute()

    @handle_gdrive_errors()
    def create_file(self, name: str, path: str, mime_type: str, parent_id: str = None, fields: str = None) -> dict:
        fields = fields or 'id, name'
        file_metadata = {'name': name}

        if parent_id:
            file_metadata['parents'] = [parent_id]

        return self.service.create(
            body=file_metadata, media_body=MediaFileUpload(path, mimetype=mime_type), fields=fields
        ).execute()

    @handle_gdrive_errors()
    def upload_file(
        self, file_id: str, file_name: str, file_path: str, mime_type: str, parent_id: str = None, fields: str = None
    ) -> dict:
        fields = fields or 'id, name, mimeType'
        file_metadata = {'name': file_name}

        if parent_id:
            file_metadata['parents'] = [parent_id]

        return self.service.update(
            fileId=file_id,
            body=file_metadata,
            media_body=MediaFileUpload(file_path, mimetype=mime_type),
            fields=fields,
        ).execute()

    @handle_gdrive_errors()
    def get_files(self, page_size: int = None) -> dict[str, list[dict]]:
        page_size = page_size or 10

        return self.service.list(pageSize=page_size).execute()

    @handle_gdrive_errors()
    def get_file_metadata(self, file_id, fields: str = None) -> dict:
        fields = fields or 'id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink'

        return self.service.get(fileId=file_id, fields=fields).execute()

    @handle_gdrive_errors()
    def delete_file(self, file_id: str) -> None:
        self.service.delete(fileId=file_id).execute()
