from datetime import datetime, UTC
from unittest.mock import patch, PropertyMock

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.query import Query

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.helpers.sqlalchemy_query_builder import EQUAL_OP
from app.managers import DocumentManager
from app.models import Document, User
from tests.base.base_test import BaseTest


class DocumentManagerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.manager = DocumentManager()

    def test_check_manager_property(self):
        with patch.object(DocumentManager, 'model', new_callable=PropertyMock) as mock_value:
            mock_value.return_value = User
            document_manager = DocumentManager()
            self.assertEqual(type(document_manager.model), DefaultMeta)

    @patch('app.managers.document.DocumentRepository.create', autospec=True)
    def test_create_document(self, mock_repo_create):
        document_data = DocumentFactory.build_dict()
        mock_repo_create.return_value = Document(**document_data)

        document = self.manager.create(**document_data)

        mock_repo_create.assert_called_once()
        self.assertEqual(document.name, document_data['name'])
        self.assertEqual(document.size, document_data['size'])
        self.assertEqual(document.directory_path, document_data['directory_path'])
        self.assertEqual(document.internal_filename, document_data['internal_filename'])
        self.assertEqual(document.mime_type, document_data['mime_type'])
        self.assertEqual(document.created_by_user, document_data['created_by_user'])
        self.assertTrue(db.session.query(Document.id).filter().first() is None)

    @patch('app.managers.document.DocumentRepository.find', autospec=True)
    def test_save_document(self, mock_repo_find):
        document = DocumentFactory()
        document_data = DocumentFactory.build_dict()
        mock_repo_find.return_value = db.session.get(Document, document.id)

        document = self.manager.save(document.id, **document_data)

        mock_repo_find.assert_called_once()
        self.assertEqual(document.name, document_data['name'])
        self.assertEqual(document.size, document_data['size'])
        self.assertEqual(document.directory_path, document_data['directory_path'])
        self.assertEqual(document.internal_filename, document_data['internal_filename'])
        self.assertEqual(document.mime_type, document_data['mime_type'])
        self.assertEqual(document.created_by_user, document_data['created_by_user'])
        self.assertTrue(isinstance(document.created_at, datetime))
        self.assertTrue(isinstance(document.updated_at, datetime))
        self.assertIsNone(document.deleted_at)
        self.assertIsNotNone(db.session.get(Document, document.id))
        self.assertTrue(db.session.query(Document.id).filter(Document.id != document.id).first() is None)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_documents_no_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        mock_create_search_query.return_value = db.session.query(Document)
        mock_get_request_query_fields.return_value = 0, 10, []
        DocumentFactory.create_batch(5)

        all_docs = self.manager.get()

        mock_get_request_query_fields.assert_called_once()
        mock_create_search_query.assert_called_once()
        self.assertTrue(isinstance(all_docs['query'], Query))
        self.assertTrue(all(isinstance(doc, Document) for doc in all_docs['query']))
        self.assertEqual(all_docs['records_filtered'], 5)
        self.assertEqual(all_docs['records_total'], 5)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_documents_with_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        created_docs = DocumentFactory.create_batch(5)
        mock_create_search_query.return_value = db.session.query(Document).where(Document.name == created_docs[0].name)
        mock_get_request_query_fields.return_value = 0, 10, []

        filtered_docs = self.manager.get(
            **{
                'items_per_page': 10,
                'order': [],
                'page_number': 1,
                'search': [
                    {
                        'field_name': 'name',
                        'field_operator': EQUAL_OP,
                        'field_value': created_docs[0].name,
                    }
                ],
            }
        )

        self.assertTrue(isinstance(filtered_docs['query'], Query))
        self.assertTrue(all(isinstance(doc, Document) for doc in filtered_docs['query']))
        self.assertEqual(filtered_docs['records_filtered'], 1)
        self.assertEqual(filtered_docs['records_total'], 5)

    @patch('app.managers.document.DocumentRepository.delete', autospec=True)
    def test_delete_soft_document(self, mock_repo_delete):
        document = DocumentFactory(created_by_user=UserFactory(), deleted_at=None)

        def fake_delete(self, doc, force_delete=False):  # noqa  # pylint: disable=unused-argument
            doc.deleted_at = datetime.now(UTC)
            return doc

        mock_repo_delete.side_effect = fake_delete

        deleted_document = self.manager.delete(document.id)

        mock_repo_delete.assert_called_once()
        self.assertTrue(isinstance(deleted_document, Document))
        self.assertEqual(deleted_document.id, document.id)
        self.assertTrue(isinstance(deleted_document.deleted_at, datetime))

    @patch('app.managers.document.DocumentRepository.find', autospec=True)
    def test_find_by_id_document(self, mock_repo_find):
        document = DocumentFactory(created_by_user=UserFactory(), deleted_at=None)
        mock_repo_find.return_value = db.session.get(Document, document.id)

        found_document = self.manager.find_by_id(document.id)

        mock_repo_find.assert_called_once()
        self.assertTrue(isinstance(found_document, Document))
        self.assertEqual(found_document.id, document.id)
