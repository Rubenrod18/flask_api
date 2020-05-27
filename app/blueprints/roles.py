import logging
from datetime import datetime

from cerberus import Validator
from flask import Blueprint, request
from flask_restful import Api
from flask_security import roles_required
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from .base import BaseResource
from app.models.role import Role as RoleModel
from app.utils.cerberus_schema import role_model_schema, search_model_schema, MyValidator
from ..utils.decorators import token_required

blueprint = Blueprint('roles', __name__, url_prefix='/roles')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class RoleBaseResource(BaseResource):
    db_model = RoleModel


@api.resource('')
class NewRoleResource(RoleBaseResource):
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=role_model_schema())
        v.allow_unknown = False

        if not v.validate(data):
            raise UnprocessableEntity(v.errors)

        role = RoleModel.create(**data)
        role_dict = role.serialize()

        return {
                   'data': role_dict
               }, 201


@api.resource('/<int:role_id>')
class RoleResource(RoleBaseResource):
    @token_required
    @roles_required('admin')
    def get(self, role_id: int) -> tuple:
        role = RoleModel.get_or_none(RoleModel.id == role_id)

        if isinstance(role, RoleModel):
            role_dict = role.serialize()
        else:
            raise NotFound('Role doesn\'t exist')

        return {
                   'data': role_dict,
               }, 200

    @token_required
    @roles_required('admin')
    def put(self, role_id: int) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=role_model_schema(False))
        v.allow_unknown = False

        if not v.validate(data):
            raise UnprocessableEntity(v.errors)

        role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                      RoleModel.deleted_at.is_null()))

        if role:
            data['id'] = role_id
            RoleModel(**data).save()

            role = (RoleModel.get_or_none(RoleModel.id == role_id,
                                          RoleModel.deleted_at.is_null()))
            role_dict = role.serialize()
        else:
            raise BadRequest('Role doesn\'t exist')

        return {
                   'data': role_dict,
               }, 200

    @token_required
    @roles_required('admin')
    def delete(self, role_id: int) -> tuple:
        role = RoleModel.get_or_none(RoleModel.id == role_id)

        if isinstance(role, RoleModel):
            if role.deleted_at is None:
                role.deleted_at = datetime.utcnow()
                role.save()

                role_dict = role.serialize()
            else:
                raise BadRequest('Role already deleted')
        else:
            raise NotFound('Role doesn\'t exist')

        return {
                   'data': role_dict,
               }, 200


@api.resource('/search')
class RolesSearchResource(RoleBaseResource):
    @token_required
    @roles_required('admin')
    def post(self) -> tuple:
        data = request.get_json()

        role_fields = RoleModel.get_fields(['id'])
        v = Validator(schema=search_model_schema(role_fields))
        v.allow_unknown = False

        if not v.validate(data):
            return UnprocessableEntity(v.errors), 422

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = RoleModel.select()
        records_total = query.count()

        query = self.create_search_query(query, data)

        query = (query.order_by(*order_by)
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
