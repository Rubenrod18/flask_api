"""Module for testing task module."""
from datetime import UTC, datetime, timedelta

from flask import url_for

from app.celery.tasks import (create_user_email_task, reset_password_email_task,
                              create_word_and_excel_documents_task,
                              send_email_with_attachments_task)
from database.factories.document_factory import DocumentFactory
from database.factories.role_factory import RoleFactory
from database.factories.user_factory import UserFactory
from tests.base.base_test import TestBase


class TestCeleryTasks(TestBase):
    def setUp(self):
        super(TestCeleryTasks, self).setUp()

    def test_create_user_email_task(self):
        ignore_fields = {'role', 'created_by'}
        data = UserFactory.build_dict(exclude=ignore_fields)
        assert create_user_email_task(data) is True

    def test_reset_password_email_task(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        with self.app.app_context():
            token = user.get_reset_token()
            reset_password_url = url_for('auth_reset_password_resource', token=token,
                                         _external=True)
        email_data = {'email': user.email, 'reset_password_url': reset_password_url}
        assert reset_password_email_task(email_data) is True

    def test_send_email_with_attachments_task(self):
        document = DocumentFactory(
            deleted_at=None,
            internal_filename='example.pdf',
            directory_path=self.app.config['MOCKUP_DIRECTORY'],
            created_at=datetime.now(UTC) - timedelta(days=1),
        )

        args = [
            {
                'result': {
                    'id': document.id,
                    'name': 'example.pdf',
                    'internal_filename': 'example.pdf',
                    'mime_type': 'application/pdf',
                    'created_by': {
                        'email': self.app.config.get('TEST_USER_EMAIL'),
                        'name': 'admin',
                    }
                }
            }
        ]

        assert send_email_with_attachments_task(args) is True

    # TODO: pending to add Redis as CELERY_RESULT_BACKEND config value
    def xtest_create_word_and_excel_documents(self):
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

        kwargs = {'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}
        assert create_word_and_excel_documents_task(**kwargs) is True
