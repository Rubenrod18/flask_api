from app.extensions import db
from app.models import Role
from app.repositories import RoleRepository
from app.services import base as b


class RoleService(b.BaseService, b.CreationService, b.DeletionService, b.FindByIdService, b.GetService, b.SaveService):
    def __init__(self, role_repository: RoleRepository = None):
        super().__init__(repository=role_repository or RoleRepository())

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
        return self.repository.save(record_id, **kwargs)

    def delete(self, record_id: int) -> Role:
        return self.repository.delete(record_id)
