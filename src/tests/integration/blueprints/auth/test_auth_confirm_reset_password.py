import os

from app.helpers.otp_token import OTPTokenManager

from ._base_auth_integration_test import _BaseAuthIntegrationTest


class ConfirmResetPasswordAuthIntegrationTest(_BaseAuthIntegrationTest):
    def setUp(self):
        super().setUp()
        self.otp_token_manager = OTPTokenManager(
            secret_key=self.app.config.get('SECRET_KEY'),
            salt=self.app.config.get('SECURITY_PASSWORD_SALT'),
            expiration=self.app.config.get('RESET_TOKEN_EXPIRES'),
        )
        self.token = self.otp_token_manager.generate_token(self.admin_user.email)
        self.endpoint = f'{self.base_path}/reset_password/{self.token}'

    def test_validate_reset_password(self):
        response = self.client.get(self.endpoint, json={})

        self.assertEqual(200, response.status_code)

    def test_reset_password(self):
        plain_password = os.getenv('TEST_USER_PASSWORD')
        payload = {'password': plain_password, 'confirm_password': plain_password}

        response = self.client.post(self.endpoint, json=payload)
        json_response = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertTrue(json_response.get('access_token'))
