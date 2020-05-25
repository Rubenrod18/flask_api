from urllib.parse import urlparse

from flask import url_for, Flask
from peewee import fn

from app.celery.tasks import create_user_email, reset_password_email
from app.celery.excel.tasks import export_user_data_in_excel
from app.celery.word.tasks import export_user_data_in_word
from app.models.user import User as UserModel


def test_create_user_email_task(factory: any):
    ignore_fields = ['role', 'created_by']
    data = factory('User').make(exclude=ignore_fields, to_dict=True)

    task = create_user_email.delay(data)
    result = task.get()

    assert True == result


def test_reset_password_email_task(app: Flask):
    user = (UserModel.select()
            .where(UserModel.deleted_at.is_null())
            .order_by(fn.Random())
            .limit(1)
            .get())

    token = user.get_reset_token()

    reset_password_url = url_for('auth.resetpasswordresource', token=token, _external=True)
    email_data = {
        'email': user.email,
        'reset_password_url': reset_password_url,
    }

    task = reset_password_email.delay(email_data)
    result = task.get()

    assert True == result


def test_export_excel_task(app: Flask):
    user = (UserModel.select(UserModel.id)
            .where(UserModel.email == app.config.get('TEST_USER_EMAIL'))
            .order_by(fn.Random())
            .limit(1)
            .get())

    request_data = {
        'search': [],
        'order': 'asc',
        'sort': 'id',
        'items_per_page': 100,
        'page_number': 1,
    }

    task = export_user_data_in_excel.delay(created_by=user.id, request_data=request_data)
    result = task.get()

    document_data = result.get('result')
    parse_url = urlparse(document_data.get('url'))

    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    assert result.get('current') == result.get('total')
    assert result.get('status') == 'Task completed!'

    assert user.id == document_data.get('created_by')
    assert document_data.get('name')
    assert mime_type == document_data.get('mime_type')
    assert document_data.get('size') > 0
    assert parse_url.scheme and parse_url.netloc
    assert document_data.get('created_at') == document_data.get('updated_at')
    assert document_data.get('deleted_at') is None


def test_export_word_task(app: Flask):
    def _run_task(created_by: int, request_data: dict, to_pdf: int = 0):
        task = export_user_data_in_word.delay(created_by, request_data, to_pdf)
        result = task.get()

        document_data = result.get('result')
        parse_url = urlparse(document_data.get('url'))

        mime_type = 'application/pdf' if to_pdf else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        assert result.get('current') == result.get('total')
        assert result.get('status') == 'Task completed!'

        assert created_by == document_data.get('created_by')
        assert document_data.get('name')
        assert mime_type == document_data.get('mime_type')
        assert document_data.get('size') > 0
        assert parse_url.scheme and parse_url.netloc
        assert document_data.get('created_at') == document_data.get('updated_at')
        assert document_data.get('deleted_at') is None

    user = UserModel.get(UserModel.email == app.config.get('TEST_USER_EMAIL'))

    request_data = {
        'search': [],
        'order': 'asc',
        'sort': 'id',
        'items_per_page': 100,
        'page_number': 1,
    }

    _run_task(user.id, request_data)
    _run_task(**{'created_by': user.id, 'request_data': request_data, 'to_pdf': 1})
    _run_task(created_by=user.id, request_data=request_data, to_pdf=0)
