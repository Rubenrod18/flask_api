"""Module for testing task module."""

from unittest.mock import MagicMock, patch

from app.celery.tasks import (
    create_word_and_excel_documents_task,
)
from app.database.factories.user_factory import UserFactory
from tests.base.base_test import BaseTest


class CeleryTasksTest(BaseTest):
    def test_unit_create_word_and_excel_documents_tasks_are_called(self):
        user = UserFactory()
        user_id = user.id
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        kwargs = {'created_by': user_id, 'request_data': request_data, 'to_pdf': 1}

        with (
            patch('app.celery.tasks.export_user_data_in_word_task.s') as mock_word_task_sig,
            patch('app.celery.tasks.export_user_data_in_excel_task.s') as mock_excel_task_sig,
            patch('app.celery.tasks.send_email_with_attachments_task.s') as mock_callback_sig,
            patch('app.celery.tasks.chord') as mock_chord,
            patch('app.celery.tasks.chain') as mock_chain,
        ):
            mock_chain_sig = MagicMock()
            mock_chain.return_value = mock_chain_sig

            mock_chord_instance = MagicMock()
            mock_chord.return_value = mock_chord_instance

            mock_callback_result = MagicMock()
            mock_callback_result.successful.return_value = True
            mock_callback_result.get.return_value = 'Success'
            mock_callback_result.result = 'Success'
            mock_callback_result.traceback = None
            mock_chord_instance.return_value = mock_callback_result

            create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

            mock_word_task_sig.assert_called_once_with(user_id, request_data, 1)
            mock_excel_task_sig.assert_called_once_with(user_id, request_data)
            mock_callback_sig.assert_called_once_with()

            mock_chain.assert_called_once_with(
                mock_word_task_sig.return_value,
                mock_excel_task_sig.return_value,
            )
            mock_chord.assert_called_once_with(mock_chain_sig)
            mock_chord_instance.assert_called_once_with(mock_callback_sig.return_value)

            assert mock_callback_result.successful.called
