from marshmallow import fields
from werkzeug.exceptions import BadRequest

from app.extensions import ma
from app.models.role import Role as RoleModel
from app.serializers.core import TimestampField


class RoleSerializer(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'description', 'label', 'created_at', 'updated_at',
            'deleted_at',
        )

    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    label = fields.Str()
    created_at = TimestampField()
    updated_at = TimestampField()
    deleted_at = TimestampField()

    @staticmethod
    def valid_role_name(data: dict) -> dict:
        if RoleModel.get_or_none(name=data.get('role_name')):
            raise BadRequest('Role name already created')

        return data
