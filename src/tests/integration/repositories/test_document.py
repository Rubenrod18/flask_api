from datetime import datetime

import pytest

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Document
from app.repositories.document import DocumentRepository


class TestDocumentRepository:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.repository = DocumentRepository()

    def test_create_document(self):
        document_data = DocumentFactory.build_dict()

        document = self.repository.create(**document_data)

        assert document.name == document_data['name']
        assert document.size == document_data['size']
        assert document.directory_path == document_data['directory_path']
        assert document.internal_filename == document_data['internal_filename']
        assert document.mime_type == document_data['mime_type']
        assert document.created_by_user == document_data['created_by_user']
        assert db.session.query(Document).filter_by(name=document_data['name']).one_or_none() is None

    def test_find_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user, deleted_at=None)

        test_cases = [
            ('id', (), {'id': document.id}),
            ('name', (), {'name': document.name}),
            ('size', (), {'size': document.size}),
            ('directory_path', (), {'directory_path': document.directory_path}),
            ('internal_filename', (), {'internal_filename': document.internal_filename}),
            ('mime_type', (), {'mime_type': document.mime_type}),
            ('created_by', (), {'created_by': document.created_by}),
            ('created_at', (), {'created_at': document.created_at}),
            ('updated_at', (), {'updated_at': document.updated_at}),
            ('deleted_at', (), {'deleted_at': None}),
            ('id', (Document.id == document.id,), {}),
            ('name', (Document.name == document.name,), {}),
            ('size', (Document.size == document.size,), {}),
            ('directory_path', (Document.directory_path == document.directory_path,), {}),
            ('internal_filename', (Document.internal_filename == document.internal_filename,), {}),
            ('mime_type', (Document.mime_type == document.mime_type,), {}),
            ('created_by', (Document.created_by == document.created_by,), {}),
            ('created_at', (Document.created_at == document.created_at,), {}),
            ('updated_at', (Document.updated_at == document.updated_at,), {}),
            ('deleted_at', (Document.deleted_at.is_(None),), {}),
        ]

        for description, args, kwargs in test_cases:
            result = self.repository.find(*args, **kwargs)
            assert result is not None, (description, args, kwargs)
            assert isinstance(result, Document), (description, args, kwargs)
            assert result.id == document.id, (description, args, kwargs)

    def test_delete_soft_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user)

        document = self.repository.delete(document.id)

        assert isinstance(document.deleted_at, datetime)
        assert (
            db.session.query(Document).filter_by(name=document.name, deleted_at=document.deleted_at).one_or_none()
            is None
        )

    def test_delete_hard_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user)

        with pytest.raises(NotImplementedError):
            self.repository.delete(document.id, force_delete=True)
