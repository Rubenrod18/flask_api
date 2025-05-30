from flask_jwt_extended import create_refresh_token, decode_token

from ._base_auth_integration_test import _BaseAuthIntegrationTest


class RefreshAuthIntegrationTest(_BaseAuthIntegrationTest):
    def test_user_refresh_token(self):
        refresh_token = create_refresh_token(identity=str(self.admin_user.id))

        response = self.client.post(
            f'{self.base_path}/refresh',
            json={},
            headers=self.build_headers(
                extra_headers={self.app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: f'Bearer {refresh_token}'}
            ),
        )
        json_response = response.get_json()

        self.assertEqual(200, response.status_code, json_response)
        self.assertTrue(json_response.get('access_token'))
        decoded = decode_token(json_response.get('access_token'))
        self.assertEqual(decoded['sub'], str(self.admin_user.id))
        self.assertIn('exp', decoded)
        self.assertTrue(decoded['exp'] > 0)
