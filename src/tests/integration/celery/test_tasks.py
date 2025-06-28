"""Module for testing task module."""

from datetime import datetime, timedelta, UTC

import pytest
from flask import current_app, url_for

from app.celery import ContextTask, make_celery
from app.celery.tasks import (
    create_user_email_task,
    reset_password_email_task,
    send_email_with_attachments_task_logic,
)
from app.database.factories.document_factory import LocalDocumentFactory
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import mail
from app.file_storages import LocalStorage
from app.helpers.otp_token import OTPTokenManager
from app.models.role import ADMIN_ROLE


# pylint: disable=attribute-defined-outside-init
class TestCeleryTasks:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.otp_token_manager = OTPTokenManager(
            secret_key=app.config.get('SECRET_KEY'),
            salt=app.config.get('SECURITY_PASSWORD_SALT'),
            expiration=app.config.get('RESET_TOKEN_EXPIRES'),
        )
        self.local_storage = LocalStorage()
        self.celery = make_celery(app)

    def test_create_user_email_task(self):
        ignore_fields = {'role', 'created_by'}
        data = UserFactory.build_dict(exclude=ignore_fields)
        assert create_user_email_task.apply(args=(data,)).get()

    def test_reset_password_email_task(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        token = self.otp_token_manager.generate_token(user.email)
        reset_password_url = url_for('auth_reset_password_resource', token=token, _external=True)
        email_data = {'email': user.email, 'reset_password_url': reset_password_url}
        assert reset_password_email_task.apply(args=(email_data,)).get()

    def test_send_email_with_attachments_task(self):
        document = LocalDocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        args = [
            {
                'result': {
                    'id': document.id,
                    'name': document.name,
                    'internal_filename': document.internal_filename,
                    'mime_type': document.mime_type,
                    'created_by': {
                        'email': current_app.config.get('TEST_USER_EMAIL'),
                        'name': ADMIN_ROLE,
                    },
                }
            }
        ]

        @self.celery.task(base=ContextTask)
        def test_task(task_data):
            return send_email_with_attachments_task_logic(task_data)

        with mail.record_messages() as outbox:
            assert test_task.apply(args=(args,)).get()
            assert len(outbox) == 1
