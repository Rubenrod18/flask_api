"""Module for testing task module."""

import os
from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch

from flask import url_for

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.tasks import (
    create_user_email_task,
    create_word_and_excel_documents_task,
    reset_password_email_task,
    send_email_with_attachments_task,
)
from app.celery.word.tasks import export_user_data_in_word_task
from app.database.factories.document_factory import DocumentFactory
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db, mail
from app.file_storages import LocalStorage
from app.helpers.otp_token import OTPTokenManager
from app.models import Document
from app.models.role import ADMIN_ROLE
from app.utils.constants import MS_EXCEL_MIME_TYPE, MS_WORD_MIME_TYPE, PDF_MIME_TYPE
from tests.base.base_test import BaseTest


class CeleryTasksTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.otp_token_manager = OTPTokenManager(
            secret_key=self.app.config.get('SECRET_KEY'),
            salt=self.app.config.get('SECURITY_PASSWORD_SALT'),
            expiration=self.app.config.get('RESET_TOKEN_EXPIRES'),
        )
        self.local_storage = LocalStorage()

    def test_create_user_email_task(self):
        ignore_fields = {'role', 'created_by'}
        data = UserFactory.build_dict(exclude=ignore_fields)
        self.assertTrue(create_user_email_task.apply(args=(data,)).get())

    def test_reset_password_email_task(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        with self.app.app_context():
            token = self.otp_token_manager.generate_token(user.email)
            reset_password_url = url_for('auth_reset_password_resource', token=token, _external=True)
        email_data = {'email': user.email, 'reset_password_url': reset_password_url}
        self.assertTrue(reset_password_email_task.apply(args=(email_data,)).get())

    def test_send_email_with_attachments_task(self):
        document = DocumentFactory(
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
                        'email': self.app.config.get('TEST_USER_EMAIL'),
                        'name': ADMIN_ROLE,
                    },
                }
            }
        ]

        with mail.record_messages() as outbox:
            self.assertTrue(send_email_with_attachments_task.apply(args=(args,)).get())
            self.assertEqual(len(outbox), 1)

    def test_create_word_and_excel_documents_chord_returns_success_result(self):
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

        mock_callback_result = MagicMock()
        mock_callback_result.successful.return_value = True
        mock_callback_result.result = 'Success'
        mock_callback_result.traceback = None

        with (
            patch('app.celery.tasks.chord') as mock_chord,
            patch.object(db.session, 'commit') as mock_commit,
            patch.object(db.session, 'close') as mock_close,
        ):
            mock_chord.return_value = lambda x: mock_callback_result

            create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

            mock_callback_result.successful.assert_called_once()
            mock_commit.assert_called_once()
            mock_close.assert_called_once()

    def test_create_word_and_excel_documents_chord_returns_fail_result(self):
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

        mock_callback_result = MagicMock()
        mock_callback_result.successful.return_value = False
        mock_callback_result.result = None
        mock_callback_result.traceback = None

        with (
            patch('app.celery.tasks.chord') as mock_chord,
            patch.object(db.session, 'rollback') as mock_rollback,
            patch.object(db.session, 'close') as mock_close,
        ):
            mock_chord.return_value = lambda x: mock_callback_result

            create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

            mock_callback_result.successful.assert_called_once()
            mock_rollback.assert_called_once()
            mock_close.assert_called_once()

    def test_export_user_data_in_word_task(self):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }

        test_cases = [
            ({'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}, PDF_MIME_TYPE, 'pdf'),
            ({'created_by': user.id, 'request_data': request_data, 'to_pdf': 0}, MS_WORD_MIME_TYPE, 'docx'),
        ]
        doc_id = 0

        for kwargs, mimetype, file_ext in test_cases:
            task_result = export_user_data_in_word_task.apply(kwargs=kwargs).get()
            doc_id += 1

            self.assertTrue(isinstance(task_result, dict), task_result)
            self.assertEqual(task_result.get('current'), 3, task_result)
            self.assertEqual(task_result.get('total'), 3, task_result)
            self.assertEqual(task_result.get('status'), 'Task completed!', task_result)
            self.assertTrue(isinstance(task_result.get('result'), dict), task_result)
            self.assertEqual(task_result['result'].get('id'), doc_id, task_result)
            self.assertTrue(task_result['result'].get('name').find(f'_users.{file_ext}') != -1, task_result)
            self.assertEqual(task_result['result'].get('mime_type'), mimetype, task_result)
            self.assertGreater(task_result['result'].get('size'), 0, task_result)
            self.assertIsNotNone(task_result['result'].get('created_at'), task_result)
            self.assertIsNotNone(task_result['result'].get('updated_at'), task_result)
            self.assertIsNone(task_result['result'].get('deleted_at'), task_result)
            self.assertEqual(
                task_result['result'].get('url'),
                f'http://{os.getenv("SERVER_NAME")}/api/documents/{doc_id}',
                task_result,
            )
            self.assertEqual(
                task_result['result'].get('created_by'),
                {'id': user.id, 'email': user.email, 'name': user.name, 'last_name': user.last_name},
                task_result,
            )

            query = db.session.query(Document)
            self.assertEqual(len(query.filter(Document.mime_type == mimetype).all()), 1)
            self.assertTrue(os.path.exists(query.first().get_filepath()))
            self.assertGreater(self.local_storage.get_filesize(query.first().get_filepath()), 0)

    def test_export_user_data_in_excel_task(self):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        kwargs = {'created_by': user.id, 'request_data': request_data}

        task_result = export_user_data_in_excel_task.apply(kwargs=kwargs).get()

        self.assertTrue(isinstance(task_result, dict), task_result)
        self.assertEqual(task_result.get('current'), 3, task_result)
        self.assertEqual(task_result.get('total'), 3, task_result)
        self.assertEqual(task_result.get('status'), 'Task completed!', task_result)
        self.assertTrue(isinstance(task_result.get('result'), dict), task_result)
        self.assertEqual(task_result['result'].get('id'), 1, task_result)
        self.assertTrue(task_result['result'].get('name').find('_users.xlsx') != -1, task_result)
        self.assertEqual(task_result['result'].get('mime_type'), MS_EXCEL_MIME_TYPE, task_result)
        self.assertGreater(task_result['result'].get('size'), 0, task_result)
        self.assertIsNotNone(task_result['result'].get('created_at'), task_result)
        self.assertIsNotNone(task_result['result'].get('updated_at'), task_result)
        self.assertIsNone(task_result['result'].get('deleted_at'), task_result)
        self.assertEqual(
            task_result['result'].get('url'), f'http://{os.getenv("SERVER_NAME")}/api/documents/1', task_result
        )
        self.assertEqual(
            task_result['result'].get('created_by'),
            {'id': user.id, 'email': user.email, 'name': user.name, 'last_name': user.last_name},
            task_result,
        )

        query = db.session.query(Document)
        self.assertEqual(len(query.filter().all()), 1)
        self.assertTrue(os.path.exists(query.first().get_filepath()))
        self.assertGreater(self.local_storage.get_filesize(query.first().get_filepath()), 0)

    def test_create_word_and_excel_documents_tasks_are_called(self):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        kwargs = {'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}

        # NOTE: I didn't find the way to check that the tasks called in this task
        #       ran as I expected, the only way to check it out is to do a test
        #       per each task.
        result = create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

        self.assertTrue(result)
