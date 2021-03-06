import logging

from flask_security import verify_password
from marshmallow import validate, fields, validates, post_load
from werkzeug.exceptions import Unauthorized, Forbidden

from app.extensions import ma
from app.managers import UserManager
from config import Config

logger = logging.getLogger(__name__)
user_manager = UserManager()


class AuthUserLoginSerializer(ma.Schema):
    email = fields.Str(load_only=True, required=True)
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN,
                                 max=50),
    )
    __user = None

    @validates('email')
    def validate_email(self, email):
        args = (user_manager.model.active == True,
                user_manager.model.deleted_at.is_null(),)
        self.__user = user_manager.find_by_email(email, *args)

        if self.__user is None:
            logger.debug(f'User "{email}" not found.')
            raise Unauthorized('Credentials invalid')

        if self.__user.active is False:
            logger.debug(f'User "{email}" not activated.')
            raise Unauthorized('Credentials invalid')

        if self.__user.deleted_at is not None:
            logger.debug(f'User "{email}" deleted.')
            raise Unauthorized('Credentials invalid')

    @validates('password')
    def validate_password(self, password):
        if not verify_password(password, self.__user.password):
            logger.debug(f'User "{self.__user.email}" password '
                         f'does not match.')
            raise Unauthorized('Credentials invalid')

    @post_load
    def make_object(self, data, **kwargs):
        return self.__user


class AuthUserConfirmResetPasswordSerializer(ma.Schema):
    token = fields.Str(required=True)
    # TODO: It could be safer if I add "password" and "confirm_password" fields.
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN,
                                 max=50),
    )

    @validates('token')
    def validate_token(self, token):
        user = user_manager.model.verify_reset_token(token)
        if not user:
            logger.debug(f'Token - User "{user.email}" is invalid')
            raise Forbidden('Invalid token')

        if user.deleted_at is not None:
            logger.debug(f'Token - User "{user.email}" already deleted')
            raise Forbidden('Invalid token')

        if not user.active:
            logger.debug(f'Token - User "{user.email}" is not active')
            raise Forbidden('Invalid token')

    @post_load
    def make_object(self, data, **kwargs):
        return user_manager.model.verify_reset_token(data.get('token'))
