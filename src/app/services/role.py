from abc import ABC

from app.extensions import db
from app.managers import RoleManager
from app.models import Role, User, user_datastore
from app.serializers import RoleSerializer, SearchSerializer
from app.services.base import BaseService


class RoleService(BaseService, ABC):
    def __init__(self):
        super().__init__(manager=RoleManager(), serializer=RoleSerializer(), search_serializer=SearchSerializer())

    def create(self, **kwargs) -> Role:
        data = self.serializer.load(kwargs)
        return self.manager.create(**data)

    def find(self, role_id: int, *args) -> Role | None:
        self.serializer.load({'id': role_id}, partial=True)
        return self.manager.find(role_id)

    def get(self, **kwargs) -> dict:
        data = self.search_serializer.load(kwargs)
        return self.manager.get(**data)

    def save(self, role_id: int, **kwargs) -> Role:
        kwargs['id'] = role_id
        serialized_data = self.serializer.load(kwargs)

        self.manager.save(role_id, **serialized_data)
        return self.manager.find(role_id)

    def delete(self, role_id: int) -> Role:
        self.serializer.load({'id': role_id}, partial=True)
        return self.manager.delete(role_id)

    def assign_role_to_user(self, user: User, role_id: int) -> None:
        """Assigns a role to a user, replacing any existing role."""
        role = self.manager.find(role_id)
        if user.roles:
            user_datastore.remove_role_from_user(user, user.roles[0])

        user_datastore.add_role_to_user(user, role)
        db.session.add(user)
        db.session.flush()
