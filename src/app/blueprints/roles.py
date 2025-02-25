from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_security import roles_required

from app import serializers, swagger as swagger_models
from app.extensions import api as root_api

from ..containers import Container
from ..models.role import ADMIN_ROLE
from ..services.role import RoleService
from .base import BaseResource

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description='Users with role admin can manage these endpoints.')


class BaseRoleResource(BaseResource):
    serializer_class = serializers.RoleSerializer

    @inject
    def __init__(
        self,
        rest_api: str,
        service: RoleService = Provide[Container.role_service],
        *args,
        **kwargs,
    ):
        super().__init__(rest_api, service, *args, **kwargs)


@api.route('')
class NewRoleResource(BaseRoleResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.expect(swagger_models.role_input_sw_model)
    @api.marshal_with(swagger_models.role_sw_model, envelope='data', code=201)
    @jwt_required()
    @roles_required(ADMIN_ROLE)
    def post(self) -> tuple:
        serializer = self.serializer_class()
        validated_data = serializer.load(request.get_json())

        role = self.service.create(**validated_data)

        return serializer.dump(role), 201


@api.route('/<int:role_id>')
class RoleResource(BaseRoleResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found'}, security='auth_token')
    @api.marshal_with(swagger_models.role_sw_model, envelope='data')
    @jwt_required()
    @roles_required(ADMIN_ROLE)
    def get(self, role_id: int) -> tuple:
        serializer = self.serializer_class()
        serializer.load({'id': role_id}, partial=True)

        role = self.service.find(role_id)

        return serializer.dump(role), 200

    @api.doc(
        responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.role_input_sw_model)
    @api.marshal_with(swagger_models.role_sw_model, envelope='data')
    @jwt_required()
    @roles_required(ADMIN_ROLE)
    def put(self, role_id: int) -> tuple:
        json_data = request.get_json()
        json_data['id'] = role_id
        serializer = self.serializer_class()
        serialized_data = serializer.load(json_data)

        role = self.service.save(role_id, **serialized_data)

        return serializer.dump(role), 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden'}, security='auth_token')
    @api.marshal_with(swagger_models.role_sw_model, envelope='data')
    @jwt_required()
    @roles_required(ADMIN_ROLE)
    def delete(self, role_id: int) -> tuple:
        serializer = self.serializer_class()
        serializer.load({'id': role_id}, partial=True)

        role = self.service.delete(role_id)

        return serializer.dump(role), 200


@api.route('/search')
class RolesSearchResource(BaseRoleResource):
    @api.doc(
        responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.search_input_sw_model)
    @api.marshal_with(swagger_models.role_search_output_sw_model)
    @jwt_required()
    @roles_required(ADMIN_ROLE)
    def post(self) -> tuple:
        serializer = self.get_serializer(many=True)
        validated_data = serializers.SearchSerializer().load(request.get_json())

        doc_data = self.service.get(**validated_data)

        return {
            'data': serializer.dump(list(doc_data['query'])),
            'records_total': doc_data['records_total'],
            'records_filtered': doc_data['records_filtered'],
        }, 200
