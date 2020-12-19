import logging
from datetime import datetime

from flask import Blueprint, request
from flask_security import roles_required
from marshmallow import INCLUDE, ValidationError
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from .base import BaseResource
from app.extensions import api as root_api
from app.models.role import Role as RoleModel
from app.utils.marshmallow_schema import (RoleSchema as RoleSerializer,
                                          SearchSchema)
from ..swagger import (role_input_sw_model, role_output_sw_model,
                       search_input_sw_model, role_search_output_sw_model)
from ..utils.decorators import token_required

_API_DESCRIPTION = 'Users with role admin can manage these endpoints.'

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description=_API_DESCRIPTION)
logger = logging.getLogger(__name__)


class RoleBaseResource(BaseResource):
    db_model = RoleModel
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

        role = RoleModel.create(**data)
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
        role = RoleModel.get_or_none(RoleModel.id == role_id)
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
        role = RoleModel.get_or_none(RoleModel.id == role_id)
        if role is None:
            raise BadRequest('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        request_data = request.get_json()
        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        data['id'] = role_id
        RoleModel(**data).save()

        role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                      RoleModel.deleted_at.is_null()))
        role_data = self.role_serializer.dump(role)

        return {'data': role_data}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden'},
             security='auth_token')
    @api.marshal_with(role_output_sw_model)
    @token_required
    @roles_required('admin')
    def delete(self, role_id: int) -> tuple:
        role = RoleModel.get_or_none(RoleModel.id == role_id)
        if role is None:
            raise NotFound('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        role.deleted_at = datetime.utcnow()
        role.save()

        role_data = self.role_serializer.dump(role)

        return {'data': role_data}, 200


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
        request_data = request.get_json()
        try:
            data = SearchSchema().load(request_data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = RoleModel.select()
        records_total = query.count()

        query = self.create_search_query(query, request_data)
        query = (query.order_by(*order_by)
                 .paginate(page_number, items_per_page))

        records_filtered = query.count()
        self.role_serializer = RoleSerializer(many=True)
        role_data = self.role_serializer.dump(list(query))

        return {
                   'data': role_data,
                   'records_total': records_total,
                   'records_filtered': records_filtered,
               }, 200
