# pylint: disable=attribute-defined-outside-init, unused-argument
import uuid
from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

import pytest
from flask import current_app, Response, send_file
from werkzeug.exceptions import BadRequest

from app.database.factories.document_factory import GDriveDocumentFactory, LocalDocumentFactory
from app.database.factories.user_factory import AdminUserFactory
from app.file_storages import LocalStorage
from app.models import Document
from app.models.document import StorageType
from app.providers.google_drive import GoogleDriveFilesProvider, GoogleDrivePermissionsProvider
from app.repositories import DocumentRepository
from app.services import DocumentService
from app.utils.constants import MS_EXCEL_MIME_TYPE, PDF_MIME_TYPE
from tests.conftest import BytesIOMatcher


class _TestDocumentBaseService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.admin_user = AdminUserFactory(deleted_at=None)


class TestCreateLocalDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.pdf_filename = 'example.pdf'
        self.internal_basename = str(uuid.uuid1())
        self.internal_filename = f'{self.internal_basename}.pdf'
        self.document = LocalDocumentFactory(name=self.pdf_filename, deleted_at=None)

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    @mock.patch('app.services.role.db.session', autospec=True)
    def test_create_local_document(self, mock_session, mock_current_user, mock_uuid):
        mock_current_user.id = 1
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.save_bytes.return_value = None
        local_storage.get_filename.return_value = self.pdf_filename
        local_storage.get_filesize.return_value = self.document.size

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.create.return_value = self.document
        document_service = DocumentService(mock_doc_repo, local_storage)

        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.pdf_filename}'
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': pdf_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(pdf_file, 'rb').read(),
        }

        created_document = document_service.create(**document_data)

        local_storage.save_bytes.assert_called_once_with(document_data.get('file_data'), filepath)
        local_storage.get_filename.assert_called_once_with(pdf_file)
        local_storage.get_filesize.assert_called_once_with(filepath)
        mock_doc_repo.create.assert_called_once_with(
            **{
                'created_by': self.admin_user.id,
                'name': self.pdf_filename,
                'internal_filename': self.internal_filename,
                'mime_type': PDF_MIME_TYPE,
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': self.document.size,
            }
        )
        mock_session.add.assert_called_once_with(self.document)
        mock_session.flush.assert_called_once_with()
        assert isinstance(created_document, Document)
        assert created_document.created_by == self.admin_user.id
        assert created_document.name == self.pdf_filename
        assert created_document.mime_type == PDF_MIME_TYPE
        assert created_document.size == self.document.size
        assert created_document.storage_type == StorageType.LOCAL.value
        assert created_document.storage_id is None
        assert created_document.created_at
        assert created_document.updated_at == created_document.created_at
        assert created_document.deleted_at is None

    @mock.patch('app.services.document.current_user', autospec=True)
    def test_create_document_file_is_empty(self, mock_current_user):
        mock_current_user.id = 1
        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()

        with pytest.raises(BadRequest) as exc_info:
            document_service.create(
                **{
                    'mime_type': PDF_MIME_TYPE,
                    'filename': self.pdf_filename,
                    'file_data': b'',
                }
            )
            document_service.file_storage.delete_file.assert_called_once_with(
                f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
            )

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'The file is empty!'

    @mock.patch('app.file_storages.local.os.path.exists', return_value=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    def test_create_document_file_already_exists(self, mock_current_user, mock_exists):  # noqa # pylint: disable=unused-argument
        mock_current_user.id = 1

        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': self.pdf_filename,
            'file_data': b'',
        }

        with pytest.raises(BadRequest) as exc_info:
            document_service.create(**document_data)
            document_service.file_storage.delete_file.assert_not_called()

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'The file already exists!'


class TestCreateGoogleDriveDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.pdf_filename = 'example.pdf'
        self.internal_basename = str(uuid.uuid1())
        self.internal_filename = f'{self.internal_basename}.pdf'
        self.document = GDriveDocumentFactory(name=self.pdf_filename, deleted_at=None)

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    @mock.patch('app.services.role.db.session', autospec=True)
    def test_create_google_drive_document(self, mock_session, mock_current_user, mock_uuid):
        mock_current_user.id = 1
        mock_current_user.fs_uniquifier = str(uuid.uuid1())
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        gdrive_files_provider = MagicMock(spec=GoogleDriveFilesProvider)
        gdrive_files_provider.folder_exists.return_value = None
        gdrive_folder_id = 5
        gdrive_files_provider.create_folder.return_value = {'id': gdrive_folder_id}
        gdrive_file_id = 7
        gdrive_files_provider.create_file_from_stream.return_value = {
            'id': gdrive_file_id,
            'mimeType': PDF_MIME_TYPE,
            'size': 9_556_144,
            'name': self.pdf_filename,
        }

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.get_filename.return_value = self.pdf_filename

        gdrive_permissions_provider = MagicMock(spec=GoogleDrivePermissionsProvider)
        gdrive_permissions_provider.apply_public_read_access_permission.return_value = {}

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.create.return_value = self.document
        document_service = DocumentService(
            document_repository=mock_doc_repo,
            file_storage=local_storage,
            gdrive_files_provider=gdrive_files_provider,
            gdrive_permissions_provider=gdrive_permissions_provider,
        )

        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.pdf_filename}'
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': pdf_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(pdf_file, 'rb').read(),
            'storage_type': StorageType.GDRIVE.value,
        }

        created_document = document_service.create(**document_data)

        gdrive_files_provider.folder_exists.assert_called_once_with(folder_name=mock_current_user.fs_uniquifier)
        gdrive_files_provider.create_folder.assert_called_once_with(folder_name=mock_current_user.fs_uniquifier)
        local_storage.get_filename.assert_called_once_with(pdf_file)
        gdrive_files_provider.create_file_from_stream.assert_called_once_with(
            parent_id=gdrive_folder_id,
            file_name=self.pdf_filename,
            file_stream=BytesIOMatcher(document_data.get('file_data')),
            mime_type=PDF_MIME_TYPE,
            fields='id, name, mimeType, size',
        )
        gdrive_permissions_provider.apply_public_read_access_permission.assert_called_once_with(item_id=gdrive_file_id)
        mock_doc_repo.create.assert_called_once_with(
            **{
                'created_by': self.admin_user.id,
                'name': self.pdf_filename,
                'mime_type': PDF_MIME_TYPE,
                'size': 9_556_144,
                'storage_type': StorageType.GDRIVE,
                'storage_id': gdrive_file_id,
            }
        )
        mock_session.add.assert_called_once_with(self.document)
        mock_session.flush.assert_called_once_with()
        assert isinstance(created_document, Document)
        assert created_document.created_by == self.admin_user.id
        assert created_document.name == self.pdf_filename
        assert created_document.mime_type == PDF_MIME_TYPE
        assert created_document.size == self.document.size
        assert created_document.size == self.document.size
        assert created_document.directory_path is None
        assert created_document.internal_filename is None
        assert created_document.storage_type == StorageType.GDRIVE.value
        assert uuid.UUID(created_document.storage_id, version=1)
        assert created_document.url == f'https://drive.google.com/file/d/{created_document.storage_id}/view'
        assert created_document.created_at
        assert created_document.updated_at == created_document.created_at
        assert created_document.deleted_at is None


class TestFindByIdDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(deleted_at=None)

    def test_find_by_id_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.find_by_id.return_value = self.document
        document_service = DocumentService(mock_doc_repo)

        document = document_service.find_by_id(self.document.id)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document.id)
        assert isinstance(document, Document)
        assert document.id == self.document.id


class TestGetDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(deleted_at=None)

    def test_get_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.get.return_value = [self.document]
        document_service = DocumentService(mock_doc_repo)

        document_data = {
            'items_per_page': 10,
            'order': [{'field_name': 'name', 'sorting': 'asc'}, {'field_name': 'created_at', 'sorting': 'desc'}],
            'page_number': 1,
            'search': [{'field_name': 'name', 'field_operator': 'contains', 'field_value': 'n'}],
        }
        documents = document_service.get(**document_data)

        mock_doc_repo.get.assert_called_once_with(**document_data)
        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].id == self.document.id


class TestSaveLocalDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.excel_filename = 'sample.xlsx'
        self.internal_basename = uuid.uuid1().hex
        self.internal_filename = f'{self.internal_basename}.xlsx'

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_save_local_document(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.save_bytes.return_value = None
        local_storage.get_filename.return_value = self.excel_filename
        filesize = 1_000_000
        local_storage.get_filesize.return_value = filesize

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        document = LocalDocumentFactory(
            name=self.excel_filename,
            size=filesize,
            deleted_at=None,
            mime_type=MS_EXCEL_MIME_TYPE,
            directory_path=current_app.config.get('STORAGE_DIRECTORY'),
            internal_filename=self.internal_filename,
        )
        mock_doc_repo.save.return_value = document
        document_service = DocumentService(mock_doc_repo, local_storage)

        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
        excel_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.excel_filename}'
        document_data = {
            'mime_type': MS_EXCEL_MIME_TYPE,
            'filename': excel_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(excel_file, 'rb').read(),
            'internal_filename': self.internal_filename,
        }

        document = document_service.save(document.id, **document_data)

        local_storage.save_bytes.assert_called_once_with(document_data.get('file_data'), filepath, override=True)
        local_storage.get_filename.assert_called_once_with(excel_file)
        local_storage.get_filesize.assert_called_once_with(filepath)
        mock_doc_repo.save.assert_called_once_with(
            document.id,
            **{
                'name': self.excel_filename,
                'mime_type': MS_EXCEL_MIME_TYPE,
                'size': filesize,
                'internal_filename': self.internal_filename,
            },
        )
        assert isinstance(document, Document)
        assert document.created_by == self.admin_user.id
        assert document.name == self.excel_filename
        assert document.mime_type == MS_EXCEL_MIME_TYPE
        assert document.size == filesize
        assert document.storage_type == StorageType.LOCAL.value
        assert document.storage_id is None
        assert document.created_at
        assert document.updated_at == document.created_at
        assert document.deleted_at is None

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_save_document_file_is_empty(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()
        document = LocalDocumentFactory(deleted_at=None)

        with pytest.raises(BadRequest) as exc_info:
            document_service.save(
                document.id,
                **{
                    'mime_type': PDF_MIME_TYPE,
                    'filename': self.excel_filename,
                    'file_data': b'',
                },
            )
            document_service.file_storage.delete_file.assert_called_once_with(
                f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
            )

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'The file is empty!'


class TestSaveGoogleDriveDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.excel_file = 'sample.xlsx'
        self.internal_basename = str(uuid.uuid1())
        self.internal_filename = f'{self.internal_basename}.xlsx'
        self.document = GDriveDocumentFactory(
            name=self.excel_file,
            deleted_at=None,
            mime_type=MS_EXCEL_MIME_TYPE,
        )

    @mock.patch('app.services.document.current_user', autospec=True)
    def test_save_google_drive_document(self, mock_current_user):
        mock_current_user.fs_uniquifier = str(uuid.uuid1())

        gdrive_files_provider = MagicMock(spec=GoogleDriveFilesProvider)
        gdrive_folder_id = 5
        gdrive_files_provider.folder_exists.return_value = {'id': gdrive_folder_id}
        gdrive_file_id = 7
        gdrive_files_provider.upload_file_from_stream.return_value = {
            'id': gdrive_file_id,
            'mimeType': MS_EXCEL_MIME_TYPE,
            'size': 9_556_144,
            'name': self.excel_file,
        }

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.get_filename.return_value = self.excel_file

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.find_by_id.return_value = self.document
        mock_doc_repo.save.return_value = self.document
        document_service = DocumentService(
            document_repository=mock_doc_repo,
            file_storage=local_storage,
            gdrive_files_provider=gdrive_files_provider,
        )

        excel_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.excel_file}'
        document_data = {
            'mime_type': MS_EXCEL_MIME_TYPE,
            'filename': excel_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(excel_file, 'rb').read(),
            'storage_type': StorageType.GDRIVE.value,
        }

        created_document = document_service.save(self.document.id, **document_data)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document.id)
        local_storage.get_filename.assert_called_once_with(excel_file)
        gdrive_files_provider.upload_file_from_stream.assert_called_once_with(
            file_id=self.document.storage_id,
            file_name=self.excel_file,
            file_stream=BytesIOMatcher(document_data.get('file_data')),
            mime_type=MS_EXCEL_MIME_TYPE,
            fields='name, mimeType, size',
        )
        mock_doc_repo.save.assert_called_once_with(
            self.document.id,
            **{
                'name': self.excel_file,
                'mime_type': MS_EXCEL_MIME_TYPE,
                'size': 9_556_144,
            },
        )
        assert isinstance(created_document, Document)
        assert created_document.created_by == self.admin_user.id
        assert created_document.name == self.excel_file
        assert created_document.mime_type == MS_EXCEL_MIME_TYPE
        assert created_document.size == self.document.size
        assert created_document.size == self.document.size
        assert created_document.directory_path is None
        assert created_document.internal_filename is None
        assert created_document.storage_type == StorageType.GDRIVE.value
        assert uuid.UUID(created_document.storage_id, version=1)
        assert created_document.url == f'https://drive.google.com/file/d/{created_document.storage_id}/view'
        assert created_document.created_at
        assert created_document.updated_at == created_document.created_at
        assert created_document.deleted_at is None


class TestDeleteDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(deleted_at=None)

    def test_delete_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        self.document.deleted_at = datetime.now(UTC)
        mock_doc_repo.delete.return_value = self.document
        document_service = DocumentService(mock_doc_repo)

        document = document_service.delete(self.document.id)

        mock_doc_repo.delete.assert_called_once_with(self.document.id)
        assert isinstance(document, Document)
        assert document.id == self.document.id
        assert document.deleted_at == self.document.deleted_at


class TestGetDocumentContentDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = LocalDocumentFactory(deleted_at=None)

    @pytest.mark.parametrize(
        'doc_name, as_attachment_param, expected_kwargs',
        [
            (
                None,
                {},
                lambda doc: {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 0,
                },
            ),
            (
                None,
                {'as_attachment': 0},
                lambda doc: {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 0,
                },
            ),
            (
                None,
                {'as_attachment': 1},
                lambda doc: {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 1,
                    'download_name': f'{doc.name}.pdf',
                },
            ),
            (
                'document_name_0.pdf',
                {'as_attachment': 1},
                lambda doc: {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 1,
                    'download_name': doc.name,
                },
            ),
        ],
        ids=[
            'default as_attachment',
            'explicit as_attachment=0',
            'explicit as_attachment=1',
            'custom doc name with as_attachment=1',
        ],
    )
    @mock.patch('app.services.document.send_file', autospec=True)
    def test_get_document_content_document(self, mock_send_file, doc_name, as_attachment_param, expected_kwargs):
        mock_doc_repo = mock.MagicMock(spec=DocumentRepository)

        document = LocalDocumentFactory(name=doc_name) if doc_name else LocalDocumentFactory()
        mock_doc_repo.find_by_id.return_value = document

        document_service = DocumentService(mock_doc_repo)
        expected_args = expected_kwargs(document)

        with current_app.test_request_context():
            mock_send_file.return_value = send_file(**expected_args)
            response = document_service.get_document_content(self.document.id, as_attachment_param)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document.id)
        mock_send_file.assert_called_once_with(**expected_args)
        assert isinstance(response, Response)
        assert response.mimetype == PDF_MIME_TYPE
