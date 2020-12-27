from marshmallow import ValidationError
from werkzeug.exceptions import UnprocessableEntity

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
        else:
            return self.manager.create(**data)

    def find(self, role_id: int, *args):
        try:
            self.serializer.load({'id': role_id}, partial=True)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)
        else:
            return self.manager.find(role_id)

    def save(self, role_id: int, **kwargs):
        try:
            kwargs['id'] = role_id
            serialized_data = self.serializer.load(kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)
        else:
            self.manager.save(role_id, **serialized_data)
            return self.manager.find(role_id)

    def delete(self, role_id: int):
        try:
            self.serializer.load({'id': role_id}, partial=True)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)
        else:
            return self.manager.delete(role_id)
