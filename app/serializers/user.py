from marshmallow import fields, validate, pre_load
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.managers import UserManager, RoleManager
from app.serializers import RoleSerializer
from app.serializers.core import TimestampField
from config import Config

user_manager = UserManager()
role_manager = RoleManager()


class VerifyRoleId(fields.Field):

    def _deserialize(self, value, *args, **kwargs):
        role = role_manager.find(value)
        if role is None:
            raise NotFound(f'Role "{value}" not found')

        if role.deleted_at is not None:
            raise BadRequest(f'Role "{value}" deleted')

        return value


class UserSerializer(ma.Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)
    created_by = fields.Nested(lambda: UserSerializer(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN,
                                 max=50),
        load_only=True
    )
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = TimestampField(dump_only=True)
    updated_at = TimestampField(dump_only=True)
    deleted_at = TimestampField(dump_only=True)
    roles = fields.List(
        fields.Nested(RoleSerializer, only=('name', 'label')),
        dump_only=True
    )

    role_id = VerifyRoleId(load_only=True)

    @staticmethod
    def valid_request_email(data: dict) -> dict:
        if user_manager.find_by_email(data.get('email')):
            raise BadRequest('User email already created')

        return data


class UserExportWordSerializer(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def convert_to_integer(self, value, many, **kwargs):
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value
