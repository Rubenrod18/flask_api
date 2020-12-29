"""Module for testing excel module."""
from urllib.parse import urlparse

from flask import Flask
from peewee import fn

from app.celery.excel.tasks import export_user_data_in_excel
from app.models.user import User as UserModel
from app.utils.constants import MS_EXCEL_MIME_TYPE


def test_export_excel_task(app: Flask):
    user = (UserModel.select(UserModel.id)
            .where(UserModel.email == app.config.get('TEST_USER_EMAIL'))
            .order_by(fn.Random())
            .limit(1)
            .get())

    request_data = {
        'search': [],
        'order': [
            {'field_name': 'name', 'sorting': 'asc'},
        ],
        'items_per_page': 100,
        'page_number': 1,
    }

    task = export_user_data_in_excel.delay(created_by=user.id,
                                           request_data=request_data)
    result = task.get()

    document_data = result.get('result')
    parse_url = urlparse(document_data.get('url'))

    mime_type = MS_EXCEL_MIME_TYPE

    assert result.get('current') == result.get('total')
    assert result.get('status') == 'Task completed!'

    assert user.id == document_data.get('created_by').get('id')
    assert document_data.get('name')
    assert mime_type == document_data.get('mime_type')
    assert document_data.get('size') > 0
    assert parse_url.scheme and parse_url.netloc
    assert document_data.get('created_at') == document_data.get('updated_at')
    assert document_data.get('deleted_at') is None
