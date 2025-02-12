import logging

from marshmallow import fields, pre_load, validate, validates
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.managers import RoleManager, UserManager
from app.serializers import RoleSerializer
from app.serializers.core import TimestampField
from config import Config

logger = logging.getLogger(__name__)
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

    id = fields.Int()
    created_by = fields.Nested(lambda: UserSerializer(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50), load_only=True)
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = TimestampField(dump_only=True)
    updated_at = TimestampField(dump_only=True)
    deleted_at = TimestampField(dump_only=True)
    roles = fields.List(fields.Nested(RoleSerializer, only=('name', 'label')), dump_only=True)

    role_id = VerifyRoleId(load_only=True)

    @validates('id')
    def validate_id(self, user_id: int):
        args = (user_manager.model.deleted_at.is_(None),)
        user = user_manager.find(user_id, *args)

        if user is None:
            logger.debug(f'User "{user_id}" not found.')
            raise NotFound('User not found')

        if user.deleted_at is not None:
            logger.debug(f'User "{user_id}" deleted.')
            raise NotFound('User not found')

    @validates('email')
    def validate_email(self, email: str):
        if user_manager.find_by_email(email):
            raise BadRequest('User email already created')


class UserExportWordSerializer(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def process_input(self, value, many, **kwargs):
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value
