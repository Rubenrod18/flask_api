from app.managers.base import BaseManager
from app.models.role import Role


class RoleManager(BaseManager):
    def __init__(self):
        super().__init__(model=Role)
