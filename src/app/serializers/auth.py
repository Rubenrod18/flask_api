from flask_security import verify_password
from marshmallow import fields, post_load, validate, validates, validates_schema, ValidationError
from werkzeug.exceptions import Forbidden, Unauthorized

from app.extensions import ma
from app.helpers.otp_token import OTPTokenManager
from app.managers import UserManager
from app.models import User
from config import Config


class AuthUserLoginSerializer(ma.Schema):
    email = fields.Str(load_only=True, required=True)
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50),
    )
    __user = None

    def __init__(self, user_manager: UserManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager

    @validates('email')
    def validate_email(self, email):
        args = (
            self.user_manager.model.active.is_(True),
            self.user_manager.model.deleted_at.is_(None),
        )
        self.__user = self.user_manager.find_by_email(email, *args)

        if self.__user is None or self.__user.active is False or self.__user.deleted_at is not None:
            raise Unauthorized('Credentials invalid')

    @validates('password')
    def validate_password(self, password):
        if isinstance(self.__user, User) and not verify_password(password, self.__user.password):
            raise Unauthorized('Credentials invalid')

    @post_load
    def make_object(self, data, **kwargs):
        return self.__user


class AuthUserConfirmResetPasswordSerializer(ma.Schema):
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

    def __init__(self, user_manager: UserManager, otp_token_manager: OTPTokenManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_manager = user_manager
        self.otp_token_manager = otp_token_manager

    @validates('token')
    def validate_token(self, token):
        email = self.otp_token_manager.verify_token(token)
        user = self.user_manager.find_by_email(email)

        if not user or user.deleted_at is not None or not user.active:
            raise Forbidden('Invalid token')

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Passwords must match', field_name='confirm_password')

    @post_load
    def make_object(self, data, **kwargs):
        email = self.otp_token_manager.verify_token(data.get('token'))
        return self.user_manager.find_by_email(email)
