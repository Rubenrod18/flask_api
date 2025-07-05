from flask_security import verify_password
from marshmallow import fields, post_load, validate, validates, validates_schema, ValidationError
from werkzeug.exceptions import Forbidden, Unauthorized

from app.extensions import ma
from app.helpers.otp_token import OTPTokenManager
from app.repositories import UserRepository
from app.serializers.core import RepositoryMixin
from config import Config


class AuthUserLoginSerializer(ma.Schema, RepositoryMixin):
    repository_classes = {'user_repository': UserRepository}

    email = fields.Str(load_only=True, required=True)
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50),
    )
    _user = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_repository = self.get_repository('user_repository')

    @validates('email')
    def validate_email(self, email):
        args = (
            self._user_repository.model.active.is_(True),
            self._user_repository.model.deleted_at.is_(None),
        )
        self._user = self._user_repository.find_by_email(email, *args)

        if self._user is None or self._user.active is False or self._user.deleted_at is not None:
            raise Unauthorized('Credentials invalid')

    @validates('password')
    def validate_password(self, password):
        if self._user and not verify_password(password, self._user.password):
            raise Unauthorized('Credentials invalid')

    @post_load
    def make_object(self, data, **kwargs):  # pylint: disable=unused-argument
        return self._user


class AuthUserConfirmResetPasswordSerializer(ma.Schema, RepositoryMixin):
    repository_classes = {'user_repository': UserRepository}

    token = fields.Str(required=True)
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50),
    )
    confirm_password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50),
    )

    def __init__(self, otp_token_manager: OTPTokenManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_repository = self.get_repository('user_repository')
        self.otp_token_manager = otp_token_manager

    @validates('token')
    def validate_token(self, token):
        email = self.otp_token_manager.verify_token(token)
        user = self._user_repository.find_by_email(email)

        if not user or user.deleted_at is not None or not user.active:
            raise Forbidden('Invalid token')

    @validates_schema
    def validate_passwords(self, data, **kwargs):  # pylint: disable=unused-argument
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Passwords must match', field_name='confirm_password')

    @post_load
    def make_object(self, data, **kwargs):  # pylint: disable=unused-argument
        email = self.otp_token_manager.verify_token(data.get('token'))
        return self._user_repository.find_by_email(email)
