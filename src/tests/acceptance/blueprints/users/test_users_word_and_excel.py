import pytest

from ._base_users_test import _TestBaseUserEndpointsTest


# pylint: disable=attribute-defined-outside-init
class TestWordAndExcelUserEndpoint(_TestBaseUserEndpointsTest):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/word_and_xlsx'

    def test_export_excel_and_word_endpoint(self):
        response = self.client.post(self.endpoint, json={}, headers=self.build_headers(), exp_code=202)

        assert isinstance(response.get_json(), dict)

    @pytest.mark.parametrize(
        'user_email_attr, expected_status',
        [
            ('admin_user', 202),
            ('team_leader_user', 202),
            ('worker_user', 202),
        ],
    )
    def test_check_user_roles_in_export_excel_and_word_endpoint(self, user_email_attr, expected_status):
        user_email = getattr(self, user_email_attr).email
        self.client.post(
            self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=expected_status
        )
