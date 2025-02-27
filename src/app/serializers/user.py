from marshmallow import fields, pre_load, validate, validates
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.managers import RoleManager, UserManager
from app.models import User
from app.serializers import RoleSerializer
from app.serializers.core import ManagerMixin
from config import Config


class VerifyRoleId(fields.Int, ManagerMixin):
    _manager_classes = {'role_manager': RoleManager}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._role_manager = self._get_manager('role_manager')

    def _deserialize(self, value, *args, **kwargs):
        role = self._role_manager.find(value)

        if role is None or role.deleted_at is not None:
            raise NotFound('Role not found')

        return value


class UserSerializer(ma.SQLAlchemySchema, ManagerMixin):
    class Meta:
        model = User
        ordered = True

    _manager_classes = {'user_manager': UserManager}

    id = fields.Int()
    created_by = fields.Nested(lambda: UserSerializer(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50), load_only=True)
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    roles = fields.List(fields.Nested(RoleSerializer, only=('name', 'label')), dump_only=True)

    role_id = VerifyRoleId(load_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_manager = self._get_manager('user_manager')

    @validates('id')
    def validate_id(self, user_id: int):
        args = (self._user_manager.model.deleted_at.is_(None),)
        user = self._user_manager.find(user_id, *args)

        if user is None or user.deleted_at is not None:
            raise NotFound('User not found')

    @validates('email')
    def validate_email(self, email: str):
        if self._user_manager.find_by_email(email):
            raise BadRequest('User email already created')


class UserExportWordSerializer(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def process_input(self, value, many, **kwargs):
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value
