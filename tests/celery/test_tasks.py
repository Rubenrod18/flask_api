"""Module for testing task module."""
from flask import url_for, Flask
from peewee import fn

from app.celery.tasks import (create_user_email_task, reset_password_email_task,
                              create_word_and_excel_documents_task,
                              send_email_with_attachments_task)
from app.models import Document as DocumentModel, User as UserModel


def test_create_user_email_task(factory: any):
    ignore_fields = ['role', 'created_by']
    data = factory('User').make(exclude=ignore_fields, to_dict=True)
    assert create_user_email_task(data) is True


def test_reset_password_email_task(app: Flask):
    user = (UserModel.select()
            .where(UserModel.deleted_at.is_null())
            .order_by(fn.Random())
            .limit(1)
            .get())

    with app.app_context():
        token = user.get_reset_token()
        reset_password_url = url_for('auth_reset_password_resource', token=token,
                                     _external=True)
    email_data = {'email': user.email, 'reset_password_url': reset_password_url}
    assert reset_password_email_task(email_data) is True


def test_send_email_with_attachments_task(app: Flask):
    document = (DocumentModel.select(DocumentModel.id)
                .order_by(fn.Random())
                .limit(1)
                .get())

    args = [
        {
            'result': {
                'id': document.id,
                'name': 'example.pdf',
                'internal_filename': 'example.pdf',
                'mime_type': 'application/pdf',
                'created_by': {
                    'email': app.config.get('TEST_USER_EMAIL'),
                    'name': 'admin',
                }
            }
        }
    ]

    assert send_email_with_attachments_task(args) is True


def test_create_word_and_excel_documents(app: Flask):
    user = UserModel.get(UserModel.email == app.config.get('TEST_USER_EMAIL'))

    request_data = {
        'search': [],
        'order': [
            {'field_name': 'name', 'sorting': 'asc'},
        ],
        'items_per_page': 100,
        'page_number': 1,
    }

    kwargs = {'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}
    assert create_word_and_excel_documents_task(**kwargs) is True
