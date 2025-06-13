from ._base_auth_integration_test import _BaseAuthEndpointsTest


class LogoutAuthEndpointTest(_BaseAuthEndpointsTest):
    def setUp(self):
        super().setUp()
        self.endpoint = f'{self.base_path}/logout'

    def test_user_logout(self):
        auth_header = self.build_headers()

        response = self.client.post(self.endpoint, json={}, headers=auth_header, exp_code=200)
        json_response = response.get_json()

        self.assertFalse(json_response)

    def test_user_logout_missing_auth_header(self):
        response = self.client.post(f'{self.base_path}/logout', json={}, exp_code=401)

        self.assertDictEqual({'msg': 'Missing Authorization Header'}, response.get_json())
