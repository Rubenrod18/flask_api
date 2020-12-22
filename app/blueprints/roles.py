import logging

from flask import Blueprint, request
from flask_security import roles_required

from .base import BaseResource
from app.extensions import api as root_api
from app.models.role import Role as RoleModel
from app.serializers import RoleSerializer
from app.swagger import (role_input_sw_model, role_output_sw_model,
                         search_input_sw_model, role_search_output_sw_model)
from app.utils.decorators import token_required
from ..managers.role import RoleManager
from ..services.role import RoleService

_API_DESCRIPTION = 'Users with role admin can manage these endpoints.'

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description=_API_DESCRIPTION)
logger = logging.getLogger(__name__)


class RoleBaseResource(BaseResource):
    db_model = RoleModel
    role_service = RoleService()
    role_manager = RoleManager()
    role_serializer = RoleSerializer()


@api.route('')
class NewRoleResource(RoleBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(role_input_sw_model)
    @api.marshal_with(role_output_sw_model, code=201)
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        role = self.role_service.create(**request.get_json())
        return {'data': self.role_serializer.dump(role)}, 201


@api.route('/<int:role_id>')
class RoleResource(RoleBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found'},
             security='auth_token')
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def get(self, role_id: int) -> tuple:
        role = self.role_service.find(role_id)
        return {'data': self.role_serializer.dump(role)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(role_input_sw_model)
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def put(self, role_id: int) -> tuple:
        role = self.role_service.save(role_id, **request.get_json())
        return {'data': self.role_serializer.dump(role)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden'},
             security='auth_token')
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def delete(self, role_id: int) -> tuple:
        role = self.role_service.delete(role_id)
        return {'data': self.role_serializer.dump(role)}, 200


@api.route('/search')
class RolesSearchResource(RoleBaseResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @api.marshal_with(role_search_output_sw_model)
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        role_data = self.role_manager.get(**request.get_json())
        role_serializer = RoleSerializer(many=True)
        return {
                   'data': role_serializer.dump(list(role_data['query'])),
                   'records_total': role_data['records_total'],
                   'records_filtered': role_data['records_filtered'],
               }, 200
