from app.database.factories.document_factory import DocumentFactory
from app.database.factories.user_factory import UserFactory
from app.repositories.document import DocumentRepository
from tests.base.base_test import TestBase


class TestDocumentRepository(TestBase):
    def setUp(self):
        super().setUp()
        self.repository = DocumentRepository()

    def test_create_document(self):
        document_data = DocumentFactory.build_dict()

        document = self.repository.create(**document_data)

        self.assertEqual(document.name, document_data['name'])
        self.assertEqual(document.size, document_data['size'])
        self.assertEqual(document.directory_path, document_data['directory_path'])
        self.assertEqual(document.internal_filename, document_data['internal_filename'])
        self.assertEqual(document.mime_type, document_data['mime_type'])
        self.assertEqual(document.created_by_user, document_data['created_by_user'])

    def test_find_document(self):
        user = UserFactory()
        document = DocumentFactory(created_by_user=user)

        test_cases = [
            ('name', document.name),
            ('size', document.size),
            ('directory_path', document.directory_path),
            ('internal_filename', document.internal_filename),
            ('mime_type', document.mime_type),
            ('created_by_user', document.created_by_user),
        ]

        for field_name, field_value in test_cases:
            with self.subTest(msg=field_name, field_value=field_value):
                self.assertTrue(self.repository.find(**{field_name: field_value}))
