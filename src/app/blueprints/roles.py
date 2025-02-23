from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from flask_security import roles_required

from app.extensions import api as root_api
from app.serializers import RoleSerializer
from app.swagger import role_input_sw_model, role_search_output_sw_model, role_sw_model, search_input_sw_model

from ..containers import Container
from ..services.role import RoleService

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description='Users with role admin can manage these endpoints.')


class RoleBaseResource(Resource):
    role_service: RoleService
    role_serializer: RoleSerializer

    @inject
    def __init__(
        self,
        rest_api: str,
        role_service: RoleService = Provide[Container.role_service],
        role_serializer: RoleSerializer = Provide[Container.role_serializer],
        *args,
        **kwargs,
    ):
        super().__init__(rest_api, *args, **kwargs)
        self.role_service = role_service
        self.role_serializer = role_serializer


@api.route('')
class NewRoleResource(RoleBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.expect(role_input_sw_model)
    @api.marshal_with(role_sw_model, envelope='data', code=201)
    @jwt_required()
    @roles_required('admin')
    def post(self) -> tuple:
        role = self.role_service.create(**request.get_json())
        return self.role_serializer.dump(role), 201


@api.route('/<int:role_id>')
class RoleResource(RoleBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found'}, security='auth_token')
    @api.marshal_with(role_sw_model, envelope='data')
    @jwt_required()
    @roles_required('admin')
    def get(self, role_id: int) -> tuple:
        role = self.role_service.find(role_id)
        return self.role_serializer.dump(role), 200

    @api.doc(
        responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(role_input_sw_model)
    @api.marshal_with(role_sw_model, envelope='data')
    @jwt_required()
    @roles_required('admin')
    def put(self, role_id: int) -> tuple:
        role = self.role_service.save(role_id, **request.get_json())
        return self.role_serializer.dump(role), 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden'}, security='auth_token')
    @api.marshal_with(role_sw_model, envelope='data')
    @jwt_required()
    @roles_required('admin')
    def delete(self, role_id: int) -> tuple:
        role = self.role_service.delete(role_id)
        return self.role_serializer.dump(role), 200


@api.route('/search')
class RolesSearchResource(RoleBaseResource):
    @api.doc(
        responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(search_input_sw_model)
    @api.marshal_with(role_search_output_sw_model)
    @jwt_required()
    @roles_required('admin')
    def post(self) -> tuple:
        role_data = self.role_service.get(**request.get_json())
        role_serializer = RoleSerializer(many=True)
        return {
            'data': role_serializer.dump(list(role_data['query'])),
            'records_total': role_data['records_total'],
            'records_filtered': role_data['records_filtered'],
        }, 200
