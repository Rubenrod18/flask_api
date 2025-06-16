import time

import pytest
from werkzeug.exceptions import BadRequest

from app.helpers.otp_token import OTPTokenManager


@pytest.fixture
def otp_token_manager(faker):
    return OTPTokenManager(secret_key=faker.sha256(), salt=faker.md5(), expiration=1)


class TestOTPTokenManager:
    def test_generate_token(self, faker, otp_token_manager):
        data = faker.text()

        token = otp_token_manager.generate_token(data)

        assert isinstance(token, str)

    def test_verify_valid_token(self, faker, otp_token_manager):
        data = faker.text()

        token = otp_token_manager.generate_token(data)

        assert otp_token_manager.verify_token(token) == data

    def test_verify_expired_token(self, faker, otp_token_manager):
        data = faker.text()

        token = otp_token_manager.generate_token(data)

        time.sleep(otp_token_manager.expiration + 1)

        with pytest.raises(BadRequest) as exc_info:
            otp_token_manager.verify_token(token)

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'Token expired'

    def test_verify_invalid_token(self, faker, otp_token_manager):
        invalid_token = faker.text()

        with pytest.raises(BadRequest) as exc_info:
            otp_token_manager.verify_token(invalid_token)

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'Invalid token'
