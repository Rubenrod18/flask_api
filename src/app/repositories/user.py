from app.extensions import db
from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=User)

    def create(self, **kwargs) -> db.Model:
        # NOTE: The creation of users are managed by the package flask-security
        raise NotImplementedError

    def find_by_email(self, email: str, *args) -> User | None:
        args += (self.model.email == email,)
        return self.find(*args)

    def get_last_record(self) -> User | None:
        return db.session.query(self.model).order_by(self.model.id.desc()).limit(1).first()
