import unittest
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound, UnprocessableEntity

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.models import Document
from app.repositories import DocumentRepository
from app.serializers import DocumentAttachmentSerializer, DocumentSerializer


class TestDocumentSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.user = UserFactory()
        self.document_repository = MagicMock(spec=DocumentRepository)
        self.document_repository.model = MagicMock(spec=Document)
        self.document_repository.model.deleted_at.is_.return_value = None
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
        self.serializer._document_repository = self.document_repository  # pylint: disable=protected-access
        self.document_repository.find_by_id.return_value = self.document

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.document)

        assert serialized_data['id'] == 1
        assert serialized_data['name'] == 'test_doc.pdf'
        assert serialized_data['mime_type'] == 'application/pdf'
        assert 'url' in serialized_data
        assert serialized_data['created_by']['name'] == self.user.name

    def test_validate_existing_document_id(self):
        document = self.serializer.load({'id': self.document.id}, partial=True)

        assert document['id'] == self.document.id

    def test_validate_nonexistent_document_id(self):
        self.document_repository.find_by_id.return_value = None

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(999)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'Document not found'

    def test_validate_deleted_document_id(self):
        self.document.deleted_at = datetime.now(UTC)

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(1)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'Document not found'

    @patch('magic.from_buffer')
    def test_valid_request_file(self, mock_magic):
        mock_magic.return_value = 'application/pdf'
        data = {'mime_type': 'application/pdf', 'file_data': b'%PDF-1.4'}

        assert DocumentSerializer.valid_request_file(data) == data

    @patch('magic.from_buffer')
    def test_invalid_request_file(self, mock_magic):
        mock_magic.return_value = 'text/plain'
        data = {'mime_type': 'application/pdf', 'file_data': b'Invalid content'}

        with pytest.raises(UnprocessableEntity) as exc_info:
            DocumentSerializer.valid_request_file(data)

        assert exc_info.value.code == 422
        assert exc_info.value.description == 'mime_type not valid'


class TestDocumentAttachmentSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = DocumentAttachmentSerializer()

    def test_valid_as_attachment(self):
        data = {'as_attachment': 1}

        result = self.serializer.load(data)

        assert result['as_attachment'] == 1

    def test_invalid_as_attachment(self):
        data = {'as_attachment': 2}

        with pytest.raises(ValidationError):
            self.serializer.load(data)

    def test_process_input(self):
        data = {'as_attachment': '1'}

        result = self.serializer.load(data)

        assert result['as_attachment'] == 1
