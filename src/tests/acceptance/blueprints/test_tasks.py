import uuid
from unittest.mock import MagicMock, patch

from celery import states

from tests.base.base_api_test import BaseApiTest


class TaskEndpointTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/tasks'

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_success(self, mock_async_result):
        mock_task_result = MagicMock()
        mock_task_result.state = states.SUCCESS
        mock_task_result.info = {'current': 5, 'total': 10, 'result': 'task_completed'}
        mock_async_result.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertEqual(json_data.get('result'), mock_task_result.info.get('result'))

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_failure(self, mock_async_result_delay):
        mock_task_result = MagicMock()
        mock_task_result.state = states.FAILURE
        mock_task_result.info = {'current': 1, 'total': 1}
        mock_async_result_delay.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertIsNone(json_data.get('result'))

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_task_status_started(self, mock_async_result_delay):
        mock_task_result = MagicMock()
        mock_task_result.state = states.STARTED
        mock_task_result.info = {'current': 5, 'total': 10}
        mock_async_result_delay.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertIsNone(json_data.get('result'))

    @patch('app.blueprints.tasks.AsyncResult')
    def test_check_user_roles_in_task_status_endpoint(self, mock_async_result_delay):
        mock_task_result = MagicMock()
        mock_task_result.state = states.STARTED
        mock_task_result.info = {'current': 5, 'total': 10}
        mock_async_result_delay.return_value = mock_task_result

        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            response = self.client.get(
                f'{self.base_path}/status/{uuid.uuid4()}',
                json={},
                headers=self.build_headers(user_email=user_email),
                exp_code=response_status,
            )
            self.assertEqual(response.status_code, response_status)
