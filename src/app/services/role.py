from app.managers import RoleManager
from app.serializers import RoleSerializer
from app.services.base import BaseService


class RoleService(BaseService):
    def __init__(self):
        super().__init__()
        self.manager = RoleManager()
        self.serializer = RoleSerializer()

    def create(self, **kwargs):
        data = self.serializer.load(kwargs)
        return self.manager.create(**data)

    def find(self, role_id: int, *args):
        self.serializer.load({'id': role_id}, partial=True)
        return self.manager.find(role_id)

    def save(self, role_id: int, **kwargs):
        kwargs['id'] = role_id
        serialized_data = self.serializer.load(kwargs)

        self.manager.save(role_id, **serialized_data)
        return self.manager.find(role_id)

    def delete(self, role_id: int):
        self.serializer.load({'id': role_id}, partial=True)
        return self.manager.delete(role_id)
