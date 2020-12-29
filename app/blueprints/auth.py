from flask import Blueprint, request
from flask_restx import Resource

from app.extensions import api as root_api
from app.services.auth import AuthService
from app.swagger import (auth_login_sw_model, auth_token_sw_model,
                         auth_user_reset_password_sw_model,
                         auth_user_reset_password_token_sw_model)
from app.utils.decorators import token_required

blueprint = Blueprint('auth', __name__)
api = root_api.namespace('auth', description='Authentication endpoints')


class AuthBaseResource(Resource):
    auth_service = AuthService()


@api.route('/login')
class AuthUserLoginResource(AuthBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        404: 'Not found', 422: 'Unprocessable Entity'})
    @api.expect(auth_login_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self) -> tuple:
        token = self.auth_service.login_user(**request.get_json())
        return {'token': f'Bearer {token}'}, 200


@api.route('/logout')
class AuthUserLogoutResource(AuthBaseResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized'},
             security='auth_token')
    @token_required
    def post(self) -> tuple:
        self.auth_service.logout_user()
        return {}, 200


@api.route('/reset_password')
class RequestResetPasswordResource(AuthBaseResource):
    @api.doc(responses={202: 'Success', 403: 'Forbidden', 404: 'Not Found',
                        422: 'Unprocessable Entity'})
    @api.expect(auth_user_reset_password_sw_model)
    def post(self) -> tuple:
        self.auth_service.request_reset_password(**request.get_json())
        return {}, 202


@api.route('/reset_password/<token>')
@api.doc(params={'token': 'A password reset token created previously'})
class ResetPasswordResource(AuthBaseResource):
    @api.doc(responses={200: 'Success', 403: 'Forbidden'})
    def get(self, token: str) -> tuple:
        self.auth_service.verify_reset_token(token)
        return {}, 200

    @api.doc(responses={200: 'Success', 403: 'Forbidden',
                        422: 'Unprocessable Entity'})
    @api.expect(auth_user_reset_password_token_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self, token: str) -> tuple:
        password = request.get_json().get('password')
        new_token = self.auth_service.confirm_request_reset_password(token,
                                                                     password)
        return {'token': f'Bearer {new_token}'}, 200
