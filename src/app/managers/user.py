from sqlalchemy import func

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

    def random_user(self, *args) -> User | None:
        # HACK: Only used in UserSeeder, could it better move this code to the UserSeeder?
        query = (self.model.deleted_at.is_(None),)

        if args:
            query = query + args

        return (
            db.session.query(self.model)
            .join(self.model.roles)
            .filter(*query)
            .order_by(func.random())  # pylint: disable=not-callable
            .limit(1)
            .one_or_none()
        )
