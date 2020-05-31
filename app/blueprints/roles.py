import logging
from datetime import datetime

from flask import Blueprint, request
from flask_restx import fields
from flask_security import roles_required
from marshmallow import INCLUDE, ValidationError
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from config import Config
from .base import BaseResource
from app.extensions import api as root_api
from app.models.role import Role as RoleModel
from app.utils.cerberus_schema import role_model_schema, search_model_schema
from app.utils.marshmallow_schema import RoleSchema as RoleSerializer
from ..utils.decorators import token_required

blueprint = Blueprint('roles', __name__)
api = root_api.namespace('roles', description='Roles endpoints. Users with role admin can manage these endpoints.')
logger = logging.getLogger(__name__)

role_sw_model = api.model('Role', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'label': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
    'deleted_at': fields.String,
})


class RoleBaseResource(BaseResource):
    db_model = RoleModel
    request_validation_schema = role_model_schema()
    role_serializer = RoleSerializer()

    def deserialize_request_data(self, **kwargs: dict) -> dict:
        try:
            return self.role_serializer.load(**kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)


@api.route('')
class NewRoleResource(RoleBaseResource):
    _parser = api.parser()
    _parser.add_argument(Config.SECURITY_TOKEN_AUTHENTICATION_HEADER, location='headers', required=True,
                         default='Bearer token')
    _parser.add_argument('name', type=str, location='json', required=True)
    _parser.add_argument('label', type=str, location='json', required=True)
    _parser.add_argument('description', type=str, location='json', required=True)

    @api.doc(responses={
        201: ('Success', role_sw_model),
        401: 'Unauthorized',
        403: 'Forbidden',
        422: 'Unprocessable Entity',
    })
    @api.expect(_parser)
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)
        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        role = RoleModel.create(**data)
        role_data = self.role_serializer.dump(role)

        return {
                   'data': role_data
               }, 201


@api.route('/<int:role_id>')
class RoleResource(RoleBaseResource):
    _parser = api.parser()
    _parser.add_argument(Config.SECURITY_TOKEN_AUTHENTICATION_HEADER, location='headers', required=True,
                         default='Bearer token')

    @api.doc(responses={
        200: ('Success', role_sw_model),
        401: 'Unauthorized',
        403: 'Forbidden',
        422: 'Unprocessable Entity',
    })
    @api.expect(_parser)
    @token_required
    @roles_required('admin')
    def get(self, role_id: int) -> tuple:
        role = RoleModel.get_or_none(RoleModel.id == role_id)
        if role is None:
            raise NotFound('Role doesn\'t exist')

        role_data = self.role_serializer.dump(role)

        return {
                   'data': role_data,
               }, 200

    _parser = api.parser()
    _parser.add_argument(Config.SECURITY_TOKEN_AUTHENTICATION_HEADER, location='headers', required=True,
                         default='Bearer token')
    _parser.add_argument('name', type=str, location='json')
    _parser.add_argument('label', type=str, location='json')
    _parser.add_argument('description', type=str, location='json')

    @api.doc(responses={
        200: ('Success', role_sw_model),
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        422: 'Unprocessable Entity',
    })
    @api.expect(_parser)
    @token_required
    @roles_required('admin')
    def put(self, role_id: int) -> tuple:
        role = RoleModel.get_or_none(RoleModel.id == role_id)
        if role is None:
            raise BadRequest('Role doesn\'t exist')

        if role.deleted_at is not None:
            raise BadRequest('Role already deleted')

        request_data = request.get_json()
        self.request_validation_schema = role_model_schema(False)
        self.request_validation(request_data)

        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        data['id'] = role_id
        RoleModel(**data).save()

        role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                      RoleModel.deleted_at.is_null()))
        role_data = self.role_serializer.dump(role)

        return {
                   'data': role_data,
               }, 200

    _parser = api.parser()
    _parser.add_argument(Config.SECURITY_TOKEN_AUTHENTICATION_HEADER, location='headers', required=True,
                         default='Bearer token')

    @api.doc(responses={
        200: ('Success', role_sw_model),
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        422: 'Unprocessable Entity',
    })
    @api.expect(_parser)
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

        return {
                   'data': role_data,
               }, 200


@api.route('/search')
class RolesSearchResource(RoleBaseResource):
    role_fields = RoleModel.get_fields(['id'])
    request_validation_schema = search_model_schema(role_fields)

    _parser = api.parser()
    _parser.add_argument(Config.SECURITY_TOKEN_AUTHENTICATION_HEADER, location='headers', required=True,
                         default='Bearer token')
    _parser.add_argument('search', type=list, location='json')
    _parser.add_argument('order', type=list, location='json')
    _parser.add_argument('items_per_page', type=int, location='json')
    _parser.add_argument('page_number', type=int, location='json')

    @api.doc(responses={
        200: 'Success',
        401: 'Unauthorized',
        403: 'Forbidden',
        422: 'Unprocessable Entity',
    })
    @api.expect(_parser)
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)

        page_number, items_per_page, order_by = self.get_request_query_fields(request_data)

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
