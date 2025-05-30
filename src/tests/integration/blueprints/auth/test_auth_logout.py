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
