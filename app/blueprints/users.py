import logging
from datetime import datetime

from flask_login import current_user
from flask import Blueprint, request, url_for
from flask_restx import fields
from flask_security import roles_accepted
from marshmallow import ValidationError, INCLUDE, EXCLUDE
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from app.celery.word.tasks import export_user_data_in_word
from app.celery.excel.tasks import export_user_data_in_excel
from app.celery.tasks import create_user_email
from .base import BaseResource
from .roles import role_sw_model
from ..extensions import db_wrapper, api as root_api
from ..models.user import User as UserModel, user_datastore
from ..models.role import Role as RoleModel
from ..utils.cerberus_schema import user_model_schema, search_model_schema
from ..utils.decorators import token_required
from ..utils.marshmallow_schema import UserSchema as UserSerializer, ExportWordInputSchema as ExportWordInputSerializer

blueprint = Blueprint('users', __name__, )
api = root_api.namespace('users', description='Users endpoints')

logger = logging.getLogger(__name__)

creator_sw_model = api.model('Creator', {
    'id': fields.Integer,
})

user_sw_model = api.model('User', {
    'id': fields.Integer,
    'name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'genre': fields.String(enum=('m', 'f')),
    'birth_date': fields.String,
    'active': fields.Boolean,
    'created_at': fields.String,
    'updated_at': fields.String,
    'deleted_at': fields.String,
    'created_by': fields.Nested(creator_sw_model),
    'roles': fields.List(fields.Nested(role_sw_model))
})


class UserBaseResource(BaseResource):
    db_model = UserModel
    request_validation_schema = user_model_schema()
    user_serializer = UserSerializer()

    def deserialize_request_data(self, **kwargs: dict) -> dict:
        try:
            return self.user_serializer.load(**kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)


@api.route('')
class NewUserResource(UserBaseResource):
    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)
        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        with db_wrapper.database.atomic():
            role = RoleModel.get_by_id(data['role_id'])

            data['created_by'] = current_user.id
            data['roles'] = [role]
            user = user_datastore.create_user(**data)

        user_data = self.user_serializer.dump(user)
        create_user_email.delay(user_data)

        return {
                   'data': user_data,
               }, 201


@api.route('/<int:user_id>')
class UserResource(UserBaseResource):
    @token_required
    @roles_accepted('admin', 'team_leader')
    def get(self, user_id: int) -> tuple:
        user = UserModel.get_or_none(UserModel.id == user_id)
        if user is None:
            raise NotFound('User doesn\'t exist')

        user_data = self.user_serializer.dump(user)

        return {
                   'data': user_data,
               }, 200

    @token_required
    @roles_accepted('admin', 'team_leader')
    def put(self, user_id: int) -> tuple:
        user = (UserModel.get_or_none(UserModel.id == user_id,
                                      UserModel.deleted_at.is_null()))
        if user is None:
            raise BadRequest('User doesn\'t exist')

        request_data = request.get_json()
        self.request_validation_schema = user_model_schema(False)
        self.request_validation(request_data)

        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        with db_wrapper.database.atomic():
            data['id'] = user_id
            UserModel(**data).save()

            user_datastore.remove_role_from_user(user, user.roles[0])
            role = RoleModel.get_by_id(data['role_id'])
            user_datastore.add_role_to_user(user, role)

        user = (UserModel.get_or_none(UserModel.id == user_id,
                                      UserModel.deleted_at.is_null()))
        user_data = self.user_serializer.dump(user)

        return {
                   'data': user_data,
               }, 200

    @token_required
    @roles_accepted('admin', 'team_leader')
    def delete(self, user_id: int) -> tuple:
        user = UserModel.get_or_none(UserModel.id == user_id)
        if user is None:
            raise NotFound('User doesn\'t exist')

        if user.deleted_at is not None:
            raise BadRequest('User already deleted')

        user.deleted_at = datetime.utcnow()
        user.save()
        user_data = self.user_serializer.dump(user)

        return {
                   'data': user_data,
               }, 200


@api.route('/search')
class UsersSearchResource(UserBaseResource):
    user_fields = UserModel.get_fields(exclude=['id', 'password'])
    request_validation_schema = search_model_schema(user_fields)

    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)

        page_number, items_per_page, order_by = self.get_request_query_fields(request_data)

        query = UserModel.select()
        records_total = query.count()

        query = self.create_search_query(query, request_data)
        query = (query.order_by(*order_by)
                 .paginate(page_number, items_per_page))

        records_filtered = query.count()
        self.user_serializer = UserSerializer(many=True)
        user_data = self.user_serializer.dump(list(query))

        return {
                   'data': user_data,
                   'records_total': records_total,
                   'records_filtered': records_filtered,
               }, 200


@api.route('/xlsx')
class ExportUsersExcelResource(UserBaseResource):
    user_fields = UserModel.get_fields(exclude=['id', 'password'])
    request_validation_schema = search_model_schema(user_fields)

    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)

        task = export_user_data_in_excel.apply_async((current_user.id, request_data), countdown=5)

        return {
                   'task': task.id,
                   'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True),
               }, 202


@api.route('/word')
class ExportUsersWordResource(UserBaseResource):
    user_fields = UserModel.get_fields(exclude=['id', 'password'])
    request_validation_schema = search_model_schema(user_fields)

    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        request_data = request.get_json()
        self.request_validation(request_data)

        try:
            serializer = ExportWordInputSerializer()
            request_args = serializer.load(request.args.to_dict(), unknown=EXCLUDE)
            to_pdf = request_args.get('to_pdf', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        task = export_user_data_in_word.apply_async(args=[current_user.id, request_data, to_pdf])

        return {
                   'task': task.id,
                   'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True),
               }, 202
