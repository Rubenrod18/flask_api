from app.models.role import Role
from app.repositories.base import MySQLRepository


class RoleRepository(MySQLRepository):
    def __init__(self):
        super().__init__(model=Role)
