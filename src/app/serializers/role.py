from marshmallow import pre_load, validates, ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import ma
from app.models import Role
from app.models.role import ROLE_NAME_DELIMITER
from app.repositories import RoleRepository
from app.serializers.core import RepositoryMixin


class RoleSerializer(ma.SQLAlchemySchema, RepositoryMixin):
    class Meta:
        model = Role

    repository_classes = {'role_repository': RoleRepository}

    id = ma.auto_field()
    name = ma.auto_field(required=False)
    description = ma.auto_field()
    label = ma.auto_field()
    created_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._role_repository = self.get_repository('role_repository')

    def _validate_id(self, role_id: int) -> None:
        args = (self._role_repository.model.deleted_at.is_(None),)
        role = self._role_repository.find_by_id(role_id, *args)

        if role is None or role.deleted_at is not None:
            raise NotFound('Role not found')

    def _validate_name(self, value: str) -> None:
        if self._role_repository.find_by_name(name=value):
            raise ValidationError('Role name already created')

    @validates('id', 'name')
    def validate_fields(self, value: str | int, data_key: str) -> None:
        if data_key == 'id':
            self._validate_id(value)
        elif data_key == 'name':
            self._validate_name(value)

    @pre_load
    def sluglify_name(self, item, many, **kwargs):  # pylint: disable=unused-argument
        if item.get('label') and not item.get('name'):
            item['name'] = item['label'].lower().strip().replace(' ', ROLE_NAME_DELIMITER)
        return item
