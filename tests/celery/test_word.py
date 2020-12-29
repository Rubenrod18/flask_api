"""Module for testing word module."""
from urllib.parse import urlparse

from flask import Flask

from app.celery.word.tasks import export_user_data_in_word
from app.models.user import User as UserModel
from app.utils.constants import PDF_MIME_TYPE, MS_WORD_MIME_TYPE


def test_export_word_task(app: Flask):
    def _run_task(created_by: int, request_data: dict, to_pdf: int = 0):
        task = export_user_data_in_word.delay(created_by, request_data, to_pdf)
        result = task.get()

        document_data = result.get('result')
        parse_url = urlparse(document_data.get('url'))

        mime_type = PDF_MIME_TYPE if to_pdf else MS_WORD_MIME_TYPE

        assert result.get('current') == result.get('total')
        assert result.get('status') == 'Task completed!'

        assert created_by == document_data.get('created_by').get('id')
        assert document_data.get('name')
        assert mime_type == document_data.get('mime_type')
        assert document_data.get('size') > 0
        assert parse_url.scheme and parse_url.netloc
        assert document_data.get('created_at') == document_data.get('updated_at')
        assert document_data.get('deleted_at') is None

    user = UserModel.get(UserModel.email == app.config.get('TEST_USER_EMAIL'))

    request_data = {
        'search': [],
        'order': [
            {'field_name': 'name', 'sorting': 'asc'},
        ],
        'items_per_page': 100,
        'page_number': 1,
    }

    _run_task(user.id, request_data)
    _run_task(**{'created_by': user.id, 'request_data': request_data,
                 'to_pdf': 1})
    _run_task(created_by=user.id, request_data=request_data, to_pdf=0)
