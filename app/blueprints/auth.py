import logging

from flask_restful import Api, Resource
from flask import Blueprint, request
from flask_security import verify_password
from flask_security.passwordless import generate_login_token

from app.models.user import User as UserModel
from app.utils.cerberus_schema import MyValidator, user_login_schema

blueprint = Blueprint('auth', __name__, url_prefix='/auth')
api = Api(blueprint)

logger = logging.getLogger(__name__)

# TODO: recovery password, update new password

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

        user = UserModel.get(UserModel.email == data.get('email'))

        if not verify_password(data.get('password'), user.password):
            return {
                       'message': 'credentials are invalid',
                   }, 401

        token = generate_login_token(user)

        return {
                   'token': token,
               }, 200
