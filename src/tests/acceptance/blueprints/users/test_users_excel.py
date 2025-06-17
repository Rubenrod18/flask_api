import pytest

from ._base_users_test import _TestBaseUserEndpointsTest


class TestWordUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/word'

    def test_export_word_endpoint(self):
        auth_headers = self.build_headers()
        test_cases = [
            (f'{self.base_path}/word', auth_headers, {}),
            (f'{self.base_path}/word?to_pdf=1', auth_headers, {}),
            (f'{self.base_path}/word?to_pdf=0', auth_headers, {}),
        ]

        for uri, auth_headers, payload in test_cases:
            response = self.client.post(uri, json=payload, headers=auth_headers, exp_code=202)
            json_response = response.get_json()

            assert json_response.get('task')
            assert json_response.get('url')

    def test_check_user_roles_in_export_word_endpoint(self):
        test_cases = [
            (self.admin_user.email, 202),
            (self.team_leader_user.email, 202),
            (self.worker_user.email, 202),
        ]

        for user_email, response_status in test_cases:
            self.client.post(
                f'{self.base_path}/word',
                json={},
                headers=self.build_headers(user_email=user_email),
                exp_code=response_status,
            )
