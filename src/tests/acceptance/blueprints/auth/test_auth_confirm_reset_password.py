import os

import pytest

from app.helpers.otp_token import OTPTokenManager

from ._base_auth_test import _TestBaseAuthEndpoints


# pylint: disable=attribute-defined-outside-init
class TestConfirmResetPasswordEndpoint(_TestBaseAuthEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.otp_token_manager = OTPTokenManager(
            secret_key=self.app.config.get('SECRET_KEY'),
            salt=self.app.config.get('SECURITY_PASSWORD_SALT'),
            expiration=self.app.config.get('RESET_TOKEN_EXPIRES'),
        )
        self.token = self.otp_token_manager.generate_token(self.admin_user.email)
        self.endpoint = f'{self.base_path}/reset_password/{self.token}'

    def test_validate_reset_password(self):
        self.client.get(self.endpoint, json={})

    def test_reset_password(self):
        plain_password = os.getenv('TEST_USER_PASSWORD')
        payload = {'password': plain_password, 'confirm_password': plain_password}

        response = self.client.post(self.endpoint, json=payload, exp_code=200)
        json_response = response.get_json()

        assert json_response.get('access_token')
