import pytest

from ._base_auth_test import _TestBaseAuthEndpoints


# pylint: disable=attribute-defined-outside-init
class TestLogoutAuthEndpoint(_TestBaseAuthEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/logout'

    def test_user_logout(self):
        auth_header = self.build_headers()

        response = self.client.post(self.endpoint, json={}, headers=auth_header, exp_code=200)
        json_response = response.get_json()

        assert not json_response

    def test_user_logout_missing_auth_header(self):
        response = self.client.post(f'{self.base_path}/logout', json={}, exp_code=401)

        assert {'msg': 'Missing Authorization Header'} == response.get_json()
