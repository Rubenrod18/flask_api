from app.managers.base import BaseManager
from app.models import Role
from app.repositories.role import RoleRepository


class RoleManager(BaseManager):
    def __init__(self):
        super().__init__(repository=RoleRepository)

    def find_by_name(self, name: str) -> Role | None:
        return self.repository.find(*(self.model.name == name,))
