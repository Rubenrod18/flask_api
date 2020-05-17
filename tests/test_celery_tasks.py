from urllib.parse import urlparse

from flask import url_for, Flask
from peewee import fn

from app.celery.tasks import create_user_email, reset_password_email, export_users_excel, export_users_pdf

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


def test_export_excel_task(app: Flask, factory: any):
    user = (UserModel.select(UserModel.id)
            .where(UserModel.email == app.config.get('TEST_USER_EMAIL'))
            .order_by(fn.Random())
            .limit(1)
            .get())

    user_list = factory('User', 10).make(to_dict=True)

    task = export_users_excel.delay(created_by=user.id, user_list=user_list)
    result = task.get()

    parse_url = urlparse(result.get('result'))

    assert result.get('current') == result.get('total')
    assert result.get('status') == 'Task completed!'
    assert parse_url.scheme and parse_url.netloc


def test_export_pdf_task(app: Flask, factory: any):
    user = (UserModel.select(UserModel.id)
            .where(UserModel.email == app.config.get('TEST_USER_EMAIL'))
            .order_by(fn.Random())
            .limit(1)
            .get())
    print(type(factory))

    user_list = factory('User', 10).make(to_dict=True)

    task = export_users_pdf.delay(created_by=user.id, user_list=user_list)
    result = task.get()

    parse_url = urlparse(result.get('result'))

    assert result.get('current') == result.get('total')
    assert result.get('status') == 'Task completed!'
    assert parse_url.scheme and parse_url.netloc
