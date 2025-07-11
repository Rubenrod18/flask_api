from marshmallow import fields, pre_load, validate, validates, ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import ma
from app.models import User
from app.repositories import RoleRepository, UserRepository
from app.serializers import RoleSerializer
from app.serializers.core import RepositoryMixin
from config import Config


class VerifyRoleId(fields.Int, RepositoryMixin):
    repository_classes = {'role_repository': RoleRepository}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._role_repository = self.get_repository('role_repository')

    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        role = self._role_repository.find_by_id(value)

        if role is None or role.deleted_at is not None:
            raise NotFound('Role not found')

        return value


class UserSerializer(ma.SQLAlchemySchema, RepositoryMixin):
    class Meta:
        model = User

    repository_classes = {'user_repository': UserRepository}

    id = ma.auto_field()
    created_by = fields.Nested(lambda: UserSerializer(only=('id',)))
    name = ma.auto_field()
    last_name = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field(validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN, max=50), load_only=True)
    genre = ma.auto_field(validate=validate.OneOf(['m', 'f']))
    birth_date = ma.auto_field()
    active = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    roles = fields.List(fields.Nested(RoleSerializer, only=('name', 'label')), dump_only=True)

    role_id = VerifyRoleId(load_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_repository = self.get_repository('user_repository')

    @validates('id')
    def validate_id(self, user_id: int):
        args = (self._user_repository.model.deleted_at.is_(None),)
        user = self._user_repository.find_by_id(user_id, *args)

        if user is None or user.deleted_at is not None:
            raise NotFound('User not found')

    @validates('email')
    def validate_email(self, email: str):
        if self._user_repository.find_by_email(email):
            raise ValidationError('User email already created')


class UserExportWordSerializer(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def process_input(self, value, many, **kwargs):  # pylint: disable=unused-argument
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value
