from app.extensions import db
from app.managers.base import BaseManager
from app.models.user import User
from app.repositories.user import UserRepository


class UserManager(BaseManager):
    def __init__(self):
        super().__init__(repository=UserRepository)

    def find_by_email(self, email: str, *args) -> User | None:
        args += (self.model.email == email,)
        return self.repository.find(*args)

    def get_last_record(self) -> User | None:
        return db.session.query(self.model).order_by(self.model.id.desc()).limit(1).first()
