from app.extensions import db
from app.managers.base import BaseManager
from app.models.role import Role


class RoleManager(BaseManager):
    def __init__(self):
        super().__init__(model=Role)

    def find_by_name(self, name: str, *args) -> Role | None:
        query = (self.model.name == name,)
        if args:
            query = query + args
        return db.session.query(self.model).filter(*query).first()
