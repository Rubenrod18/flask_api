from unittest.mock import MagicMock, patch

from app.celery.tasks import (
    create_word_and_excel_documents_task,
)
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.file_storages import LocalStorage
from tests.base.base_test import BaseTest


class WordAndExcelTaskTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.local_storage = LocalStorage()

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
