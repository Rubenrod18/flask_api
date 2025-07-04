import io
import mimetypes
import uuid

from flask import current_app, Response, send_file
from flask_login import current_user
from werkzeug.exceptions import BadRequest

from app.exceptions import FileEmptyError, GoogleDriveError
from app.extensions import db
from app.file_storages import LocalStorage
from app.models import Document
from app.models.document import StorageTypes
from app.providers.google_drive import GoogleDriveFilesProvider, GoogleDrivePermissionsProvider
from app.repositories import DocumentRepository
from app.services import base as b


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
                'storage_type': StorageTypes.GDRIVE,
                'storage_id': gdrive_file['id'],
            }
        except (Exception, GoogleDriveError) as e:
            if 'gdrive_file' in locals():
                self.gdrive_files_provider.delete_file(gdrive_file['id'])

            raise e

    def create(self, **kwargs) -> Document:
        storage_type = kwargs.get('storage_type', StorageTypes.LOCAL.value)
        storage_types = {
            StorageTypes.LOCAL.value: self._create_local_file,
            StorageTypes.GDRIVE.value: self._create_gdrive_file,
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

    def _save_local_file(self, **kwargs) -> dict:
        file_extension = mimetypes.guess_extension(kwargs['mime_type'])
        internal_filename = f'{uuid.uuid1().hex}{file_extension}'
        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{internal_filename}'

        try:
            self.file_storage.save_bytes(kwargs.get('file_data'), filepath, override=True)

            return {
                'name': self.file_storage.get_filename(kwargs.get('filename')),
                'internal_filename': internal_filename,
                'mime_type': kwargs.get('mime_type'),
                'size': self.file_storage.get_filesize(filepath),
            }
        except (FileExistsError, FileEmptyError) as e:
            if isinstance(e, FileEmptyError):
                self.file_storage.delete_file(filepath)

            raise BadRequest(description=str(e)) from e

    def _save_gdrive_file(self, **kwargs) -> dict:
        try:
            gdrive_file = self.gdrive_files_provider.upload_file_from_stream(
                file_id=kwargs['document'].storage_id,
                file_name=self.file_storage.get_filename(kwargs['filename']),
                file_stream=io.BytesIO(kwargs['file_data']),
                mime_type=kwargs['mime_type'],
                fields='name, mimeType, size',
            )

            return {
                'name': gdrive_file['name'],
                'mime_type': gdrive_file['mimeType'],
                'size': gdrive_file['size'],
            }
        except (Exception, GoogleDriveError) as e:
            if 'gdrive_file' in locals():
                self.gdrive_files_provider.delete_file(gdrive_file['id'])

            raise e

    def save(self, record_id: int, **kwargs) -> Document:
        storage_type = kwargs.get('storage_type', StorageTypes.LOCAL.value)
        storage_types = {
            StorageTypes.LOCAL.value: self._save_local_file,
            StorageTypes.GDRIVE.value: self._save_gdrive_file,
        }

        document = self.repository.find_by_id(record_id)
        kwargs['document'] = document
        document_data = storage_types.get(storage_type)(**kwargs)

        return self.repository.save(record_id, **document_data)

    def delete(self, record_id: int) -> Document:
        return self.repository.delete(record_id)

    @staticmethod
    def _get_local_document_content(document: Document) -> dict:
        return {'path_or_file': document.get_filepath()}

    def _get_gdrive_document_content(self, document: Document) -> dict:
        return {'path_or_file': self.gdrive_files_provider.download_file_content(document.storage_id)}

    def get_document_content(self, document_id: int, request_args: dict) -> Response:
        as_attachment = request_args.get('as_attachment', 0)
        storage_type = request_args.get('storage_type', StorageTypes.LOCAL.value)
        storage_types = {
            StorageTypes.LOCAL.value: self._get_local_document_content,
            StorageTypes.GDRIVE.value: self._get_gdrive_document_content,
        }

        document = self.repository.find_by_id(document_id)
        file_extension = mimetypes.guess_extension(document.mime_type)

        file_data = storage_types.get(storage_type)(document)
        file_data.update(
            {
                'as_attachment': as_attachment,
                'mimetype': document.mime_type,
            }
        )

        if as_attachment:
            file_data['download_name'] = (
                document.name if document.name.find(file_extension) != -1 else f'{document.name}{file_extension}'
            )

        return send_file(**file_data)
