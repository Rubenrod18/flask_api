from app.extensions import db
from app.managers import RoleManager
from app.models import Role, User, user_datastore
from app.services.base import BaseService


class RoleService(BaseService):
    def __init__(self):
        super().__init__(manager=RoleManager())

    def create(self, **kwargs) -> Role:
        role = self.manager.create(**kwargs)
        db.session.add(role)
        db.session.flush()
        return role

    def find_by_id(self, record_id: int, *args) -> Role | None:
        return self.manager.find_by_id(record_id)

    def get(self, **kwargs) -> dict:
        return self.manager.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> Role:
        self.manager.save(record_id, **kwargs)
        return self.manager.find_by_id(record_id)

    def delete(self, record_id: int) -> Role:
        return self.manager.delete(record_id)

    def assign_role_to_user(self, user: User, role_id: int) -> None:
        """Assigns a role to a user, replacing any existing role."""
        role = self.manager.find_by_id(role_id)
        if user.roles:
            user_datastore.remove_role_from_user(user, user.roles[0])

        user_datastore.add_role_to_user(user, role)
        db.session.add(user)
        db.session.flush()
