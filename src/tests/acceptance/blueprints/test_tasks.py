import uuid
from unittest.mock import MagicMock, patch

import pytest
from celery import states

from tests.base.base_api_test import TestBaseApi


class TestTaskEndpoint(TestBaseApi):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.base_path = f'{self.base_path}/tasks'

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_success(self, mock_async_result):
        mock_task_result = MagicMock()
        mock_task_result.state = states.SUCCESS
        mock_task_result.info = {'current': 5, 'total': 10, 'result': 'task_completed'}
        mock_async_result.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        assert isinstance(json_data, dict)
        assert json_data.get('state'), mock_task_result.state
        assert json_data.get('current'), mock_task_result.info.get('current')
        assert json_data.get('total'), mock_task_result.info.get('total')
        assert json_data.get('result'), mock_task_result.info.get('result')

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_failure(self, mock_async_result_delay):
        mock_task_result = MagicMock()
        mock_task_result.state = states.FAILURE
        mock_task_result.info = {'current': 1, 'total': 1}
        mock_async_result_delay.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        assert isinstance(json_data, dict)
        assert json_data.get('state'), mock_task_result.state
        assert json_data.get('current'), mock_task_result.info.get('current')
        assert json_data.get('total'), mock_task_result.info.get('total')
        assert json_data.get('result') is None

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_started(self, mock_async_result_delay):
        mock_task_result = MagicMock()
        mock_task_result.state = states.STARTED
        mock_task_result.info = {'current': 5, 'total': 10}
        mock_async_result_delay.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        assert isinstance(json_data, dict)
        assert json_data.get('state'), mock_task_result.state
        assert json_data.get('current'), mock_task_result.info.get('current')
        assert json_data.get('total'), mock_task_result.info.get('total')
        assert json_data.get('result') is None

    @patch('app.blueprints.tasks.AsyncResult')
    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 200),
            ('team_leader_user', 200),
            ('worker_user', 200),
        ],
    )
    def test_check_user_roles_in_task_status_endpoint(self, mock_async_result_delay, user_email_attr, expected_status):
        mock_task_result = MagicMock()
        mock_task_result.state = states.STARTED
        mock_task_result.info = {'current': 5, 'total': 10}
        mock_async_result_delay.return_value = mock_task_result

        user_email = getattr(self, user_email_attr).email

        self.client.get(
            f'{self.base_path}/status/{uuid.uuid4()}',
            json={},
            headers=self.build_headers(user_email=user_email),
            exp_code=expected_status,
        )
