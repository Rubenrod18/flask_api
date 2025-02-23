from flask_login import current_user
from marshmallow import EXCLUDE

from app.extensions import db
from app.managers import UserManager
from app.models import User, user_datastore
from app.serializers import SearchSerializer, UserSerializer
from app.services import RoleService
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, role_service: RoleService = None):
        super().__init__(manager=UserManager(), serializer=UserSerializer(), search_serializer=SearchSerializer())
        self.role_service = role_service or RoleService()

    def create(self, user_data) -> User:
        deserialized_data = self.serializer.load(user_data)
        role_id = deserialized_data.pop('role_id')

        user = self.manager.get_last_record()
        fs_uniquifier = 1 if user is None else user.id + 1

        deserialized_data.update({'created_by': current_user.id, 'fs_uniquifier': fs_uniquifier})
        user = user_datastore.create_user(**deserialized_data)
        db.session.add(user)
        db.session.flush()

        self.role_service.assign_role_to_user(user, role_id)

        return user

    def find(self, user_id: int, *args) -> User | None:
        self.serializer.load({'id': user_id}, partial=True)
        return self.manager.find(user_id, *args)

    def get(self, **kwargs) -> dict:
        data = self.search_serializer.load(kwargs)
        return self.manager.get(**data)

    def save(self, user_id: int, **kwargs) -> User:
        kwargs['id'] = user_id
        data = self.serializer.load(kwargs, unknown=EXCLUDE)

        user = self.manager.find(user_id)
        self.manager.save(user_id, **data)

        if 'role_id' in data:
            self.role_service.assign_role_to_user(user, data['role_id'])

        db.session.add(user)
        db.session.flush()

        return user.reload()

    def delete(self, user_id: int) -> User:
        self.serializer.load({'id': user_id}, partial=True)
        return self.manager.delete(user_id)
