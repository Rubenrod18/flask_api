import logging

from flask_login import current_user
from flask import Blueprint, request, url_for
from flask_security import roles_accepted
from marshmallow import ValidationError, INCLUDE, EXCLUDE
from werkzeug.exceptions import UnprocessableEntity, NotFound, BadRequest

from app.celery.word.tasks import export_user_data_in_word
from app.celery.excel.tasks import export_user_data_in_excel
from app.celery.tasks import create_user_email, create_word_and_excel_documents
from app.blueprints.base import BaseResource
from app.extensions import db_wrapper, api as root_api
from app.managers import RoleManager, UserManager
from app.models import User as UserModel, user_datastore
from app.serializers import (UserSerializer, UserExportWordSerializer,
                             SearchSerializer)
from app.swagger import (user_input_sw_model, user_output_sw_model,
                         user_search_output_sw_model, search_input_sw_model)
from app.utils.decorators import token_required

_API_DESCRIPTION = ('Users with role admin or team_leader can manage '
                    'these endpoints.')

blueprint = Blueprint('users', __name__)
api = root_api.namespace('users', description=_API_DESCRIPTION)
logger = logging.getLogger(__name__)


class UserBaseResource(BaseResource):
    db_model = UserModel
    user_manager = UserManager()
    role_manager = RoleManager()
    user_serializer = UserSerializer()

    def deserialize_request_data(self, **kwargs: dict) -> dict:
        try:
            return self.user_serializer.load(**kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)


@api.route('')
class NewUserResource(UserBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(user_input_sw_model)
    @api.marshal_with(user_output_sw_model, code=201)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        request_data = self.user_serializer.valid_request_user(request.get_json())
        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        with db_wrapper.database.atomic():
            role = self.role_manager.find(data['role_id'])

            data['created_by'] = current_user.id
            data['roles'] = [role]
            user = user_datastore.create_user(**data)

        user_data = self.user_serializer.dump(user)
        create_user_email.delay(user_data)
        logger.debug(user_data)

        return {'data': user_data}, 201


@api.route('/<int:user_id>')
class UserResource(UserBaseResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.marshal_with(user_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def get(self, user_id: int) -> tuple:
        user = self.user_manager.find(user_id)
        if user is None:
            raise NotFound('User doesn\'t exist')

        return {'data': self.user_serializer.dump(user)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(user_input_sw_model)
    @api.marshal_with(user_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def put(self, user_id: int) -> tuple:
        user = self.user_manager.find(user_id)
        if user is None:
            raise BadRequest('User doesn\'t exist')

        if user.deleted_at is not None:
            raise BadRequest('User already deleted')

        request_data = self.user_serializer.valid_request_user(request.get_json())
        data = self.deserialize_request_data(data=request_data, unknown=INCLUDE)

        with db_wrapper.database.atomic():
            self.user_manager.save(user_id, **data)

            if 'role_id' in data:
                user_datastore.remove_role_from_user(user, user.roles[0])
                role = self.role_manager.find(data['role_id'])
                user_datastore.add_role_to_user(user, role)

        args = (UserModel.deleted_at.is_null(),)
        user = self.user_manager.find(user_id, *args)
        return {'data': self.user_serializer.dump(user)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.marshal_with(user_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def delete(self, user_id: int) -> tuple:
        user = self.user_manager.find(user_id)
        if user is None:
            raise NotFound('User doesn\'t exist')

        if user.deleted_at is not None:
            raise BadRequest('User already deleted')

        user = self.user_manager.delete(user_id)
        return {'data': self.user_serializer.dump(user)}, 200


@api.route('/search')
class UsersSearchResource(UserBaseResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @api.marshal_with(user_search_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def post(self) -> tuple:
        try:
            request_data = SearchSerializer().load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        user_data = self.user_manager.get(**request_data)
        user_serializer = UserSerializer(many=True)

        return {
                   'data': user_serializer.dump(list(user_data['query'])),
                   'records_total': user_data['records_total'],
                   'records_filtered': user_data['records_filtered'],
               }, 200


@api.route('/xlsx')
class ExportUsersExcelResource(UserBaseResource):
    @api.doc(responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        try:
            request_data = SearchSerializer().load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        task = export_user_data_in_excel.apply_async(
            (current_user.id, request_data),
            countdown=5
        )

        return {
                   'task': task.id,
                   'url': url_for('tasks_task_status_resource', task_id=task.id,
                                  _external=True),
               }, 202


@api.route('/word')
class ExportUsersWordResource(UserBaseResource):
    @api.doc(responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        try:
            request_data = SearchSerializer().load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        try:
            serializer = UserExportWordSerializer()
            request_args = serializer.load(request.args.to_dict(),
                                           unknown=EXCLUDE)
            to_pdf = request_args.get('to_pdf', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        task = export_user_data_in_word.apply_async(
            args=[current_user.id, request_data, to_pdf]
        )

        return {
                   'task': task.id,
                   'url': url_for('tasks_task_status_resource', task_id=task.id,
                                  _external=True),
               }, 202


@api.route('/word_and_xlsx')
class ExportUsersExcelAndWordResource(UserBaseResource):
    @api.doc(responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self) -> tuple:
        try:
            request_data = SearchSerializer().load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        try:
            serializer = UserExportWordSerializer()
            request_args = serializer.load(request.args.to_dict(),
                                           unknown=EXCLUDE)
            to_pdf = request_args.get('to_pdf', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        create_word_and_excel_documents.apply_async(
            args=[current_user.id, request_data, to_pdf]
        )

        return {}, 202
