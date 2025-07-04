import io
from typing import IO

from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

from app.decorators.handle_gdrive_errors import handle_gdrive_errors
from app.providers.google_drive._google_drive_base_provider import _GoogleDriveBaseProvider
from app.utils.constants import FOLDER_MIME_TYPE


# pylint: disable=no-member
class GoogleDriveFilesProvider(_GoogleDriveBaseProvider):
    def __init__(self, credentials: service_account.Credentials = None):
        super().__init__(credentials)
        self.service = self.service.files()

    @handle_gdrive_errors()
    def create_folder(self, folder_name: str, parent_id: str = None, fields: str = None) -> dict:
        fields = fields or 'id, name'
        folder_metadata = {'name': folder_name, 'mimeType': FOLDER_MIME_TYPE}

        if parent_id:
            folder_metadata['parents'] = [parent_id]

        return self.service.create(body=folder_metadata, fields=fields).execute()

    @handle_gdrive_errors()
    def folder_exists(self, folder_name: str, parent_id: str = None, fields: str = None) -> dict | None:
        fields = fields or 'files(id, name)'
        query = f'mimeType="{FOLDER_MIME_TYPE}" and name="{folder_name}" and trashed=false'

        if parent_id:
            query += f' and "{parent_id}" in parents'

        response = self.service.list(q=query, fields=fields, pageSize=1).execute()

        folders = response.get('files', [])
        return folders[0] if folders else None

    @handle_gdrive_errors()
    def create_file_from_path(
        self, file_name: str, file_path: str, mime_type: str, parent_id: str = None, fields: str = None
    ) -> dict:
        fields = fields or 'id, name'
        file_metadata = {'name': file_name}

        if parent_id:
            file_metadata['parents'] = [parent_id]

        return self.service.create(
            body=file_metadata, media_body=MediaFileUpload(file_path, mimetype=mime_type), fields=fields
        ).execute()

    @handle_gdrive_errors()
    def create_file_from_stream(
        self, file_name: str, file_stream: IO[bytes], mime_type: str, parent_id: str = None, fields: str = None
    ) -> dict:
        fields = fields or 'id, name'
        file_metadata = {'name': file_name}

        if parent_id:
            file_metadata['parents'] = [parent_id]

        return self.service.create(
            body=file_metadata, media_body=MediaIoBaseUpload(file_stream, mimetype=mime_type), fields=fields
        ).execute()

    @handle_gdrive_errors()
    def upload_file_from_path(
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
    def upload_file_from_stream(
        self,
        file_id: str,
        file_name: str,
        file_stream: IO[bytes],
        mime_type: str,
        fields: str = None,
    ) -> dict:
        fields = fields or 'id, name, mimeType'
        file_metadata = {'name': file_name}

        return self.service.update(
            fileId=file_id,
            body=file_metadata,
            media_body=MediaIoBaseUpload(file_stream, mimetype=mime_type),
            fields=fields,
        ).execute()

    @handle_gdrive_errors()
    def get_files(self, page_size: int = None) -> dict[str, list[dict]]:
        page_size = page_size or 10

        return self.service.list(pageSize=page_size).execute()

    @handle_gdrive_errors()
    def get_file_metadata(self, file_id: str, fields: str = None) -> dict:
        fields = fields or 'id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink'

        return self.service.get(fileId=file_id, fields=fields).execute()

    @handle_gdrive_errors()
    def delete_file(self, item_id: str) -> None:
        """Delete an item (file or folder)  by id."""
        self.service.delete(fileId=item_id).execute()

    @handle_gdrive_errors()
    def download_file_content(self, file_id: str) -> io.BytesIO:
        request = self.service.get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()
            # IDEA: print(f"Download {int(status.progress() * 100)}%.")

        fh.seek(0)
        return fh
