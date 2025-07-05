# pylint: disable=attribute-defined-outside-init, unused-argument
import uuid
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock

import pytest
from flask import current_app
from werkzeug.exceptions import BadRequest

from app.file_storages import LocalStorage
from app.models.document import StorageTypes
from app.repositories import DocumentRepository
from app.services import DocumentService
from app.utils.constants import MS_EXCEL_MIME_TYPE, PDF_MIME_TYPE
from tests.base.base_unit_test import TestBaseUnit
from tests.conftest import BytesIOMatcher
from tests.factories.document_factory import GDriveDocumentFactory, LocalDocumentFactory


class _DocumentStub(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'name'
        self.mime_type = PDF_MIME_TYPE
        self.storage_type = kwargs.get('storage_type', StorageTypes.LOCAL)
        self.storage_id = kwargs.get('storage_id', None)

    def get_filepath(self):
        return True


class _TestDocumentBaseService(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def base_setup(self, faker, mock_gdrive_files_provider, mock_gdrive_permissions_provider):
        self.created_by_id = faker.random_int()
        self.mock_gdrive_files_provider, _ = mock_gdrive_files_provider
        self.mock_gdrive_permissions_provider, _ = mock_gdrive_permissions_provider
        self.document = MagicMock(_DocumentStub, autospec=True)
        self.document_id = faker.random_int()
        self.document.size = faker.random_int()


class TestCreateLocalDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.pdf_filename = 'example.pdf'
        self.internal_basename = str(uuid.uuid1())
        self.internal_filename = f'{self.internal_basename}.pdf'

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    @mock.patch('app.services.role.db.session')
    def test_create_local_document(self, mock_session, mock_current_user, mock_uuid):
        mock_current_user.id = self.created_by_id
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.save_bytes.return_value = None
        local_storage.get_filename.return_value = self.pdf_filename
        local_storage.get_filesize.return_value = self.document.size

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.create.return_value = self.document
        document_service = DocumentService(
            mock_doc_repo, local_storage, self.mock_gdrive_files_provider, self.mock_gdrive_permissions_provider
        )

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
                'created_by': self.created_by_id,
                'name': self.pdf_filename,
                'internal_filename': self.internal_filename,
                'mime_type': PDF_MIME_TYPE,
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': self.document.size,
            }
        )
        mock_session.add.assert_called_once_with(self.document)
        mock_session.flush.assert_called_once()
        assert isinstance(created_document, _DocumentStub)

    @mock.patch('app.services.document.current_user', autospec=True)
    def test_create_document_file_is_empty(self, mock_current_user):
        mock_current_user.id = 1
        document_service = DocumentService(
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )
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

        document_service = DocumentService(
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )
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

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    @mock.patch('app.services.role.db.session')
    def test_create_google_drive_document(self, mock_session, mock_current_user, mock_uuid):
        mock_current_user.id = self.created_by_id
        mock_current_user.fs_uniquifier = str(uuid.uuid1())
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        self.mock_gdrive_files_provider.folder_exists.return_value = None
        gdrive_folder_id = 5
        self.mock_gdrive_files_provider.create_folder.return_value = {'id': gdrive_folder_id}
        gdrive_file_id = 7
        self.mock_gdrive_files_provider.create_file_from_stream.return_value = {
            'id': gdrive_file_id,
            'mimeType': PDF_MIME_TYPE,
            'size': 9_556_144,
            'name': self.pdf_filename,
        }

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.get_filename.return_value = self.pdf_filename

        self.mock_gdrive_permissions_provider.apply_public_read_access_permission.return_value = {}

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.create.return_value = self.document
        document_service = DocumentService(
            document_repository=mock_doc_repo,
            file_storage=local_storage,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.pdf_filename}'
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': pdf_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(pdf_file, 'rb').read(),
            'storage_type': StorageTypes.GDRIVE.value,
        }

        created_document = document_service.create(**document_data)

        self.mock_gdrive_files_provider.folder_exists.assert_called_once_with(
            folder_name=mock_current_user.fs_uniquifier
        )
        self.mock_gdrive_files_provider.create_folder.assert_called_once_with(
            folder_name=mock_current_user.fs_uniquifier
        )
        local_storage.get_filename.assert_called_once_with(pdf_file)
        self.mock_gdrive_files_provider.create_file_from_stream.assert_called_once_with(
            parent_id=gdrive_folder_id,
            file_name=self.pdf_filename,
            file_stream=BytesIOMatcher(document_data.get('file_data')),
            mime_type=PDF_MIME_TYPE,
            fields='id, name, mimeType, size',
        )
        self.mock_gdrive_permissions_provider.apply_public_read_access_permission.assert_called_once_with(
            item_id=gdrive_file_id
        )
        mock_doc_repo.create.assert_called_once_with(
            **{
                'created_by': self.created_by_id,
                'name': self.pdf_filename,
                'mime_type': PDF_MIME_TYPE,
                'size': 9_556_144,
                'storage_type': StorageTypes.GDRIVE,
                'storage_id': gdrive_file_id,
            }
        )
        mock_session.add.assert_called_once_with(self.document)
        mock_session.flush.assert_called_once()
        assert isinstance(created_document, _DocumentStub)


class TestFindByIdDocumentService(_TestDocumentBaseService):
    def test_find_by_id_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.find_by_id.return_value = self.document
        document_service = DocumentService(
            mock_doc_repo,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        document = document_service.find_by_id(self.document_id)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document_id)
        assert isinstance(document, _DocumentStub)


class TestGetDocumentService(_TestDocumentBaseService):
    def test_get_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.get.return_value = [self.document]
        document_service = DocumentService(
            mock_doc_repo,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        document_data = {
            'items_per_page': 10,
            'order': [{'field_name': 'name', 'sorting': 'asc'}, {'field_name': 'created_at', 'sorting': 'desc'}],
            'page_number': 1,
            'search': [{'field_name': 'name', 'field_operator': 'contains', 'field_value': 'n'}],
        }
        documents = document_service.get(**document_data)

        mock_doc_repo.get.assert_called_once_with(**document_data)
        assert len(documents) == 1
        assert isinstance(documents[0], _DocumentStub)


class TestSaveLocalDocumentService(_TestDocumentBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.excel_filename = 'sample.xlsx'
        self.internal_basename = uuid.uuid1().hex
        self.internal_filename = f'{self.internal_basename}.xlsx'

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_save_local_document(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)
        self.document.storage_type = StorageTypes.LOCAL

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.save_bytes.return_value = None
        local_storage.get_filename.return_value = self.excel_filename
        filesize = 1_000_000
        local_storage.get_filesize.return_value = filesize

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.find_by_id.return_value = self.document
        mock_doc_repo.save.return_value = self.document
        document_service = DocumentService(
            mock_doc_repo,
            local_storage,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
        excel_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.excel_filename}'
        document_data = {
            'mime_type': MS_EXCEL_MIME_TYPE,
            'filename': excel_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(excel_file, 'rb').read(),
            'internal_filename': self.internal_filename,
        }

        document = document_service.save(self.document_id, **document_data)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document_id)
        local_storage.save_bytes.assert_called_once_with(document_data.get('file_data'), filepath, override=True)
        local_storage.get_filename.assert_called_once_with(excel_file)
        local_storage.get_filesize.assert_called_once_with(filepath)
        mock_doc_repo.save.assert_called_once_with(
            self.document_id,
            **{
                'name': self.excel_filename,
                'mime_type': MS_EXCEL_MIME_TYPE,
                'size': filesize,
                'internal_filename': self.internal_filename,
            },
        )
        assert isinstance(document, _DocumentStub)

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_save_document_file_is_empty(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        document_service = DocumentService(
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )
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

    @mock.patch('app.services.document.current_user', autospec=True)
    def test_save_google_drive_document(self, mock_current_user):
        mock_current_user.fs_uniquifier = str(self.faker.uuid4())
        self.document.storage_type = StorageTypes.GDRIVE
        self.document.storage_id = self.faker.uuid4()

        gdrive_folder_id = 5
        self.mock_gdrive_files_provider.folder_exists.return_value = {'id': gdrive_folder_id}
        gdrive_file_id = 7
        self.mock_gdrive_files_provider.upload_file_from_stream.return_value = {
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
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        excel_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.excel_file}'
        document_data = {
            'mime_type': MS_EXCEL_MIME_TYPE,
            'filename': excel_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(excel_file, 'rb').read(),
            'storage_type': StorageTypes.GDRIVE.value,
        }

        created_document = document_service.save(self.document_id, **document_data)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document_id)
        local_storage.get_filename.assert_called_once_with(excel_file)
        self.mock_gdrive_files_provider.upload_file_from_stream.assert_called_once_with(
            file_id=self.document.storage_id,
            file_name=self.excel_file,
            file_stream=BytesIOMatcher(document_data.get('file_data')),
            mime_type=MS_EXCEL_MIME_TYPE,
            fields='name, mimeType, size',
        )
        mock_doc_repo.save.assert_called_once_with(
            self.document_id,
            **{
                'name': self.excel_file,
                'mime_type': MS_EXCEL_MIME_TYPE,
                'size': 9_556_144,
            },
        )
        assert isinstance(created_document, _DocumentStub)


class TestDeleteDocumentService(_TestDocumentBaseService):
    def test_delete_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        self.document.deleted_at = datetime.now(UTC)
        mock_doc_repo.delete.return_value = self.document
        document_service = DocumentService(
            mock_doc_repo,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        document = document_service.delete(self.document_id)

        mock_doc_repo.delete.assert_called_once_with(self.document_id)
        assert isinstance(document, _DocumentStub)


class TestGetDocumentContentDocumentService(_TestDocumentBaseService):
    @pytest.mark.parametrize(
        'doc_name, request_args, expected_kwargs',
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
                    'download_name': f'{doc.name}.pdf',
                },
            ),
            (
                None,
                {'storage_type': StorageTypes.LOCAL.value},
                lambda doc: {
                    'path_or_file': b'',
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 0,
                },
            ),
        ],
        ids=[
            'default as_attachment',
            'explicit as_attachment=0',
            'explicit as_attachment=1',
            'custom doc name with as_attachment=1',
            'storage_type equals to "local"',
        ],
    )
    def test_get_local_document_content(self, doc_name, request_args, expected_kwargs):
        mock_doc_repo = mock.MagicMock(spec=DocumentRepository)

        document = _DocumentStub()
        mock_doc_repo.find_by_id.return_value = document
        expected_send_file_kwargs = expected_kwargs(document)

        document_service = DocumentService(
            mock_doc_repo,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )
        mock_get_local_document_content = MagicMock()
        mock_get_local_document_content.return_value = {'path_or_file': expected_send_file_kwargs['path_or_file']}
        document_service._get_local_document_content = mock_get_local_document_content  # pylint: disable=protected-access

        file_data = document_service.get_document_content(self.document_id, request_args)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document_id)
        document_service._get_local_document_content.assert_called_once_with(document)  # pylint: disable=protected-access
        assert file_data == expected_send_file_kwargs

    @pytest.mark.parametrize(
        'request_args, expected_kwargs',
        [
            (
                {'storage_type': StorageTypes.GDRIVE.value},
                lambda doc: {
                    'path_or_file': b'',
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 0,
                },
            ),
        ],
        ids=[
            'storage_type equals to "gdrive"',
        ],
    )
    def test_get_gdrive_document_content(self, request_args, expected_kwargs):
        mock_doc_repo = mock.MagicMock(spec=DocumentRepository)
        document = GDriveDocumentFactory()
        mock_doc_repo.find_by_id.return_value = document
        expected_send_file_kwargs = expected_kwargs(document)

        self.mock_gdrive_files_provider.download_file_content.return_value = b''
        document_service = DocumentService(
            mock_doc_repo,
            gdrive_files_provider=self.mock_gdrive_files_provider,
            gdrive_permissions_provider=self.mock_gdrive_permissions_provider,
        )

        file_data = document_service.get_document_content(document.id, request_args)

        mock_doc_repo.find_by_id.assert_called_once_with(document.id)
        self.mock_gdrive_files_provider.download_file_content.assert_called_once_with(document.storage_id)
        assert file_data == expected_send_file_kwargs
