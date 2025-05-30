from ._base_auth_integration_test import _BaseAuthEndpointsTest


class LogoutAuthEndpointTest(_BaseAuthEndpointsTest):
    def setUp(self):
        super().setUp()
        self.endpoint = f'{self.base_path}/logout'

    def test_user_logout(self):
        auth_header = self.build_headers()

        response = self.client.post(self.endpoint, json={}, headers=auth_header)
        json_response = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertFalse(json_response)
