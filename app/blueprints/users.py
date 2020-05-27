import logging
from datetime import datetime

from cerberus import Validator
from flask_login import current_user
from flask_restful import Api, reqparse
from flask import Blueprint, request, url_for
from flask_security import roles_accepted

from app.celery.word.tasks import export_user_data_in_word
from app.celery.excel.tasks import export_user_data_in_excel
from app.celery.tasks import create_user_email
from .base import BaseResource
from ..extensions import db_wrapper
from ..models.user import User as UserModel, user_datastore
from ..models.role import Role as RoleModel
from ..utils import get_request_query_fields, create_search_query
from ..utils.cerberus_schema import user_model_schema, search_model_schema, MyValidator
from ..utils.decorators import token_required

blueprint = Blueprint('users', __name__, url_prefix='/users')
api = Api(blueprint)

logger = logging.getLogger(__name__)

class UserResource(BaseResource):
    db_model = UserModel


@api.resource('')
class NewUserResource(UserResource):
    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=user_model_schema())
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        with db_wrapper.database.atomic():
            data['created_by'] = current_user.id
            user = user_datastore.create_user(**data)

            role = RoleModel.get_by_id(data['role_id'])
            user_datastore.add_role_to_user(user, role)

        user_dict = user.serialize()

        create_user_email.delay(data)

        return {
                   'data': user_dict,
               }, 201


@api.resource('/<int:user_id>')
class UserResource(UserResource):
    @token_required
    @roles_accepted('admin', 'team_leader')
    def get(self, user_id: int) -> tuple:
        response = {
            'error': 'User doesn\'t exist',
        }
        status_code = 404

        user = UserModel.get_or_none(UserModel.id == user_id)

        if isinstance(user, UserModel):
            user_dict = user.serialize()

            response = {
                'data': user_dict,
            }
            status_code = 200

        return response, status_code

    @token_required
    @roles_accepted('admin', 'team_leader')
    def put(self, user_id: int) -> tuple:
        data = request.get_json()

        v = MyValidator(schema=user_model_schema(False))
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors
                   }, 422

        user = (UserModel.get_or_none(UserModel.id == user_id,
                                      UserModel.deleted_at.is_null()))
        if user:
            with db_wrapper.database.atomic():
                data['id'] = user_id
                UserModel(**data).save()

                user_datastore.remove_role_from_user(user, user.roles[0])

                role = RoleModel.get_by_id(data['role_id'])
                user_datastore.add_role_to_user(user, role)

            user = (UserModel.get_or_none(UserModel.id == user_id,
                                          UserModel.deleted_at.is_null()))
            user_dict = user.serialize()

            response_data = {
                'data': user_dict,
            }
            response_code = 200
        else:
            response_data = {
                'error': 'User doesn\'t exist',
            }
            response_code = 400

        return response_data, response_code

    @token_required
    @roles_accepted('admin', 'team_leader')
    def delete(self, user_id: int) -> tuple:
        response = {
            'error': 'User doesn\'t exist',
        }
        status_code = 404

        user = UserModel.get_or_none(UserModel.id == user_id)

        if isinstance(user, UserModel):
            if user.deleted_at is None:
                user.deleted_at = datetime.utcnow()
                user.save()

                user_dict = user.serialize()

                response = {
                    'data': user_dict,
                }
                status_code = 200
            else:
                response = {
                    'error': 'User already deleted',
                }
                status_code = 400

        return response, status_code


@api.resource('/search')
class UsersSearchResource(UserResource):
    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        data = request.get_json()

        user_fields = UserModel.get_fields(exclude=['id', 'password'])
        v = Validator(schema=search_model_schema(user_fields))
        v.allow_unknown = False

        if not v.validate(data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = UserModel.select()
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


@api.resource('/xlsx')
class ExportUsersExcelResource(UserResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        request_data = request.get_json()

        user_fields = UserModel.get_fields(exclude=['id', 'password'])
        v = Validator(schema=search_model_schema(user_fields))

        if not v.validate(request_data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        task = export_user_data_in_excel.apply_async((current_user.id, request_data), countdown=5)

        return {
                   'task': task.id,
                   'url': url_for('tasks.taskstatusresource', task_id=task.id, _external=True),
               }, 202


@api.resource('/word')
class ExportUsersPdfResource(UserResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        # TODO: RequestParse will be deprecated in the future. Replace RequestParse to marshmallow
        # https://flask-restful.readthedocs.io/en/latest/reqparse.html
        parser = reqparse.RequestParser()
        parser.add_argument('to_pdf', type=int, location='args')

        request_data = request.get_json()

        user_fields = UserModel.get_fields(exclude=['id', 'password'])
        v = Validator(schema=search_model_schema(user_fields))

        if not v.validate(request_data):
            return {
                       'message': 'validation error',
                       'fields': v.errors,
                   }, 422

        args = parser.parse_args()
        to_pdf = args.get('to_pdf') or 0

        task = export_user_data_in_word.apply_async(args=[current_user.id, request_data, to_pdf])

        return {
            'task': task.id,
            'url': url_for('tasks.taskstatusresource', task_id=task.id, _external=True),
        }, 202
