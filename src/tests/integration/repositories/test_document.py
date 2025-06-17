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

    @pytest.mark.parametrize(
        'description,args_fn,kwargs_fn',
        [
            ('id_kwarg', lambda d: (), lambda d: {'id': d.id}),
            ('name_kwarg', lambda d: (), lambda d: {'name': d.name}),
            ('size_kwarg', lambda d: (), lambda d: {'size': d.size}),
            ('directory_path_kwarg', lambda d: (), lambda d: {'directory_path': d.directory_path}),
            ('internal_filename_kwarg', lambda d: (), lambda d: {'internal_filename': d.internal_filename}),
            ('mime_type_kwarg', lambda d: (), lambda d: {'mime_type': d.mime_type}),
            ('created_by_kwarg', lambda d: (), lambda d: {'created_by': d.created_by}),
            ('created_at_kwarg', lambda d: (), lambda d: {'created_at': d.created_at}),
            ('updated_at_kwarg', lambda d: (), lambda d: {'updated_at': d.updated_at}),
            ('deleted_at_kwarg', lambda d: (), lambda d: {'deleted_at': None}),
            ('id_expr', lambda d: (Document.id == d.id,), lambda d: {}),
            ('name_expr', lambda d: (Document.name == d.name,), lambda d: {}),
            ('size_expr', lambda d: (Document.size == d.size,), lambda d: {}),
            ('directory_path_expr', lambda d: (Document.directory_path == d.directory_path,), lambda d: {}),
            ('internal_filename_expr', lambda d: (Document.internal_filename == d.internal_filename,), lambda d: {}),
            ('mime_type_expr', lambda d: (Document.mime_type == d.mime_type,), lambda d: {}),
            ('created_by_expr', lambda d: (Document.created_by == d.created_by,), lambda d: {}),
            ('created_at_expr', lambda d: (Document.created_at == d.created_at,), lambda d: {}),
            ('updated_at_expr', lambda d: (Document.updated_at == d.updated_at,), lambda d: {}),
            ('deleted_at_expr', lambda d: (Document.deleted_at.is_(None),), lambda d: {}),
        ],
    )
    def test_find_document(self, description, args_fn, kwargs_fn):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user, deleted_at=None)

        args = args_fn(document)
        kwargs = kwargs_fn(document)

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
