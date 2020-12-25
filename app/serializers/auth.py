from flask_security import verify_password
from marshmallow import ValidationError
from werkzeug.exceptions import Unauthorized, NotFound, Forbidden

from app.extensions import ma
from app.managers import UserManager
from config import Config

user_manager = UserManager()


class AuthSerializer(ma.Schema):

    @classmethod
    def validate_user_credentials(cls, data: dict) -> dict:
        user = cls.validate_user_email(data.get('email'))
        if user and not verify_password(data.get('password'), user.password):
            raise Unauthorized('Credentials invalid')

        return data

    @staticmethod
    def validate_user_email(email: str) -> user_manager.model:
        user = user_manager.find_by_email(email)

        if user is None:
            raise NotFound(f'User "{email}" not found')

        if not user.active:
            raise Forbidden(f'User "{email}" not actived')

        if user.deleted_at is not None:
            raise Forbidden(f'User "{email}" deleted')

        return user

    @staticmethod
    def validate_user_password(password: str) -> None:
        password_length_min = Config.SECURITY_PASSWORD_LENGTH_MIN
        password_length_max = 50

        if len(password) < password_length_min:
            raise ValidationError(f'Password must be greater '
                                  f'than {password_length_min}.')
        if len(password) > password_length_max:
            raise ValidationError(f'Password must not be greater '
                                  f'than {password_length_max}.')
