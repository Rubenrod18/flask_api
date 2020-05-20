import logging
from datetime import datetime

from cerberus import Validator
from flask import Blueprint, request
from flask_restful import Api

from .base import BaseResource
from app.models.role import Role as RoleModel
from app.utils.cerberus_schema import role_model_schema, search_model_schema, MyValidator
from ..utils.decorators import authenticated

blueprint = Blueprint('roles', __name__, url_prefix='/roles')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class RoleBaseResource(BaseResource):
    db_model = RoleModel


@api.resource('')
class NewRoleResource(RoleBaseResource):
    @authenticated
    def post(self) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=role_model_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        role = RoleModel.create(**data)
        role_dict = role.serialize()

        return {
                   'data': role_dict
               }, 201


@api.resource('/<int:role_id>')
class RoleResource(RoleBaseResource):
    @authenticated
    def get(self, role_id: int) -> tuple:
        response = {
            'error': 'Role doesn\'t exist',
        }
        status_code = 404

        role = RoleModel.get_or_none(RoleModel.id == role_id)

        if isinstance(role, RoleModel):
            role_dict = role.serialize()

            response = {
                'data': role_dict,
            }
            status_code = 200

        return response, status_code

    @authenticated
    def put(self, role_id: int) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=role_model_schema(False))
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

    @authenticated
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


@api.resource('/search')
class RolesSearchResource(RoleBaseResource):
    @authenticated
    def post(self) -> tuple:
        data = request.get_json()

        role_fields = RoleModel.get_fields(['id'])
        v = Validator(schema=search_model_schema(role_fields))
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = RoleModel.select()
        records_total = query.count()

        query = self.create_query(query, data)

        query = (query.order_by(order_by)
                 .paginate(page_number, items_per_page))

        records_filtered = query.count()
        user_list = []

        for user in query:
            user_dict = user.serialize()
            user_list.append(user_dict)

        return {
                   'data': user_list,
                   'records_total': records_total,
                   'records_filtered': records_filtered,
               }, 200
