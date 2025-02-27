"""Module for testing excel module."""

from urllib.parse import urlparse

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.database.factories.user_factory import UserFactory
from app.utils.constants import MS_EXCEL_MIME_TYPE
from tests.base.base_test import TestBase


class TestExcelTask(TestBase):
    def test_export_excel_task(self):
        user = UserFactory()
        user_id = user.id

        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }

        result = export_user_data_in_excel_task.apply(args=(user.id, request_data), kwargs={}).get()

        document_data = result.get('result')
        parse_url = urlparse(document_data.get('url'))

        self.assertEqual(result.get('current'), result.get('total'))
        self.assertEqual(result.get('status'), 'Task completed!')

        self.assertEqual(user_id, document_data.get('created_by').get('id'))
        self.assertTrue(document_data.get('name'))
        self.assertEqual(MS_EXCEL_MIME_TYPE, document_data.get('mime_type'))
        self.assertGreater(document_data.get('size'), 0)
        self.assertTrue(parse_url.scheme and parse_url.netloc)
        self.assertEqual(document_data.get('created_at'), document_data.get('updated_at'))
        self.assertIsNone(document_data.get('deleted_at'))
