import time

import pytest
from werkzeug.exceptions import BadRequest

from app.helpers.otp_token import OTPTokenManager


# pylint: disable=attribute-defined-outside-init
class TestOTPTokenManager:
    @pytest.fixture(autouse=True)
    def setup(self, faker):
        self.faker = faker
        self.otp_token_manager = OTPTokenManager(secret_key=faker.sha256(), salt=faker.md5(), expiration=1)

    def test_generate_token(self):
        data = self.faker.text()

        token = self.otp_token_manager.generate_token(data)

        assert isinstance(token, str)

    def test_verify_valid_token(self):
        data = self.faker.text()

        token = self.otp_token_manager.generate_token(data)

        assert self.otp_token_manager.verify_token(token) == data

    def test_verify_expired_token(self):
        data = self.faker.text()

        token = self.otp_token_manager.generate_token(data)

        time.sleep(self.otp_token_manager.expiration + 1)

        with pytest.raises(BadRequest) as exc_info:
            self.otp_token_manager.verify_token(token)

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'Token expired'

    def test_verify_invalid_token(self):
        invalid_token = self.faker.text()

        with pytest.raises(BadRequest) as exc_info:
            self.otp_token_manager.verify_token(invalid_token)

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'Invalid token'
