from unittest.mock import MagicMock, patch

from tests.base.base_api_test import TestBaseApi


# TODO: Pending to define the pending and failure tests
class TestTaskEndpoints(TestBaseApi):
    def setUp(self):
        super(TestTaskEndpoints, self).setUp()
        self.base_path = f'{self.base_path}/tasks'

    @patch('app.services.TaskService.find_by_id')
    def test_check_task_status(self, mock_find_by_id):
        mock_task_result = MagicMock()
        mock_task_result.state = 'SUCCESS'
        mock_task_result.info = {'current': 5, 'total': 10, 'result': 'task_completed'}
        mock_find_by_id.return_value = mock_task_result

        response = self.client.get(f'{self.base_path}/status/59cc0424-6f97-44c1-a253-7b4d7566e3f7',
                                   json={}, headers=self.build_headers())
        json_data = response.get_json()

        assert 200 == response.status_code
        assert isinstance(json_data, dict)
        assert json_data.get('state')
        assert json_data.get('current')
        assert json_data.get('total')
        assert json_data.get('result')
