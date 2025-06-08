from marshmallow import post_load, validates
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.models import Role
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

    @validates('id')
    def validate_id(self, role_id: int):
        args = (self._role_repository.model.deleted_at.is_(None),)
        role = self._role_repository.find_by_id(role_id, *args)

        if role is None or role.deleted_at is not None:
            raise NotFound('Role not found')

    @post_load
    def sluglify_name(self, item, many, **kwargs):  # pylint: disable=unused-argument
        if item.get('label'):
            item['name'] = item['label'].lower().strip().replace(' ', '-')
        return item

    @validates('name')
    def validate_name(self, value):
        if self._role_repository.find_by_name(name=value):
            raise BadRequest('Role name already created')
