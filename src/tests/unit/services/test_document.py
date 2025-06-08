import uuid
from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

from flask import current_app, Response, send_file
from werkzeug.exceptions import BadRequest

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import AdminUserFactory
from app.file_storages import LocalStorage
from app.models import Document
from app.repositories import DocumentRepository
from app.services import DocumentService
from app.utils.constants import PDF_MIME_TYPE
from tests.base.base_test import BaseTest


class _DocumentBaseServiceTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.admin_user = AdminUserFactory(deleted_at=None)


class CreateDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.pdf_filename = 'example.pdf'
        self.internal_basename = uuid.uuid1().hex
        self.internal_filename = f'{self.internal_basename}.pdf'
        self.document = DocumentFactory(name=self.pdf_filename, deleted_at=None)

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    @mock.patch('app.services.role.db.session', autospec=True)
    def test_create_document(self, mock_session, mock_current_user, mock_uuid):
        mock_current_user.id = self.admin_user.id
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
        self.assertTrue(isinstance(created_document, Document))
        self.assertEqual(created_document.created_by, self.admin_user.id)
        self.assertEqual(created_document.name, self.pdf_filename)
        self.assertEqual(created_document.mime_type, PDF_MIME_TYPE)
        self.assertEqual(created_document.size, self.document.size)
        self.assertTrue(created_document.created_at)
        self.assertEqual(created_document.updated_at, created_document.created_at)
        self.assertIsNone(created_document.deleted_at)

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_create_document_file_is_empty(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()

        with self.assertRaises(BadRequest) as context:
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

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'The file is empty!')

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.file_storages.local.os.path.exists', return_value=True)
    def test_create_document_file_already_exists(self, mock_uuid, mock_exists):  # noqa # pylint: disable=unused-argument
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': self.pdf_filename,
            'file_data': b'',
        }

        with self.assertRaises(BadRequest) as context:
            document_service.create(**document_data)
            document_service.file_storage.delete_file.assert_not_called()

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'The file already exists!')


class FindByIdDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(deleted_at=None)

    def test_find_by_id_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        mock_doc_repo.find_by_id.return_value = self.document
        document_service = DocumentService(mock_doc_repo)

        document = document_service.find_by_id(self.document.id)

        mock_doc_repo.find_by_id.assert_called_once_with(self.document.id)
        self.assertTrue(isinstance(document, Document))
        self.assertEqual(document.id, self.document.id)


class GetDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(deleted_at=None)

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
        self.assertEqual(len(documents), 1)
        self.assertTrue(isinstance(documents[0], Document))
        self.assertEqual(documents[0].id, self.document.id)


class SaveDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.pdf_filename = 'example.pdf'
        self.internal_basename = uuid.uuid1().hex
        self.internal_filename = f'{self.internal_basename}.pdf'

    @mock.patch('app.services.document.uuid', autospec=True)
    @mock.patch('app.services.document.current_user', autospec=True)
    def test_save_document(self, mock_current_user, mock_uuid):
        mock_current_user.id = self.admin_user.id
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        local_storage = MagicMock(spec=LocalStorage)
        local_storage.save_bytes.return_value = None
        local_storage.get_filename.return_value = self.pdf_filename
        filesize = 1_000_000
        local_storage.get_filesize.return_value = filesize

        mock_doc_repo = MagicMock(spec=DocumentRepository)
        document = DocumentFactory(
            name=self.pdf_filename,
            size=filesize,
            deleted_at=None,
            directory_path=current_app.config.get('STORAGE_DIRECTORY'),
            internal_filename=self.internal_filename,
        )
        mock_doc_repo.find_by_id.return_value = document
        mock_doc_repo.save.return_value = document
        document_service = DocumentService(mock_doc_repo, local_storage)

        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
        pdf_file = f'{current_app.config.get("MOCKUP_DIRECTORY")}/{self.pdf_filename}'
        document_data = {
            'mime_type': PDF_MIME_TYPE,
            'filename': pdf_file,  # NOTE: `helpers.request_helpers.get_request_file` returns the abs path of the file
            'file_data': open(pdf_file, 'rb').read(),
        }

        document = document_service.save(document.id, **document_data)

        mock_doc_repo.find_by_id.assert_called_once_with(document.id)
        local_storage.save_bytes.assert_called_once_with(document_data.get('file_data'), filepath, override=True)
        local_storage.get_filename.assert_called_once_with(pdf_file)
        local_storage.get_filesize.assert_called_once_with(filepath)
        mock_doc_repo.save.assert_called_once_with(
            document.id,
            **{
                'name': self.pdf_filename,
                'mime_type': PDF_MIME_TYPE,
                'size': filesize,
            },
        )
        self.assertTrue(isinstance(document, Document))
        self.assertEqual(document.created_by, self.admin_user.id)
        self.assertEqual(document.name, self.pdf_filename)
        self.assertEqual(document.mime_type, PDF_MIME_TYPE)
        self.assertEqual(document.size, filesize)
        self.assertTrue(document.created_at)
        self.assertEqual(document.updated_at, document.created_at)
        self.assertIsNone(document.deleted_at)

    @mock.patch('app.services.document.uuid', autospec=True)
    def test_save_document_file_is_empty(self, mock_uuid):
        mock_uuid.uuid1.return_value = MagicMock(hex=self.internal_basename)

        document_service = DocumentService()
        document_service.file_storage.delete_file = MagicMock()
        document = DocumentFactory(deleted_at=None)

        with self.assertRaises(BadRequest) as context:
            document_service.save(
                document.id,
                **{
                    'mime_type': PDF_MIME_TYPE,
                    'filename': self.pdf_filename,
                    'file_data': b'',
                },
            )
            document_service.file_storage.delete_file.assert_called_once_with(
                f'{current_app.config.get("STORAGE_DIRECTORY")}/{self.internal_filename}'
            )

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'The file is empty!')


class DeleteDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(deleted_at=None)

    def test_delete_document(self):
        mock_doc_repo = MagicMock(spec=DocumentRepository)
        self.document.deleted_at = datetime.now(UTC)
        mock_doc_repo.delete.return_value = self.document
        document_service = DocumentService(mock_doc_repo)

        document = document_service.delete(self.document.id)

        mock_doc_repo.delete.assert_called_once_with(self.document.id)
        self.assertTrue(isinstance(document, Document))
        self.assertEqual(document.id, self.document.id)
        self.assertEqual(document.deleted_at, self.document.deleted_at)


class GetDocumentContentDocumentServiceTest(_DocumentBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(deleted_at=None)

    @mock.patch('app.services.document.send_file', autospec=True)
    def test_get_document_content_document(self, mock_send_file):
        mock_doc_repo = MagicMock(spec=DocumentRepository)

        test_cases = [
            (
                doc := DocumentFactory(),
                {},
                {'path_or_file': doc.get_filepath(), 'mimetype': PDF_MIME_TYPE, 'as_attachment': 0},
            ),
            (
                doc := DocumentFactory(),
                {'as_attachment': 0},
                {'path_or_file': doc.get_filepath(), 'mimetype': PDF_MIME_TYPE, 'as_attachment': 0},
            ),
            (
                doc := DocumentFactory(),
                {'as_attachment': 1},
                {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 1,
                    'download_name': f'{doc.name}.pdf',
                },
            ),
            (
                doc := DocumentFactory(name='document_name_0.pdf'),
                {'as_attachment': 1},
                {
                    'path_or_file': doc.get_filepath(),
                    'mimetype': PDF_MIME_TYPE,
                    'as_attachment': 1,
                    'download_name': doc.name,
                },
            ),
        ]

        for document, request_args, send_file_kwargs in test_cases:
            mock_doc_repo.reset_mock()
            mock_doc_repo.find_by_id.return_value = document
            document_service = DocumentService(mock_doc_repo)
            mock_send_file.reset_mock()

            with current_app.test_request_context():  # NOTE: Required by `send_file` function
                mock_send_file.return_value = send_file(**send_file_kwargs)
                response = document_service.get_document_content(self.document.id, request_args)

            mock_doc_repo.find_by_id.assert_called_once_with(self.document.id)
            mock_send_file.assert_called_once_with(**send_file_kwargs)
            self.assertTrue(isinstance(response, Response), response)
            self.assertEqual(response.mimetype, PDF_MIME_TYPE)
