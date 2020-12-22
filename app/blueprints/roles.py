import logging

from flask import Blueprint, request
from flask_security import roles_required
from marshmallow import INCLUDE, ValidationError
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from .base import BaseResource
from app.extensions import api as root_api
from app.models.role import Role as RoleModel
from app.serializers import RoleSerializer, SearchSerializer
from app.swagger import (role_input_sw_model, role_output_sw_model,
                         search_input_sw_model, role_search_output_sw_model)
from app.utils.decorators import token_required
from ..managers.role import RoleManager

_API_DESCRIPTION = 'Users with role admin can manage these endpoints.'

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description=_API_DESCRIPTION)
logger = logging.getLogger(__name__)


class RoleBaseResource(BaseResource):
    db_model = RoleModel
    role_manager = RoleManager()
    role_serializer = RoleSerializer()

    def deserialize_request_data(self, **kwargs: dict) -> dict:
        try:
            return self.role_serializer.load(**kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)


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
        request_data = self.role_serializer.valid_request_role(
            request.get_json()
        )

        try:
            data = self.role_serializer.load(data=request_data, unknown=INCLUDE)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        role = self.role_manager.create(**data)
        role_data = self.role_serializer.dump(role)

        return {'data': role_data}, 201


@api.route('/<int:role_id>')
class RoleResource(RoleBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found'},
             security='auth_token')
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def get(self, role_id: int) -> tuple:
        role = self.role_manager.find(role_id)
        if role is None:
            raise NotFound('Role doesn\'t exist')

        role_data = self.role_serializer.dump(role)
        return {'data': role_data}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(role_input_sw_model)
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def put(self, role_id: int) -> tuple:
        role = self.role_manager.find(role_id)
        if role is None:
            raise BadRequest('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        data = self.deserialize_request_data(data=request.get_json(),
                                             unknown=INCLUDE)
        data['id'] = role_id
        self.role_manager.save(**data)

        args = (RoleModel.deleted_at.is_null(),)
        role = self.role_manager.find(role_id, *args)
        return {'data': self.role_serializer.dump(role)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden'},
             security='auth_token')
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def delete(self, role_id: int) -> tuple:
        role = self.role_manager.find(role_id)
        if role is None:
            raise NotFound('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        role = self.role_manager.delete(role_id)
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
        try:
            request_data = SearchSerializer().load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        role_data = self.role_manager.get(**request_data)
        role_serializer = RoleSerializer(many=True)

        return {
                   'data': role_serializer.dump(list(role_data['query'])),
                   'records_total': role_data['records_total'],
                   'records_filtered': role_data['records_filtered'],
               }, 200
