from flask_restx import ValidationError
from flask_security import verify_password
from marshmallow import fields, validate, pre_load
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound, Forbidden

from app.extensions import ma
from app.models.user import User as UserModel
from app.serializers import RoleSchema
from app.serializers.core import TimestampField
from config import Config


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'last_name', 'email', 'genre', 'birth_date', 'active',
            'created_at', 'updated_at', 'deleted_at', 'created_by', 'roles',
        )

    id = fields.Int()
    created_by = fields.Nested(lambda: UserSchema(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    password = fields.Str(
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN,
                                 max=50)
    )
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = TimestampField()
    updated_at = TimestampField()
    deleted_at = TimestampField()
    roles = fields.List(fields.Nested(RoleSchema, only=('name', 'label')))

    def validate_credentials(self, data: dict) -> dict:
        self.validate_email(data)

        user = UserModel.get_or_none(email=data.get('email'))
        if user and not verify_password(data.get('password'), user.password):
            raise Unauthorized('Credentials invalid')

        return data

    @staticmethod
    def valid_request_user(data: dict) -> dict:
        if UserModel.get_or_none(email=data.get('email')):
            raise BadRequest('User email already created')

        return data

    @staticmethod
    def validate_password(password: str) -> None:
        password_length_min = Config.SECURITY_PASSWORD_LENGTH_MIN
        password_length_max = 50

        if len(password) < password_length_min:
            raise ValidationError(f'Password must be greater '
                                  f'than {password_length_min}.')
        if len(password) > password_length_max:
            raise ValidationError(f'Password must not be greater '
                                  f'than {password_length_max}.')

    @staticmethod
    def validate_email(data: dict) -> dict:
        user = UserModel.get_or_none(email=data.get('email'))

        if user is None:
            raise NotFound('User not found')

        if not user.active:
            raise Forbidden('User not actived')

        if user.deleted_at is not None:
            raise Forbidden('User deleted')

        return data


class ExportWordInputSchema(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def convert_to_integer(self, value, many, **kwargs):
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value
