import flask_security
from flask import url_for
from flask_jwt_extended import create_access_token
from flask_security.passwordless import generate_login_token

from app.managers import UserManager
from app.serializers.auth import AuthUserConfirmResetPasswordSerializer, AuthUserLoginSerializer
from app.services.task import TaskService
from app.swagger import auth_login_sw_model, auth_user_reset_password_sw_model
from app.utils import filter_by_keys


class AuthService:
    def __init__(self):
        self.task_service = TaskService()
        self.user_manager = UserManager()
        self.auth_user_login_serializer = AuthUserLoginSerializer()
        self.auth_user_confirm_reset_password = AuthUserConfirmResetPasswordSerializer()

    def login_user(self, **kwargs) -> str:
        data = filter_by_keys(kwargs, auth_login_sw_model.keys())
        user = self.auth_user_login_serializer.load(data)
        flask_security.login_user(user)
        token = create_access_token(identity=str(user.id))
        return token

    @staticmethod
    def logout_user() -> dict:
        if flask_security.current_user.is_authenticated:
            flask_security.logout_user()
            response = {}
        else:
            response = {'message': 'Already logged out'}

        return response

    def request_reset_password(self, **kwargs) -> None:
        data = filter_by_keys(kwargs, auth_user_reset_password_sw_model.keys())
        user = self.auth_user_login_serializer.load(data, partial=True)

        token = user.get_reset_token()
        reset_password_url = url_for('auth_reset_password_resource', token=token, _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }
        self.task_service.reset_password_email(**email_data)

    def check_token_status(self, token: str) -> None:
        data = filter_by_keys(data={'token': token}, keys=['token'])
        self.auth_user_confirm_reset_password.load(data, partial=True)

    def confirm_request_reset_password(self, token: str, password: str) -> str:
        data = filter_by_keys(data={'token': token, 'password': password}, keys=['token', 'password'])
        user = self.auth_user_confirm_reset_password.load(data)

        self.user_manager.save(user.id, **{'password': password})
        return generate_login_token(user.reload())
