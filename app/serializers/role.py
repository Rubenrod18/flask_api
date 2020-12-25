from marshmallow import fields
from werkzeug.exceptions import BadRequest

from app.extensions import ma
from app.managers import RoleManager
from app.serializers.core import TimestampField

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
        fields = (
            'id', 'name', 'description', 'label', 'created_at', 'updated_at',
            'deleted_at',
        )

    id = fields.Int()
    name = RoleName()
    description = fields.Str()
    label = fields.Str()
    created_at = TimestampField()
    updated_at = TimestampField()
    deleted_at = TimestampField()
