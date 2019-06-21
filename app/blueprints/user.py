# Standard library imports
import json

# Related third party imports
from flask_restful import Api, Resource
from flask import Blueprint, request
from playhouse.shortcuts import model_to_dict

# Local application/library specific imports
from ..models.user import User as UserModel
from ..utils import custom_converter

blueprint = Blueprint('user', __name__, url_prefix='/user')
api = Api(blueprint)


@api.resource('')
class NewUserResource(Resource):
    def post(self):
        data = dict(request.get_json())

        user = UserModel(**data).save()

        return {
            'data': user
        }

@api.resource('/<int:user_id>')
class UserResource(Resource):
    def put(self, user_id):
        data = dict(request.get_json())

        data['id'] = user_id
        UserModel(**data).save()

        user = UserModel.get(user_id)
        user_dict = model_to_dict(user)

        # TODO: improve this line
        user = {k: custom_converter(v) for (k, v) in user_dict.items()}

        return {
            'data': user
        }

    def delete(self, user_id):
        user = UserModel.get(user_id)
        user_dict = model_to_dict(user)

        # TODO: improve this line
        user = {k: custom_converter(v) for (k, v) in user_dict.items()}

        q = UserModel.delete().where(UserModel.id == user_id).execute()

        return {
            'data': user
        }
