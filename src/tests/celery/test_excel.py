"""Module for testing excel module."""
from urllib.parse import urlparse

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.utils.constants import MS_EXCEL_MIME_TYPE
from database.factories.role_factory import RoleFactory
from database.factories.user_factory import UserFactory
from tests.base.base_test import TestBase


class TestExcelTask(TestBase):
    def setUp(self):
        super(TestExcelTask, self).setUp()

    def test_export_excel_task(self):
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

        result = export_user_data_in_excel_task(created_by=user.id, request_data=request_data)

        document_data = result.get('result')
        parse_url = urlparse(document_data.get('url'))

        assert result.get('current') == result.get('total')
        assert result.get('status') == 'Task completed!'

        assert user.id == document_data.get('created_by').get('id')
        assert document_data.get('name')
        assert MS_EXCEL_MIME_TYPE == document_data.get('mime_type')
        assert document_data.get('size') > 0
        assert parse_url.scheme and parse_url.netloc
        assert document_data.get('created_at') == document_data.get('updated_at')
        assert document_data.get('deleted_at') is None