import logging

import flask_security
from flask_restful import Api, Resource
from flask import Blueprint, request, url_for
from flask_security import verify_password
from flask_security.passwordless import generate_login_token
from werkzeug.exceptions import Forbidden, Unauthorized

from app.models.user import User as UserModel, user_datastore
from app.celery.tasks import reset_password_email
from app.utils.cerberus_schema import MyValidator, user_login_schema, confirm_reset_password_schema
from app.utils.decorators import token_required

blueprint = Blueprint('auth', __name__, url_prefix='/auth')
api = Api(blueprint)

logger = logging.getLogger(__name__)

@api.resource('/login')
class AuthUserLoginResource(Resource):
    def post(self) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=user_login_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        user = user_datastore.find_user(**{'email': data.get('email')})

        if not user.is_active:
            raise Forbidden('User is not authorized')

        if not verify_password(data.get('password'), user.password):
            raise Unauthorized('Credentials are invalid')

        token = generate_login_token(user)
        # TODO: Pending to testing whats happen id add a new field in user model when a user is logged
        flask_security.login_user(user)
        return {
                   'token': token,
               }, 200


# TODO: Pending to implement testing
@api.resource('/logout')
class AuthUserLogoutResource(Resource):
    @token_required
    def get(self) -> tuple:
        flask_security.logout_user()

        return {}, 200


@api.resource('/reset_password')
class RequestResetPasswordResource(Resource):
    def post(self) -> tuple:
        data = request.get_json()
        email = data.get('email')

        user = UserModel.get(email=email)
        token = user.get_reset_token()

        reset_password_url = url_for('auth.resetpasswordresource', token=token, _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }

        reset_password_email.delay(email_data)

        return {}, 200


@api.resource('/reset_password/<token>')
class ResetPasswordResource(Resource):
    def get(self, token: str) -> tuple:
        user = UserModel.verify_reset_token(token)

        if not user:
            return {
                       'message': 'That is an invalid or expired token',
                   }, 403

        return {}, 200

    def post(self, token: str) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=confirm_reset_password_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        user = UserModel.verify_reset_token(token)

        if not user:
            return {
                       'message': 'That is an invalid or expired token',
                   }, 403

        user.password = data.get('password')
        user.save()

        token = generate_login_token(user)

        return {
                   'token': token,
               }, 200
