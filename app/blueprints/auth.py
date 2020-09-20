import logging

import flask_security
from flask import Blueprint, request, url_for
from flask_restx import Resource
from flask_security import verify_password
from flask_security.passwordless import generate_login_token
from werkzeug.exceptions import (Forbidden, Unauthorized, UnprocessableEntity,
                                 NotFound)

from app.extensions import api as root_api
from app.models.user import User as UserModel, user_datastore
from app.celery.tasks import reset_password_email
from app.utils.cerberus_schema import (MyValidator, user_login_schema,
                                       confirm_reset_password_schema)
from app.utils.decorators import token_required
from app.utils.swagger_models.auth import (AUTH_LOGIN_SW_MODEL,
                                           AUTH_TOKEN_SW_MODEL,
                                           AUTH_REQUEST_RESET_PASSWORD_SW_MODEL,
                                           AUTH_RESET_PASSWORD_SW_MODEL)

blueprint = Blueprint('auth', __name__)
api = root_api.namespace('auth', description='Authentication endpoints')
logger = logging.getLogger(__name__)


@api.route('/login')
class AuthUserLoginResource(Resource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'})
    @api.expect(AUTH_LOGIN_SW_MODEL)
    @api.marshal_with(AUTH_TOKEN_SW_MODEL)
    def post(self) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=user_login_schema())
        v.allow_unknown = False
        if not v.validate(data):
            raise UnprocessableEntity(v.errors)

        user = user_datastore.find_user(**{'email': data.get('email')})

        if not user.is_active:
            raise Forbidden('User is not authorized')

        if not verify_password(data.get('password'), user.password):
            raise Unauthorized('Credentials are invalid')

        token = generate_login_token(user)
        # TODO: Pending to testing whats happen id add a new field in user model when a user is logged
        flask_security.login_user(user)
        return {'token': f'Bearer {token}'}, 200


@api.route('/logout')
class AuthUserLogoutResource(Resource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized'},
             security='auth_token')
    @token_required
    def post(self) -> tuple:
        flask_security.logout_user()
        return {}, 200


@api.route('/reset_password')
class RequestResetPasswordResource(Resource):
    @api.doc(responses={202: 'Success', 403: 'Forbidden', 404: 'Not Found'})
    @api.expect(AUTH_REQUEST_RESET_PASSWORD_SW_MODEL)
    def post(self) -> tuple:
        data = request.get_json()
        email = data.get('email')

        user = UserModel.get_or_none(email=email)
        if user is None:
            raise NotFound('User doesn\'t exists')

        if user.deleted_at is not None:
            raise Forbidden('User already deleted')

        if not user.active:
            raise Forbidden('User is not active')

        token = user.get_reset_token()
        reset_password_url = url_for('auth_reset_password_resource',
                                     token=token,
                                     _external=True)

        email_data = {
            'email': user.email,
            'reset_password_url': reset_password_url,
        }
        reset_password_email.delay(email_data)
        return {}, 202


@api.route('/reset_password/<token>')
@api.doc(params={'token': 'A password reset token created previously'})
class ResetPasswordResource(Resource):
    @api.doc(responses={200: 'Success', 403: 'Forbidden'})
    def get(self, token: str) -> tuple:
        user = UserModel.verify_reset_token(token)

        if not user:
            raise Forbidden('Invalid token')

        if user.deleted_at is not None:
            raise Forbidden('User already deleted')

        if not user.active:
            raise Forbidden('User is not active')

        return {}, 200

    @api.doc(responses={200: 'Success', 403: 'Forbidden',
                        422: 'Unprocessable Entity'})
    @api.expect(AUTH_RESET_PASSWORD_SW_MODEL)
    @api.marshal_with(AUTH_TOKEN_SW_MODEL)
    def post(self, token: str) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=confirm_reset_password_schema())
        if not v.validate(data):
            raise UnprocessableEntity(v.errors)

        user = UserModel.verify_reset_token(token)

        if not user:
            raise Forbidden('Invalid token')

        user.password = data.get('password')
        user.save()

        token = generate_login_token(user)

        return {'token': f'Bearer {token}'}, 200
