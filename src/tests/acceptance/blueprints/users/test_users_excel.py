import pytest

from ._base_users_test import _TestBaseUserEndpointsTest


class TestWordUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/word'

    @pytest.mark.parametrize(
        'to_pdf',
        ['?to_pdf=1', '?to_pdf=0', ''],
    )
    def test_export_word_endpoint(self, to_pdf):
        response = self.client.post(
            f'{self.base_path}/word{to_pdf}', json={}, headers=self.build_headers(), exp_code=202
        )
        json_response = response.get_json()

        assert json_response.get('task')
        assert json_response.get('url')

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 202),
            ('team_leader_user', 202),
            ('worker_user', 202),
        ],
    )
    def test_check_user_roles_in_export_word_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            f'{self.base_path}/word',
            json={},
            headers=self.build_headers(user_email=user_email),
            exp_code=expected_status,
        )
