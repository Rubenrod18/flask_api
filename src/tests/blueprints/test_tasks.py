import uuid
from unittest.mock import MagicMock, patch

from celery import states

from tests.base.base_api_test import TestBaseApi


class TestTaskEndpoints(TestBaseApi):
    def setUp(self):
        super(TestTaskEndpoints, self).setUp()
        self.base_path = f'{self.base_path}/tasks'

    @patch('app.services.task.AsyncResult')
    def test_check_task_status_success(self, mock_async_result):
        mock_task_result = MagicMock()
        mock_task_result.state = states.SUCCESS
        mock_task_result.info = {'current': 5, 'total': 10, 'result': 'task_completed'}
        mock_async_result.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertEqual(json_data.get('result'), mock_task_result.info.get('result'))

    @patch('app.services.task.AsyncResult')
    def test_check_task_status_failure(self, mock_async_result):
        mock_task_result = MagicMock()
        mock_task_result.state = states.FAILURE
        mock_task_result.info = {'current': 1, 'total': 1}
        mock_async_result.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertIsNone(json_data.get('result'))

    @patch('app.services.task.AsyncResult')
    def test_check_task_status_started(self, mock_async_result):
        mock_task_result = MagicMock()
        mock_task_result.state = states.STARTED
        mock_task_result.info = {'current': 5, 'total': 10}
        mock_async_result.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/{uuid.uuid4()}', json={}, headers=self.build_headers())
        json_data = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertTrue(isinstance(json_data, dict))
        self.assertEqual(json_data.get('state'), mock_task_result.state)
        self.assertEqual(json_data.get('current'), mock_task_result.info.get('current'))
        self.assertEqual(json_data.get('total'), mock_task_result.info.get('total'))
        self.assertIsNone(json_data.get('result'))
