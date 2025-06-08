from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Role)

    def find_by_name(self, name: str, *args) -> Role | None:
        # NOTE: It only used in seeders, I keep it here because I consider it useful.
        args += (self.model.name == name,)
        return self.find(*args)
