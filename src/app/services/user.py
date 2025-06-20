from flask_login import current_user

from app.extensions import db
from app.models import User, user_datastore
from app.repositories import RoleRepository, UserRepository
from app.services import base as b


class UserService(b.BaseService, b.CreationService, b.DeletionService, b.FindByIdService, b.GetService, b.SaveService):
    def __init__(self, user_repository: UserRepository = None, role_repository: RoleRepository = None):
        super().__init__(repository=user_repository or UserRepository())
        self.role_repository = role_repository or RoleRepository()

    def create(self, **kwargs) -> User:
        role = self.role_repository.find_by_id(kwargs['role_id'])
        kwargs.pop('role_id')

        # QUESTION: Shall we consider save fs_uniquifier as an uuid?
        user = self.repository.get_last_record()
        fs_uniquifier = 1 if user is None else user.id + 1

        kwargs.update({'created_by': current_user.id, 'fs_uniquifier': fs_uniquifier, 'roles': [role]})
        user = user_datastore.create_user(**kwargs)
        db.session.add(user)
        db.session.flush()

        return user

    def find_by_id(self, record_id: int, *args) -> User | None:
        return self.repository.find_by_id(record_id, *args)

    def get(self, **kwargs) -> dict:
        return self.repository.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> User:
        user = self.repository.save(record_id, **kwargs)
        db.session.flush()

        if 'role_id' in kwargs:
            user_datastore.remove_role_from_user(user, user.roles[0])
            role = self.role_repository.find_by_id(kwargs['role_id'])
            user_datastore.add_role_to_user(user, role)
            kwargs.pop('role_id')

        return user.reload()

    def delete(self, record_id: int) -> User:
        return self.repository.delete(record_id)
