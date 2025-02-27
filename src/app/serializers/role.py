from marshmallow import fields, post_load, validates
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.managers import RoleManager
from app.models import Role
from app.serializers.core import ManagerMixin


class RoleSerializer(ma.SQLAlchemySchema, ManagerMixin):
    class Meta:
        model = Role
        ordered = True

    manager_classes = {'role_manager': RoleManager}

    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    label = fields.Str()
    created_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._role_manager = self.get_manager('role_manager')

    @validates('id')
    def validate_id(self, role_id):
        args = (self._role_manager.model.deleted_at.is_(None),)
        role = self._role_manager.find(role_id, *args)

        if role is None or role.deleted_at is not None:
            raise NotFound('Role not found')

    @post_load
    def sluglify_name(self, item, many, **kwargs):
        if item.get('label'):
            item['name'] = item['label'].lower().strip().replace(' ', '-')
        return item

    @validates('name')
    def validate_name(self, value, **kwargs):
        if self._role_manager.find_by_name(name=value):
            raise BadRequest('Role name already created')
