from marshmallow import ValidationError
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from app.managers import RoleManager
from app.serializers import RoleSerializer
from app.services.base import BaseService


class RoleService(BaseService):

    def __init__(self):
        super(RoleService, self).__init__()
        self.manager = RoleManager()
        self.serializer = RoleSerializer()

    def create(self, **kwargs):
        try:
            data = self.serializer.load(kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return self.manager.create(**data)

    def find(self, role_id: int, *args):
        role = self.manager.find(role_id, *args)
        if role is None:
            raise NotFound('Role doesn\'t exist')
        return role

    def save(self, role_id: int, **kwargs):
        try:
            serialized_data = self.serializer.load(kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        role = self.manager.find(role_id)
        if role is None:
            raise BadRequest('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        self.manager.save(role_id, **serialized_data)

        args = (self.manager.model.deleted_at.is_null(),)
        return self.manager.find(role_id, *args)

    def delete(self, role_id: int):
        role = self.manager.find(role_id)
        if role is None:
            raise NotFound('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        return self.manager.delete(role_id)
