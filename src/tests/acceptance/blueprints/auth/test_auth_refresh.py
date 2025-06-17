from flask_jwt_extended import create_refresh_token, decode_token

from ._base_auth_test import _TestBaseAuthEndpoints


class TestRefreshAuthEndpoint(_TestBaseAuthEndpoints):
    def test_user_refresh_token(self):
        refresh_token = create_refresh_token(identity=str(self.admin_user.id))

        response = self.client.post(
            f'{self.base_path}/refresh',
            json={},
            headers=self.build_headers(
                extra_headers={self.app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: f'Bearer {refresh_token}'}
            ),
            exp_code=200,
        )
        json_response = response.get_json()

        assert json_response.get('access_token')
        decoded = decode_token(json_response.get('access_token'))
        assert decoded['sub'], str(self.admin_user.id)
        assert 'exp' in decoded
        assert decoded['exp'] > 0
