import flask_security
from flask import url_for
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from app.helpers.otp_token import OTPTokenManager
from app.managers import UserManager
from app.models import User
from app.services.task import TaskService


class AuthService:
    def __init__(self):
        self.task_service = TaskService()
        self.user_manager = UserManager()

    @staticmethod
    def _authenticate_user(user: User) -> dict:
        flask_security.login_user(user)
        user_id_str = str(user.id)

        return {
            'access_token': create_access_token(identity=user_id_str),
            'refresh_token': create_refresh_token(identity=user_id_str),
        }

    def login_user(self, user: User) -> dict:
        return self._authenticate_user(user)

    @staticmethod
    def logout_user() -> dict:
        if flask_security.current_user.is_authenticated:
            flask_security.logout_user()
            response = {}
        else:
            response = {'message': 'Already logged out'}

        return response

    def request_reset_password(self, otp_token_manager: OTPTokenManager, user: User) -> None:
        token = otp_token_manager.generate_token(user.email)
        reset_password_url = url_for('auth_reset_password_resource', token=token, _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }
        self.task_service.reset_password_email(**email_data)

    def confirm_request_reset_password(self, user: User, password: str) -> dict:
        self.user_manager.save(user.id, **{'password': password})

        return self._authenticate_user(user.reload())

    @staticmethod
    def refresh_token() -> dict:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)

        return {'access_token': access_token}
