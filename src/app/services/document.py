import io
import logging
import mimetypes
import uuid

from flask import current_app, Response, send_file
from flask_login import current_user
from werkzeug.exceptions import BadRequest

from app.exceptions import FileEmptyError, GoogleDriveError
from app.extensions import db
from app.file_storages import LocalStorage
from app.models import Document
from app.models.document import StorageType
from app.providers.google_drive import GoogleDriveFilesProvider, GoogleDrivePermissionsProvider
from app.repositories import DocumentRepository
from app.services import base as b

logger = logging.getLogger(__name__)


class DocumentService(
    b.BaseService, b.CreationService, b.DeletionService, b.FindByIdService, b.GetService, b.SaveService
):
    def __init__(
        self,
        document_repository: DocumentRepository = None,
        file_storage: LocalStorage = None,
        gdrive_files_provider: GoogleDriveFilesProvider = None,
        gdrive_permissions_provider: GoogleDrivePermissionsProvider = None,
    ):
        super().__init__(repository=document_repository or DocumentRepository())
        self.file_storage = file_storage or LocalStorage()
        self.gdrive_files_provider = gdrive_files_provider or GoogleDriveFilesProvider()
        self.gdrive_permissions_provider = gdrive_permissions_provider or GoogleDrivePermissionsProvider()

    def _create_local_file(self, **kwargs) -> dict:
        file_extension = mimetypes.guess_extension(kwargs['mime_type'])
        internal_filename = f'{uuid.uuid1().hex}{file_extension}'
        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{internal_filename}'

        try:
            self.file_storage.save_bytes(kwargs['file_data'], filepath)

            return {
                'name': self.file_storage.get_filename(kwargs['filename']),
                'internal_filename': internal_filename,
                'mime_type': kwargs['mime_type'],
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': self.file_storage.get_filesize(filepath),
            }
        except (Exception, FileExistsError, FileEmptyError) as e:
            self.file_storage.delete_file(filepath)
            raise BadRequest(description=str(e)) from e

    def _create_gdrive_file(self, **kwargs) -> dict:
        try:
            gdrive_folder = self.gdrive_files_provider.folder_exists(folder_name=current_user.fs_uniquifier)
            if gdrive_folder is None:
                gdrive_folder = self.gdrive_files_provider.create_folder(folder_name=current_user.fs_uniquifier)

            gdrive_file = self.gdrive_files_provider.create_file_from_stream(
                parent_id=gdrive_folder['id'],
                file_name=self.file_storage.get_filename(kwargs['filename']),
                file_stream=io.BytesIO(kwargs['file_data']),
                mime_type=kwargs['mime_type'],
                fields='id, name, mimeType, size',
            )
            self.gdrive_permissions_provider.apply_public_read_access_permission(item_id=gdrive_file['id'])

            return {
                'name': gdrive_file['name'],
                'mime_type': gdrive_file['mimeType'],
                'size': gdrive_file['size'],
                'storage_type': StorageType.GDRIVE,
                'storage_id': gdrive_file['id'],
            }
        except (Exception, GoogleDriveError) as e:
            if 'gdrive_file' in locals():
                self.gdrive_files_provider.delete_file(gdrive_file['id'])

            raise e

    def create(self, **kwargs) -> Document:
        storage_type = kwargs.get('storage_type', StorageType.LOCAL.value)
        storage_types = {
            StorageType.LOCAL.value: self._create_local_file,
            StorageType.GDRIVE.value: self._create_gdrive_file,
        }

        document_data = {'created_by': current_user.id}
        file_data = storage_types.get(storage_type, self._create_local_file)(**kwargs)
        document_data.update(file_data)

        document = self.repository.create(**document_data)
        db.session.add(document)
        db.session.flush()

        return document

    def find_by_id(self, record_id: int, *args) -> Document | None:
        return self.repository.find_by_id(record_id, *args)

    def get(self, **kwargs) -> dict:
        return self.repository.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> Document:
        # HACK: PENDING TO ADD GDRIVE
        document = self.repository.find_by_id(record_id)
        # QUESTION: The app doesn't have file versioning, should we consider this feature in the future?
        filepath = f'{document.directory_path}/{document.internal_filename}'

        try:
            self.file_storage.save_bytes(kwargs.get('file_data'), filepath, override=True)

            data = {
                'name': self.file_storage.get_filename(kwargs.get('filename')),
                'mime_type': kwargs.get('mime_type'),
                'size': self.file_storage.get_filesize(filepath),
            }
            document = self.repository.save(record_id, **data)
            db.session.flush()
        except (FileExistsError, FileEmptyError) as e:
            if isinstance(e, FileEmptyError):
                self.file_storage.delete_file(filepath)

            raise BadRequest(description=str(e)) from e
        else:
            return document.reload()

    def delete(self, record_id: int) -> Document:
        return self.repository.delete(record_id)

    def get_document_content(self, document_id: int, request_args: dict) -> Response:
        # HACK: PENDING TO ADD GDRIVE
        as_attachment = request_args.get('as_attachment', 0)
        document = self.repository.find_by_id(document_id)

        mime_type = document.mime_type
        file_extension = mimetypes.guess_extension(mime_type)

        kwargs = {
            'path_or_file': document.get_filepath(),
            'mimetype': mime_type,
            'as_attachment': as_attachment,
        }

        if as_attachment:
            kwargs['download_name'] = (
                document.name if document.name.find(file_extension) != -1 else f'{document.name}{file_extension}'
            )

        return send_file(**kwargs)
