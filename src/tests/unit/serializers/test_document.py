import unittest
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

from marshmallow import ValidationError
from werkzeug.exceptions import NotFound, UnprocessableEntity

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.managers import DocumentManager
from app.models import Document
from app.repositories import DocumentRepository
from app.serializers import DocumentAttachmentSerializer, DocumentSerializer
from tests.base.base_test import BaseTest


class DocumentSerializerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.document_manager = MagicMock(spec=DocumentManager)
        self.document_manager.repository = MagicMock(spec=DocumentRepository)
        self.document_manager.model = MagicMock(spec=Document)
        self.document_manager.model.deleted_at.is_.return_value = None
        self.document = DocumentFactory(
            name='test_doc.pdf',
            internal_filename='test_doc_internal.pdf',
            mime_type='application/pdf',
            size=1_024,
            created_by_user=self.user,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )

        self.serializer = DocumentSerializer()
        self.serializer._document_manager = self.document_manager  # pylint: disable=protected-access
        self.document_manager.find_by_id.return_value = self.document

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.document)

        self.assertEqual(serialized_data['id'], 1)
        self.assertEqual(serialized_data['name'], 'test_doc.pdf')
        self.assertEqual(serialized_data['mime_type'], 'application/pdf')
        self.assertIn('url', serialized_data)
        self.assertEqual(serialized_data['created_by']['name'], self.user.name)

    def test_validate_existing_document_id(self):
        self.serializer.load({'id': self.document.id}, partial=True)

    def test_validate_nonexistent_document_id(self):
        self.document_manager.find_by_id.return_value = None

        with self.assertRaises(NotFound) as context:
            self.serializer.validate_id(999)

        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.description, 'Document not found')

    def test_validate_deleted_document_id(self):
        self.document.deleted_at = datetime.now(UTC)

        with self.assertRaises(NotFound) as context:
            self.serializer.validate_id(1)

        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.description, 'Document not found')

    @patch('magic.from_buffer')
    def test_valid_request_file(self, mock_magic):
        mock_magic.return_value = 'application/pdf'
        data = {'mime_type': 'application/pdf', 'file_data': b'%PDF-1.4'}

        self.assertEqual(DocumentSerializer.valid_request_file(data), data)

    @patch('magic.from_buffer')
    def test_invalid_request_file(self, mock_magic):
        mock_magic.return_value = 'text/plain'
        data = {'mime_type': 'application/pdf', 'file_data': b'Invalid content'}

        with self.assertRaises(UnprocessableEntity) as context:
            DocumentSerializer.valid_request_file(data)

        self.assertEqual(context.exception.code, 422)
        self.assertEqual(context.exception.description, 'mime_type not valid')


class TestDocumentAttachmentSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = DocumentAttachmentSerializer()

    def test_valid_as_attachment(self):
        data = {'as_attachment': 1}

        result = self.serializer.load(data)

        self.assertEqual(result['as_attachment'], 1)

    def test_invalid_as_attachment(self):
        data = {'as_attachment': 2}

        with self.assertRaises(ValidationError):
            self.serializer.load(data)

    def test_process_input(self):
        data = {'as_attachment': '1'}

        result = self.serializer.load(data)

        self.assertEqual(result['as_attachment'], 1)
