"""Module for testing task module."""

from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch

from celery import chain, chord
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
from tests.base.base_test import TestBase


class TestCeleryTasks(TestBase):
    def test_create_user_email_task(self):
        ignore_fields = {'role', 'created_by'}
        data = UserFactory.build_dict(exclude=ignore_fields)
        assert create_user_email_task.apply(args=(data,)).get() is True

    def test_reset_password_email_task(self):
        role = RoleFactory()
        user = UserFactory(roles=[role])

        with self.app.app_context():
            token = user.get_reset_token()
            reset_password_url = url_for('auth_reset_password_resource', token=token, _external=True)
        email_data = {'email': user.email, 'reset_password_url': reset_password_url}
        assert reset_password_email_task.apply(args=(email_data,)).get() is True

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
                        'name': 'admin',
                    },
                }
            }
        ]

        assert send_email_with_attachments_task.apply(args=(args,)).get() is True

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

    def test_create_word_and_excel_documents_tasks_are_called(self):
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
            patch.object(export_user_data_in_word_task, 'apply_async') as mock_word_task,
            patch.object(export_user_data_in_excel_task, 'apply_async') as mock_excel_task,
        ):
            mock_word_task.return_value.get.return_value = {'status': 'SUCCESS'}
            mock_excel_task.return_value.get.return_value = {'status': 'SUCCESS'}

            create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

            mock_word_task.assert_called_once()
            mock_excel_task.assert_called_once()

    # TODO: pending to resume the chord callback. I didn't find the way to check if the callback is called with chord.
    def xtest_create_word_and_excel_documents_callback_task_is_called(self):
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

        with (
            # patch.object(export_user_data_in_word_task, 'apply_async') as mock_word_task,
            # patch.object(export_user_data_in_excel_task, 'apply_async') as mock_excel_task,
            # patch.object(send_email_with_attachments_task, 'apply_async') as mock_callback,
            mail.record_messages() as outbox
        ):
            # mock_callback.return_value.get.return_value = {'status': 'SUCCESS'}

            """
            mock_word_task.return_value.get.return_value = {'status': 'SUCCESS'}
            mock_excel_task.return_value.get.return_value = {'status': 'SUCCESS'}
            mock_callback.return_value.get.return_value = {'status': 'SUCCESS'}

            create_word_and_excel_documents_task.apply(kwargs=kwargs).get()
            """

            group_tasks = [
                export_user_data_in_word_task.s(1, {}, 0),
                export_user_data_in_excel_task.s(1, {}),
            ]
            callback_task = send_email_with_attachments_task.s()

            result = chord(chain(*group_tasks))(callback_task)
            task_results = result.get()

            # print(f"Callback status: {mock_callback.called}")
            # print(f"Callback call arguments: {mock_callback.call_args}")

            # print(f'Task results: {task_results}')

            assert len(outbox) == 1
            # mock_callback.assert_called_once()
