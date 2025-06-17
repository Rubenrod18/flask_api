import os

import pytest
from flask import current_app

from app.database.factories.user_factory import UserFactory
from app.services import AuthService


class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.auth_service = AuthService()

    def test_confirm_request_reset_password_check_new_user_password(self):
        with current_app.test_request_context():  # NOTE: Required by `flask_security.login_user`
            user = UserFactory()
            current_user_password_hash = user.password
            password = os.getenv('TEST_USER_PASSWORD')

            self.auth_service.confirm_request_reset_password(user, password)
            user.reload()

        assert user.password == current_user_password_hash
