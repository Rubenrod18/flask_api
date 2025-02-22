from flask_login import current_user
from marshmallow import EXCLUDE

from app.extensions import db
from app.managers import RoleManager, UserManager
from app.models import user_datastore
from app.serializers import UserSerializer
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = UserManager()
        self.role_manager = RoleManager()
        self.user_serializer = UserSerializer()

    def create(self, user_data):
        deserialized_data = self.user_serializer.load(user_data)

        role = self.role_manager.find(deserialized_data.pop('role_id'))

        user = self.manager.get_last_record()
        fs_uniquifier = 1 if user is None else user.id + 1

        deserialized_data.update({'created_by': current_user.id, 'roles': [role], 'fs_uniquifier': fs_uniquifier})
        user = user_datastore.create_user(**deserialized_data)
        db.session.add(user)
        db.session.flush()

        return user

    def find(self, user_id: int, *args):
        self.user_serializer.load({'id': user_id}, partial=True)
        return self.manager.find(user_id, *args)

    def save(self, user_id: int, **kwargs):
        kwargs['id'] = user_id
        data = self.user_serializer.load(kwargs, unknown=EXCLUDE)

        user = self.manager.find(user_id)
        self.manager.save(user_id, **data)

        if 'role_id' in data:
            user_datastore.remove_role_from_user(user, user.roles[0])
            role = self.role_manager.find(data['role_id'])
            user_datastore.add_role_to_user(user, role)

        db.session.add(user)
        db.session.flush()

        return user.reload()

    def delete(self, user_id: int):
        self.user_serializer.load({'id': user_id}, partial=True)
        return self.manager.delete(user_id)
