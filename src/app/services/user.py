from flask_login import current_user

from app.extensions import db
from app.managers import UserManager
from app.models import User, user_datastore
from app.services import RoleService
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, role_service: RoleService = None):
        super().__init__(manager=UserManager())
        self.role_service = role_service or RoleService()

    def create(self, **kwargs) -> User:
        role_id = kwargs.pop('role_id')

        user = self.manager.get_last_record()
        fs_uniquifier = 1 if user is None else user.id + 1

        kwargs.update({'created_by': current_user.id, 'fs_uniquifier': fs_uniquifier})
        user = user_datastore.create_user(**kwargs)
        db.session.add(user)
        db.session.flush()

        self.role_service.assign_role_to_user(user, role_id)

        return user

    def find(self, record_id: int, *args) -> User | None:
        return self.manager.find(record_id, *args)

    def get(self, **kwargs) -> dict:
        return self.manager.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> User:
        user = self.manager.find(record_id)
        self.manager.save(record_id, **kwargs)

        if 'role_id' in kwargs:
            self.role_service.assign_role_to_user(user, kwargs['role_id'])

        db.session.add(user)
        db.session.flush()

        return user.reload()

    def delete(self, record_id: int) -> User:
        return self.manager.delete(record_id)
