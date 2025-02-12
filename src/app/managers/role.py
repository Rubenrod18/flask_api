from app.managers.base import BaseManager
from app.models.role import Role as RoleModel


class RoleManager(BaseManager):
    def __init__(self):
        super(BaseManager, self).__init__()
        self.model = RoleModel
