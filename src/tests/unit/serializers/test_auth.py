# pylint: disable=attribute-defined-outside-init, unused-argument
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import Forbidden, Unauthorized

from app.helpers.otp_token import OTPTokenManager
from app.models import User
from app.repositories import UserRepository
from app.serializers import AuthUserConfirmResetPasswordSerializer, AuthUserLoginSerializer
from tests.base.base_unit_test import TestBaseUnit


class TestAuthUserLoginSerializer(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.plain_password = self.faker.password()
        self.user = SimpleNamespace(
            email=self.faker.email(),
            active=True,
            deleted_at=None,
            password=self.faker.password(),
        )

        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.model = MagicMock(spec=User)
        self.user_repository.model.deleted_at.return_value = None
        self.user_repository.model.active.return_value = True
        self.user_repository.find_by_email.return_value = self.user

        self.serializer = AuthUserLoginSerializer()
        self.serializer._user_repository = self.user_repository  # noqa  # pylint: disable=protected-access

    @patch('app.serializers.auth.verify_password', autospec=True)
    def test_valid_login(self, mock_verify_password):
        mock_verify_password.return_value = True
        self.user_repository.find_by_email.return_value = self.user

        data = self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        self.user_repository.find_by_email.assert_called_once_with(
            self.user.email,
            self.user_repository.model.active.is_(True),
            self.user_repository.model.deleted_at.is_(None),
        )
        mock_verify_password.assert_called_once_with(self.plain_password, self.user.password)
        assert data == self.user

    def test_invalid_email(self):
        self.user_repository.find_by_email.return_value = None

        with pytest.raises(Unauthorized) as exc_info:
            self.serializer.load({'email': self.faker.email(), 'password': 'password'})

        assert exc_info.value.code == Unauthorized.code
        assert exc_info.value.description == 'Credentials invalid'

    def test_inactive_user(self):
        self.user.active = False
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(Unauthorized) as exc_info:
            self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        assert exc_info.value.code == Unauthorized.code
        assert exc_info.value.description == 'Credentials invalid'

    def test_deleted_user(self):
        self.user.deleted_at = '2000-01-01'
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(Unauthorized) as exc_info:
            self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        assert exc_info.value.code == Unauthorized.code
        assert exc_info.value.description == 'Credentials invalid'

    @patch('app.serializers.auth.verify_password', autospec=True)
    def test_invalid_password(self, mock_verify_password):
        mock_verify_password.return_value = False
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(Unauthorized) as exc_info:
            self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        mock_verify_password.assert_called_once_with(self.plain_password, self.user.password)
        assert exc_info.value.code == Unauthorized.code
        assert exc_info.value.description == 'Credentials invalid'

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            self.serializer.load({'password': self.plain_password})

        with pytest.raises(ValidationError):
            self.serializer.load({'email': self.user.email})


class TestAuthUserConfirmResetPasswordSerializer(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.valid_token = self.faker.sha256()
        self.valid_email = self.faker.email()
        self.valid_password = self.faker.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )
        self.user = SimpleNamespace(
            email=self.valid_email,
            active=True,
            deleted_at=None,
        )

        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.find_by_email.return_value = None
        self.otp_token_manager = MagicMock(spec=OTPTokenManager)

        self.serializer = AuthUserConfirmResetPasswordSerializer(self.otp_token_manager)
        self.serializer._user_repository = self.user_repository  # noqa  # pylint: disable=protected-access

    def test_valid_data(self):
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        validated_data = self.serializer.load(
            {
                'token': self.valid_token,
                'password': self.valid_password,
                'confirm_password': self.valid_password,
            }
        )

        assert validated_data == self.user

    def test_invalid_token(self):
        self.otp_token_manager.verify_token.side_effect = Forbidden('Invalid token')

        with pytest.raises(Forbidden) as exc_info:
            self.serializer.load(
                {
                    'token': self.faker.sha256(),
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        assert exc_info.value.code == Forbidden.code
        assert exc_info.value.description == 'Invalid token'

    def test_user_not_found(self):
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = None

        with pytest.raises(Forbidden) as exc_info:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        assert exc_info.value.code == Forbidden.code
        assert exc_info.value.description == 'Invalid token'

    def test_user_deleted(self):
        self.user.deleted_at = datetime.now(UTC)
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(Forbidden) as exc_info:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        assert exc_info.value.code == Forbidden.code
        assert exc_info.value.description == 'Invalid token'

    def test_user_not_active(self):
        self.user.active = False
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(Forbidden) as exc_info:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        assert exc_info.value.code == Forbidden.code
        assert exc_info.value.description == 'Invalid token'

    def test_mismatched_passwords(self):
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.faker.password(
                        length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
                    ),
                    'confirm_password': self.faker.password(
                        length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
                    ),
                }
            )

        assert 'Passwords must match' in str(exc_info.value)
