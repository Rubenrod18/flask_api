from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app import serializers, swagger as swagger_models
from app.blueprints.base import BaseResource
from app.di_container import ServiceDIContainer
from app.extensions import api as root_api
from app.helpers.otp_token import OTPTokenManager
from app.services.auth import AuthService

blueprint = Blueprint('auth', __name__)
api = root_api.namespace('auth', description='Authentication endpoints')


class BaseAuthResource(BaseResource):
    @inject
    def __init__(
        self,
        rest_api: str,
        *args,
        service: AuthService = Provide[ServiceDIContainer.auth_service],
        otp_token_manager: OTPTokenManager = Provide[ServiceDIContainer.otp_token_manager],
        **kwargs,
    ):
        super().__init__(rest_api, service, *args, **kwargs)
        self.otp_token_manager = otp_token_manager


@api.route('/login')
class AuthUserLoginResource(BaseAuthResource):
    serializer_class = serializers.AuthUserLoginSerializer

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'})
    @api.expect(swagger_models.auth_login_sw_model)
    @api.marshal_with(swagger_models.auth_token_sw_model)
    def post(self) -> tuple:
        serializer = self.get_serializer()
        user = serializer.load(request.get_json())

        return self.service.login_user(user), 200


@api.route('/refresh')
class AuthRefreshResource(BaseAuthResource):
    @jwt_required(refresh=True)
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'})
    @api.marshal_with(swagger_models.auth_token_sw_model)
    def post(self) -> tuple:
        return self.service.refresh_token(), 200


@api.route('/logout')
class AuthUserLogoutResource(BaseAuthResource):
    @jwt_required()
    @api.doc(responses={200: 'Success', 401: 'Unauthorized'}, security='auth_token')
    def post(self) -> tuple:
        return self.service.logout_user(), 200


@api.route('/reset_password')
class RequestResetPasswordResource(BaseAuthResource):
    serializer_class = serializers.AuthUserLoginSerializer

    @api.doc(responses={202: 'Success', 403: 'Forbidden', 404: 'Not Found', 422: 'Unprocessable Entity'})
    @api.expect(swagger_models.auth_user_reset_password_sw_model)
    def post(self) -> tuple:
        serializer = self.get_serializer()
        user = serializer.load(request.get_json(), partial=True)

        self.service.request_reset_password(self.otp_token_manager, user)

        return {}, 202


@api.route('/reset_password/<token>')
@api.doc(params={'token': 'A password reset token created previously'})
class ResetPasswordResource(BaseAuthResource):
    serializer_class = serializers.AuthUserConfirmResetPasswordSerializer

    @api.doc(responses={200: 'Success', 403: 'Forbidden'})
    def get(self, token: str) -> tuple:
        serializer = self.get_serializer(otp_token_manager=self.otp_token_manager)
        serializer.load({'token': token}, partial=True)

        return {}, 200

    @api.doc(responses={200: 'Success', 403: 'Forbidden', 422: 'Unprocessable Entity'})
    @api.expect(swagger_models.auth_user_reset_password_token_sw_model)
    @api.marshal_with(swagger_models.auth_token_sw_model)
    def post(self, token: str) -> tuple:
        request_data = request.get_json()
        request_data['token'] = token

        serializer = self.get_serializer(otp_token_manager=self.otp_token_manager)
        user = serializer.load(request_data)

        return self.service.confirm_request_reset_password(user, request_data['password']), 200
