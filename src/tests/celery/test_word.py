"""Module for testing word module."""

from urllib.parse import urlparse

from app.celery.word.tasks import export_user_data_in_word_task
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.utils.constants import MS_WORD_MIME_TYPE, PDF_MIME_TYPE
from tests.base.base_test import TestBase


class TestWordTask(TestBase):
    def run_task(self, created_by: int, request_data: dict, to_pdf: int = 0):
        result = export_user_data_in_word_task.apply(args=(created_by, request_data, to_pdf)).get()

        document_data = result.get('result')
        parse_url = urlparse(document_data.get('url'))

        mime_type = PDF_MIME_TYPE if to_pdf else MS_WORD_MIME_TYPE

        self.assertEqual(result.get('current'), result.get('total'))
        self.assertEqual(result.get('status'), 'Task completed!')

        self.assertEqual(created_by, document_data.get('created_by').get('id'))
        self.assertTrue(document_data.get('name'))
        self.assertEqual(mime_type, document_data.get('mime_type'))
        self.assertGreater(document_data.get('size'), 0)
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertEqual(document_data.get('created_at'), document_data.get('updated_at'))
        self.assertIsNone(document_data.get('deleted_at'))

    def test_export_word_task(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }

        self.run_task(user.id, request_data)

    def test_export_word_task_1(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }

        self.run_task(**{'created_by': user.id, 'request_data': request_data, 'to_pdf': 1})

    def test_export_word_task_2(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        self.run_task(created_by=user.id, request_data=request_data, to_pdf=0)
