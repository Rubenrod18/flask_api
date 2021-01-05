import flask_security
from flask import url_for
from flask_security.passwordless import generate_login_token

from app.managers import UserManager
from app.serializers.auth import (AuthUserLoginSerializer,
                                  AuthUserConfirmResetPassword)
from app.services.task import TaskService
from app.swagger import auth_login_sw_model, auth_user_reset_password_sw_model
from app.utils import filter_by_keys


class AuthService(object):

    def __init__(self):
        self.task_service = TaskService()
        self.user_manager = UserManager()
        self.auth_user_login_serializer = AuthUserLoginSerializer()
        self.auth_user_confirm_reset_password = AuthUserConfirmResetPassword()

    def login_user(self, **kwargs) -> str:
        data = filter_by_keys(kwargs, auth_login_sw_model.keys())
        user = self.auth_user_login_serializer.load(data)

        token = generate_login_token(user)
        # TODO: Pending to testing whats happen if add a new field in user model when a user is logged
        flask_security.login_user(user)
        return token

    @staticmethod
    def logout_user():
        # TODO: check if the user is logged
        flask_security.logout_user()

    def request_reset_password(self, **kwargs):
        data = filter_by_keys(kwargs, auth_user_reset_password_sw_model.keys())
        user = self.auth_user_login_serializer.load(data, partial=True)

        token = user.get_reset_token()
        reset_password_url = url_for('auth_reset_password_resource',
                                     token=token, _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }
        self.task_service.reset_password_email(**email_data)

    def verify_reset_token(self, token):
        fields = ['token']
        data = filter_by_keys({'token': token}, fields)
        self.auth_user_confirm_reset_password.load(data, partial=True)

    def confirm_request_reset_password(self, token: str, password: str) -> str:
        fields = ['token', 'password']
        data = filter_by_keys({'token': token, 'password': password},
                              fields)
        user = self.auth_user_confirm_reset_password.load(data)

        self.user_manager.save(user.id, **{'password': password})
        return generate_login_token(user.reload())
