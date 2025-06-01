from datetime import datetime

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.query import Query

from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.helpers.sqlalchemy_query_builder import EQUAL_OP
from app.managers import DocumentManager
from app.models import Document
from tests.base.base_test import BaseTest


class DocumentManagerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.manager = DocumentManager()

    def test_check_manager_property(self):
        self.assertEqual(type(self.manager.model), DefaultMeta)

    def test_create_document(self):
        document_data = DocumentFactory.build_dict()

        document = self.manager.create(**document_data)

        self.assertEqual(document.name, document_data['name'])
        self.assertEqual(document.size, document_data['size'])
        self.assertEqual(document.directory_path, document_data['directory_path'])
        self.assertEqual(document.internal_filename, document_data['internal_filename'])
        self.assertEqual(document.mime_type, document_data['mime_type'])
        self.assertEqual(document.created_by_user, document_data['created_by_user'])
        self.assertTrue(db.session.query(Document.id).filter().first() is None)

    def test_save_document(self):
        document = DocumentFactory()
        document_data = DocumentFactory.build_dict()

        document = self.manager.save(document.id, **document_data)

        self.assertEqual(document.name, document_data['name'])
        self.assertEqual(document.size, document_data['size'])
        self.assertEqual(document.directory_path, document_data['directory_path'])
        self.assertEqual(document.internal_filename, document_data['internal_filename'])
        self.assertEqual(document.mime_type, document_data['mime_type'])
        self.assertEqual(document.created_by_user, document_data['created_by_user'])
        self.assertIsNotNone(db.session.get(Document, document.id))
        self.assertTrue(db.session.query(Document.id).filter(Document.id != document.id).first() is None)

    def test_get_documents(self):
        created_docs = DocumentFactory.create_batch(5)

        all_docs = self.manager.get()

        self.assertTrue(isinstance(all_docs['query'], Query))
        self.assertTrue(all(isinstance(doc, Document) for doc in all_docs['query']))
        self.assertEqual(all_docs['records_filtered'], 5)
        self.assertEqual(all_docs['records_total'], 5)

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

    def test_delete_soft_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user, deleted_at=None)

        deleted_document = self.manager.delete(document.id)

        self.assertTrue(isinstance(deleted_document, Document))
        self.assertEqual(deleted_document.id, document.id)
        self.assertTrue(isinstance(deleted_document.deleted_at, datetime))

    def test_find_by_id_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user, deleted_at=None)

        found_document = self.manager.find_by_id(document.id)

        self.assertTrue(isinstance(found_document, Document))
        self.assertEqual(found_document.id, document.id)
