import logging

import flask_security
from flask import Blueprint, request, url_for
from flask_restx import Resource
from flask_security.passwordless import generate_login_token
from marshmallow import ValidationError
from werkzeug.exceptions import (Forbidden, UnprocessableEntity)

from app.extensions import api as root_api
from app.models.user import User as UserModel
from app.celery.tasks import reset_password_email
from app.models.user_roles import user_datastore
from app.serializers import UserSerializer
from app.swagger import (auth_login_sw_model, auth_token_sw_model,
                         auth_user_reset_password_sw_model,
                         auth_user_reset_password_token_sw_model)
from app.utils.decorators import token_required

blueprint = Blueprint('auth', __name__)
api = root_api.namespace('auth', description='Authentication endpoints')
logger = logging.getLogger(__name__)


@api.route('/login')
class AuthUserLoginResource(Resource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        404: 'Not found', 422: 'Unprocessable Entity'})
    @api.expect(auth_login_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self) -> tuple:
        try:
            data = UserSerializer().validate_credentials(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user = user_datastore.find_user(**{'email': data.get('email')})
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
        # TODO: check if the user is logged
        flask_security.logout_user()
        return {}, 200


@api.route('/reset_password')
class RequestResetPasswordResource(Resource):
    @api.doc(responses={202: 'Success', 403: 'Forbidden', 404: 'Not Found',
                        422: 'Unprocessable Entity'})
    @api.expect(auth_user_reset_password_sw_model)
    def post(self) -> tuple:
        try:
            data = UserSerializer().validate_email(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user = UserModel.get(email=data['email'])
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
        # TODO: move this logic to another place
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
    @api.expect(auth_user_reset_password_token_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self, token: str) -> tuple:
        try:
            password = request.get_json().get('password')
            UserSerializer().validate_password(password)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user = UserModel.verify_reset_token(token)

        if not user:
            raise Forbidden('Invalid token')

        user.password = password
        user.save()

        token = generate_login_token(user)

        return {'token': f'Bearer {token}'}, 200
