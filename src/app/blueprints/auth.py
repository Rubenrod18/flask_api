import logging

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from app.containers import Container
from app.extensions import api as root_api
from app.helpers.otp_token import OTPTokenManager
from app.services.auth import AuthService
from app.swagger import (
    auth_login_sw_model,
    auth_token_sw_model,
    auth_user_reset_password_sw_model,
    auth_user_reset_password_token_sw_model,
)

blueprint = Blueprint('auth', __name__)
api = root_api.namespace('auth', description='Authentication endpoints')
logger = logging.getLogger(__name__)


class BaseAuthResource(Resource):
    @inject
    def __init__(
        self,
        rest_api: str,
        auth_service: AuthService = Container.auth_service,
        otp_token_manager: OTPTokenManager = Provide[Container.otp_token_manager],
        *args,
        **kwargs,
    ):
        super().__init__(rest_api, *args, **kwargs)
        self.auth_service = auth_service(otp_token_manager)
        self.otp_token_manager = otp_token_manager


@api.route('/login')
class AuthUserLoginResource(BaseAuthResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'})
    @api.expect(auth_login_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self) -> tuple:
        return self.auth_service.login_user(**request.get_json()), 200


@api.route('/refresh')
class AuthRefreshResource(BaseAuthResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'})
    @api.marshal_with(auth_token_sw_model)
    @jwt_required(refresh=True)
    def post(self) -> tuple:
        return self.auth_service.refresh_token(), 200


@api.route('/logout')
class AuthUserLogoutResource(BaseAuthResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized'}, security='auth_token')
    @jwt_required()
    def post(self) -> tuple:
        return self.auth_service.logout_user(), 200


@api.route('/reset_password')
class RequestResetPasswordResource(BaseAuthResource):
    @api.doc(responses={202: 'Success', 403: 'Forbidden', 404: 'Not Found', 422: 'Unprocessable Entity'})
    @api.expect(auth_user_reset_password_sw_model)
    def post(self) -> tuple:
        self.auth_service.request_reset_password(self.otp_token_manager, **request.get_json())
        return {}, 202


@api.route('/reset_password/<token>')
@api.doc(params={'token': 'A password reset token created previously'})
class ResetPasswordResource(BaseAuthResource):
    @api.doc(responses={200: 'Success', 403: 'Forbidden'})
    def get(self, token: str) -> tuple:
        self.auth_service.check_token_status(token)
        return {}, 200

    @api.doc(responses={200: 'Success', 403: 'Forbidden', 422: 'Unprocessable Entity'})
    @api.expect(auth_user_reset_password_token_sw_model)
    @api.marshal_with(auth_token_sw_model)
    def post(self, token: str) -> tuple:
        return self.auth_service.confirm_request_reset_password(token, request.get_json().get('password')), 200
