import logging

from marshmallow import fields, post_load, validates
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import ma
from app.managers import RoleManager
from app.serializers.core import TimestampField

logger = logging.getLogger(__name__)
role_manager = RoleManager()


class RoleName(fields.Field):

    def _deserialize(self, value, *args, **kwargs):
        if role_manager.model.get_or_none(name=value):
            raise BadRequest('Role name already created')
        return value

    def _serialize(self, value, *args, **kwargs):
        return str(value)


class RoleSerializer(ma.Schema):
    class Meta:
        ordered = True

    id = fields.Int()
    name = fields.Str(dump_only=True)
    description = fields.Str()
    label = fields.Str()
    created_at = TimestampField(dump_only=True)
    updated_at = TimestampField(dump_only=True)
    deleted_at = TimestampField(dump_only=True)

    @validates('id')
    def validate_id(self, role_id):
        args = (role_manager.model.deleted_at.is_(None),)
        role = role_manager.find(role_id, *args)

        if role is None:
            logger.debug(f'Role "{role_id}" not found.')
            raise NotFound('Role not found')

        if role.deleted_at is not None:
            logger.debug(f'Role "{role_id}" already deleted.')
            raise NotFound('Role not found')

    @post_load
    def sluglify_name(self, item, many, **kwargs):
        if item.get('label'):
            item['name'] = item['label'].lower().strip().replace(' ', '-')
        return item

    @validates('name')
    def validate_name(self, value, **kwargs):
        if role_manager.model.get_or_none(name=value):
            raise BadRequest('Role name already created')
