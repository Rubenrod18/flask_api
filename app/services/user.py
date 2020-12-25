from flask_login import current_user
from marshmallow import ValidationError, EXCLUDE
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from app.extensions import db_wrapper
from app.managers import UserManager, RoleManager
from app.models import user_datastore
from app.serializers import UserSerializer
from app.services.base import BaseService


class UserService(BaseService):

    def __init__(self, *args, **kwargs):
        super(UserService, self).__init__(*args, **kwargs)
        self.manager = UserManager()
        self.role_manager = RoleManager()
        self.user_serializer = UserSerializer()

    def create(self, user_data):
        try:
            deserialized_data = self.user_serializer.load(user_data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        with db_wrapper.database.atomic():
            role = self.role_manager.find(deserialized_data['role_id'])
            deserialized_data.update({'created_by': current_user.id,
                                      'roles': [role]})
            user = user_datastore.create_user(**deserialized_data)

        return user

    def find(self, user_id: int, *args):
        user = self.manager.find(user_id, *args)
        if user is None:
            raise NotFound('User doesn\'t exist')
        return user

    def save(self, user_id: int, **kwargs):
        user = self.manager.find(user_id)
        if user is None:
            raise BadRequest('User doesn\'t exist')

        if user.deleted_at is not None:
            raise BadRequest('User already deleted')

        try:
            data = self.user_serializer.load(kwargs, unknown=EXCLUDE)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        with db_wrapper.database.atomic():
            self.manager.save(user_id, **data)

            if 'role_id' in data:
                user_datastore.remove_role_from_user(user, user.roles[0])
                role = self.role_manager.find(data['role_id'])
                user_datastore.add_role_to_user(user, role)

        args = (self.manager.model.deleted_at.is_null(),)
        user = self.manager.find(user_id, *args)
        return user

    def delete(self, user_id: int):
        user = self.manager.find(user_id)
        if user is None:
            raise NotFound('User doesn\'t exist')

        if user.deleted_at is not None:
            raise BadRequest('User already deleted')

        return self.manager.delete(user_id)
