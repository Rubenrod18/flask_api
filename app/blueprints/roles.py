import logging
from datetime import datetime

from cerberus import Validator
from flask import Blueprint, request
from flask_restful import Api, Resource

from app.models.role import Role as RoleModel
from app.utils.cerberus_schema import role_model_schema

blueprint = Blueprint('roles', __name__, url_prefix='/roles')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class RoleBaseResource(Resource):
    pass


@api.resource('')
class NewRoleResource(RoleBaseResource):
    def post(self) -> tuple:
        data = request.get_json()

        v = Validator(schema=role_model_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        data['slug'] = data['name'].lower().replace(' ', '-')

        role = RoleModel.create(**data)
        role_dict = role.serialize()

        return {
                   'data': role_dict
               }, 201


@api.resource('/<int:role_id>')
class RoleResource(RoleBaseResource):
    def get(self, role_id: int) -> tuple:
        response = {
            'error': 'Role doesn\'t exist',
        }
        status_code = 404

        role = RoleModel.get_or_none(RoleModel.id == role_id)

        if isinstance(role, RoleModel):
            if role.deleted_at is None:
                role_dict = role.serialize()

                response = {
                    'data': role_dict,
                }
                status_code = 200
            else:
                response = {
                    'error': 'Role has been deleted',
                }
                status_code = 400

        return response, status_code

    def put(self, role_id: int) -> tuple:
        data = request.get_json()

        v = Validator(schema=role_model_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                      RoleModel.deleted_at.is_null()))

        if role:
            data['id'] = role_id
            data['slug'] = data['name'].lower().replace(' ', '-')
            RoleModel(**data).save()

            role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                          RoleModel.deleted_at.is_null()))
            role_dict = role.serialize()

            response_data = {
                'data': role_dict,
            }
            response_code = 200
        else:
            response_data = {
                'error': 'Role doesn\'t exist',
            }
            response_code = 400

        return response_data, response_code

    def delete(self, role_id: int) -> tuple:
        response = {
            'error': 'Role doesn\'t exist',
        }
        status_code = 404

        role = RoleModel.get_or_none(RoleModel.id == role_id)

        if isinstance(role, RoleModel):
            if role.deleted_at is None:
                role.deleted_at = datetime.utcnow()
                role.save()

                role_dict = role.serialize()

                response = {
                    'data': role_dict,
                }
                status_code = 200
            else:
                response = {
                    'error': 'Role already deleted',
                }
                status_code = 400

        return response, status_code
