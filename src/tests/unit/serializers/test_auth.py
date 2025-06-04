from unittest.mock import MagicMock

from marshmallow import ValidationError
from werkzeug.exceptions import Forbidden, Unauthorized

from app.database.factories.user_factory import UserFactory
from app.helpers.otp_token import OTPTokenManager
from app.models import User
from app.repositories import UserRepository
from app.serializers import AuthUserConfirmResetPasswordSerializer, AuthUserLoginSerializer
from tests.base.base_test import BaseTest


class AuthUserLoginSerializerTest(BaseTest):
    def setUp(self):
        super().setUp()

        self.plain_password = self.faker.password()
        self.user = UserFactory(
            email=self.faker.email(), password=User.ensure_password(self.plain_password), active=True, deleted_at=None
        )

        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.model = MagicMock(spec=User)
        self.user_repository.model.deleted_at.return_value = None
        self.user_repository.model.active.return_value = True
        self.user_repository.find_by_email.return_value = self.user

        self.serializer = AuthUserLoginSerializer(user_repository=self.user_repository)

    def test_valid_login(self):
        self.user_repository.find_by_email.return_value = self.user

        data = self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        self.assertEqual(data, self.user)
        self.user_repository.find_by_email.assert_called_once_with(
            self.user.email,
            self.user_repository.model.active.is_(True),
            self.user_repository.model.deleted_at.is_(None),
        )

    def test_invalid_email(self):
        self.user_repository.find_by_email.return_value = None

        with self.assertRaises(Unauthorized) as context:
            self.serializer.load({'email': self.faker.email(), 'password': 'password'})

        self.assertEqual(context.exception.code, Unauthorized.code)
        self.assertEqual(context.exception.description, 'Credentials invalid')

    def test_inactive_user(self):
        self.user.active = False
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(Unauthorized) as context:
            self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        self.assertEqual(context.exception.code, Unauthorized.code)
        self.assertEqual(context.exception.description, 'Credentials invalid')

    def test_deleted_user(self):
        self.user.deleted_at = '2000-01-01'
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(Unauthorized) as context:
            self.serializer.load({'email': self.user.email, 'password': self.plain_password})

        self.assertEqual(context.exception.code, Unauthorized.code)
        self.assertEqual(context.exception.description, 'Credentials invalid')

    def test_invalid_password(self):
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(Unauthorized) as context:
            self.serializer.load({'email': self.user.email, 'password': 'wrongpassword'})

        self.assertEqual(context.exception.code, Unauthorized.code)
        self.assertEqual(context.exception.description, 'Credentials invalid')

    def test_missing_fields(self):
        with self.assertRaises(ValidationError):
            self.serializer.load({'password': self.plain_password})

        with self.assertRaises(ValidationError):
            self.serializer.load({'email': self.user.email})


class AuthUserConfirmResetPasswordSerializerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.valid_token = self.faker.sha256()
        self.valid_email = self.faker.email()
        self.valid_password = self.faker.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )
        self.user = UserFactory(email=self.valid_email, active=True, deleted_at=None)

        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.find_by_email.return_value = None
        self.otp_token_manager = MagicMock(spec=OTPTokenManager)

        self.serializer = AuthUserConfirmResetPasswordSerializer(self.user_repository, self.otp_token_manager)

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

        self.assertEqual(validated_data, self.user)

    def test_invalid_token(self):
        self.otp_token_manager.verify_token.side_effect = Forbidden('Invalid token')

        with self.assertRaises(Forbidden) as context:
            self.serializer.load(
                {
                    'token': self.faker.sha256(),
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        self.assertEqual(context.exception.code, Forbidden.code)
        self.assertEqual(context.exception.description, 'Invalid token')

    def test_user_not_found(self):
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = None

        with self.assertRaises(Forbidden) as context:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        self.assertEqual(context.exception.code, Forbidden.code)
        self.assertEqual(context.exception.description, 'Invalid token')

    def test_user_deleted(self):
        self.user.deleted_at = '2024-01-01'
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(Forbidden) as context:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        self.assertEqual(context.exception.code, Forbidden.code)
        self.assertEqual(context.exception.description, 'Invalid token')

    def test_user_not_active(self):
        self.user.active = False
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(Forbidden) as context:
            self.serializer.load(
                {
                    'token': self.valid_token,
                    'password': self.valid_password,
                    'confirm_password': self.valid_password,
                }
            )

        self.assertEqual(context.exception.code, Forbidden.code)
        self.assertEqual(context.exception.description, 'Invalid token')

    def test_mismatched_passwords(self):
        self.otp_token_manager.verify_token.return_value = self.valid_email
        self.user_repository.find_by_email.return_value = self.user

        with self.assertRaises(ValidationError) as context:
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

        self.assertIn('Passwords must match', str(context.exception))
