import pytest

from ._base_users_test import _TestBaseUserEndpointsTest


class TestExcelUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/xlsx'

    def test_export_excel_endpoint(self):
        response = self.client.post(self.endpoint, json={}, headers=self.build_headers(), exp_code=202)
        json_response = response.get_json()

        assert json_response.get('task')
        assert json_response.get('url')

    def test_check_user_roles_in_export_excel_endpoint(self):
        test_cases = [
            (self.admin_user.email, 202),
            (self.team_leader_user.email, 202),
            (self.worker_user.email, 202),
        ]

        for user_email, response_status in test_cases:
            self.client.post(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
