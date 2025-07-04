# pylint: disable=attribute-defined-outside-init, unused-argument
import os
from unittest.mock import MagicMock, patch

import pytest
from flask_security import UserMixin

from app.repositories import UserRepository
from app.services import AuthService
from tests.factories.user_factory import UserFactory


class _TestAuthBaseService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.auth_service = AuthService()


class TestLoginAuthService(_TestAuthBaseService):
    @patch('app.services.auth.flask_security.login_user', autospec=True)
    @patch('app.services.auth.create_access_token', autospec=True)
    @patch('app.services.auth.create_refresh_token', autospec=True)
    def test_login_user(self, mock_create_refresh_token, mock_create_access_token, mock_login_user):
        mock_create_refresh_token.return_value = 'refresh_token'
        mock_create_access_token.return_value = 'access_token'
        user = UserFactory()
        user_id_str = str(user.id)

        jwt = self.auth_service.login_user(user)

        mock_login_user.assert_called_once_with(user)
        mock_create_access_token.assert_called_once_with(identity=user_id_str)
        mock_create_refresh_token.assert_called_once_with(identity=user_id_str)
        assert isinstance(jwt, dict)
        assert jwt.get('access_token') == 'access_token'
        assert jwt.get('refresh_token') == 'refresh_token'


class TestLogoutAuthService(_TestAuthBaseService):
    def test_logout_user(self):
        class MockCurrentUser(UserMixin):
            is_authenticated = True

        with patch(
            'app.services.auth.flask_security', MagicMock(current_user=MockCurrentUser())
        ) as mock_flask_security:
            response = self.auth_service.logout_user()

            mock_flask_security.logout_user.assert_called_once()
            assert not response

    def test_logout_user_already_logged_out(self):
        class MockCurrentUser(UserMixin):
            is_authenticated = False

        with patch(
            'app.services.auth.flask_security', MagicMock(current_user=MockCurrentUser())
        ) as mock_flask_security:
            response = self.auth_service.logout_user()

            mock_flask_security.logout_user.assert_not_called()
            assert response == {'message': 'Already logged out'}


class TestRequestResetPasswordAuthService(_TestAuthBaseService):
    @patch('app.services.auth.OTPTokenManager', autospec=True)
    @patch('app.services.auth.url_for', autospec=True, return_value='http://new-url')
    @patch('app.services.auth.reset_password_email_task.delay', autospec=True)
    def test_request_reset_password(self, mock_task_delay, mock_url_for, mock_otp_token_manager):
        mock_otp_token_manager.generate_token.return_value = 'new_token'
        user = UserFactory()

        self.auth_service.request_reset_password(mock_otp_token_manager, user)

        mock_otp_token_manager.generate_token.assert_called_once_with(user.email)
        mock_url_for.assert_called_once_with(endpoint='auth_reset_password_resource', token='new_token', _external=True)
        mock_task_delay.assert_called_once_with({'email': user.email, 'reset_password_url': 'http://new-url'})


class TestConfirmRequestResetPasswordAuthService(_TestAuthBaseService):
    @patch('app.services.auth.flask_security.login_user', autospec=True)
    @patch('app.services.auth.create_access_token', autospec=True)
    @patch('app.services.auth.create_refresh_token', autospec=True)
    def test_confirm_request_reset_password(self, mock_create_refresh_token, mock_create_access_token, mock_login_user):
        mock_create_refresh_token.return_value = 'refresh_token'
        mock_create_access_token.return_value = 'access_token'

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = True
        auth_service = AuthService(mock_user_repo)

        user = UserFactory()
        user_id_str = str(user.id)
        password = os.getenv('TEST_USER_PASSWORD')

        jwt = auth_service.confirm_request_reset_password(user, password)

        auth_service.repository.save.assert_called_once_with(user.id, **{'password': password})
        mock_login_user.assert_called_once_with(user)
        mock_create_access_token.assert_called_once_with(identity=user_id_str)
        mock_create_refresh_token.assert_called_once_with(identity=user_id_str)
        assert isinstance(jwt, dict)
        assert jwt.get('access_token') == 'access_token'
        assert jwt.get('refresh_token') == 'refresh_token'


class TestRefreshTokenAuthService(_TestAuthBaseService):
    @patch('app.services.auth.get_jwt_identity', autospec=True)
    @patch('app.services.auth.create_access_token', autospec=True)
    def test_refresh_token(self, mock_create_access_token, mock_get_jwt_identity):
        user = UserFactory()
        mock_get_jwt_identity.return_value = user
        mock_create_access_token.return_value = 'access_token'

        response = self.auth_service.refresh_token()

        mock_get_jwt_identity.assert_called_once()
        mock_create_access_token.assert_called_once_with(identity=user)
        assert response.get('access_token') == 'access_token'
