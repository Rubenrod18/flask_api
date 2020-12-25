import flask_security
from flask import url_for
from flask_security import verify_password
from flask_security.passwordless import generate_login_token
from marshmallow import ValidationError
from werkzeug.exceptions import UnprocessableEntity, Forbidden, Unauthorized

from app.celery.tasks import reset_password_email
from app.managers import UserManager
from app.models import user_datastore
from app.serializers import UserSerializer
from app.serializers.auth import AuthSerializer
from app.swagger import auth_login_sw_model


class AuthService(object):

    def __init__(self):
        self.auth_serializer = AuthSerializer()
        self.user_manager = UserManager()
        self.user_serializer = UserSerializer()

    def login_user(self, **kwargs) -> str:
        try:
            data = {key: value for key, value in kwargs.items()
                    if key in auth_login_sw_model.keys()}
            self.user_serializer.load(data, partial=True)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user = user_datastore.find_user(**{'email': data.get('email')})
        if (user is None
                or not verify_password(data.get('password'), user.password)):
            raise Unauthorized('Credentials invalid')

        if user.active is False:
            raise Forbidden('User not actived')

        token = generate_login_token(user)
        # TODO: Pending to testing whats happen if add a new field in user model when a user is logged
        flask_security.login_user(user)
        return token

    @staticmethod
    def logout_user():
        # TODO: check if the user is logged
        flask_security.logout_user()

    def request_reset_password(self, **kwargs):
        try:
            user = self.auth_serializer.validate_user_email(kwargs.get('email'))
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        token = user.get_reset_token()
        reset_password_url = url_for('auth_reset_password_resource',
                                     token=token,
                                     _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }
        reset_password_email.delay(email_data)

    def verify_reset_token(self, token):
        user = self.user_manager.model.verify_reset_token(token)

        if not user:
            raise Forbidden('Invalid token')

        if user.deleted_at is not None:
            raise Forbidden('User already deleted')

        if not user.active:
            raise Forbidden('User is not active')

    def confirm_request_reset_password(self, token, password) -> str:
        try:
            self.auth_serializer.validate_user_password(password)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user = self.user_manager.model.verify_reset_token(token)
        if not user:
            raise Forbidden('Invalid token')

        user.password = password
        user.save()
        return generate_login_token(user)
