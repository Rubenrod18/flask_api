from app.extensions import db
from app.models import Role, User, user_datastore
from app.repositories import RoleRepository
from app.services import base as b


class RoleService(b.BaseService, b.CreationService, b.DeletionService, b.FindByIdService, b.GetService, b.SaveService):
    def __init__(self):
        super().__init__(repository=RoleRepository())

    def create(self, **kwargs) -> Role:
        role = self.repository.create(**kwargs)
        db.session.add(role)
        db.session.flush()
        return role

    def find_by_id(self, record_id: int, *args) -> Role | None:
        return self.repository.find_by_id(record_id)

    def get(self, **kwargs) -> dict:
        return self.repository.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> Role:
        self.repository.save(record_id, **kwargs)
        return self.repository.find_by_id(record_id)

    def delete(self, record_id: int) -> Role:
        return self.repository.delete(record_id)

    def assign_role_to_user(self, user: User, role_id: int) -> None:
        """Assigns a role to a user, replacing any existing role."""
        role = self.repository.find_by_id(role_id)
        if user.roles:
            user_datastore.remove_role_from_user(user, user.roles[0])

        user_datastore.add_role_to_user(user, role)
        db.session.add(user)
        db.session.flush()
