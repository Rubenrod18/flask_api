from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, url_for
from flask_jwt_extended import jwt_required
from flask_login import current_user
from flask_security import roles_accepted
from marshmallow import EXCLUDE

from app import serializers, swagger as swagger_models
from app.blueprints.base import BaseResource
from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.tasks import create_user_email_task, create_word_and_excel_documents_task
from app.celery.word.tasks import export_user_data_in_word_task
from app.di_container import ServiceDIContainer
from app.extensions import api as root_api
from app.models.role import ADMIN_ROLE, ROLES, TEAM_LEADER_ROLE
from app.services.user import UserService

blueprint = Blueprint('users', __name__)
api = root_api.namespace('users', description='Users with role admin or team_leader can manage these endpoints.')


class BaseUserResource(BaseResource):
    @inject
    def __init__(
        self,
        rest_api: str,
        service: UserService = Provide[ServiceDIContainer.user_service],
        *args,
        **kwargs,
    ):
        super().__init__(rest_api, service, *args, **kwargs)


@api.route('')
class NewUserResource(BaseUserResource):
    serializer_class = serializers.UserSerializer

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.expect(swagger_models.user_input_sw_model)
    @api.marshal_with(swagger_models.user_sw_model, envelope='data', code=201)
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def post(self) -> tuple:
        serializer = self.serializer_class()
        validated_data = serializer.load(request.get_json())

        user = self.service.create(validated_data)
        user_data = serializer.dump(user)
        create_user_email_task.delay(user_data)

        return user_data, 201


@api.route('/<int:user_id>')
class UserResource(BaseUserResource):
    serializer_class = serializers.UserSerializer

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.marshal_with(swagger_models.user_sw_model, envelope='data')
    @jwt_required()
    @roles_accepted(ADMIN_ROLE)
    def get(self, user_id: int) -> tuple:
        serializer = self.serializer_class()
        serializer.load({'id': user_id}, partial=True)

        user = self.service.find(user_id)

        return serializer.dump(user), 200

    @api.doc(
        responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.user_input_sw_model)
    @api.marshal_with(swagger_models.user_sw_model, envelope='data')
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def put(self, user_id: int) -> tuple:
        json_data = request.get_json()
        json_data['id'] = user_id
        serializer = self.get_serializer()
        deserialized_data = serializer.load(json_data, unknown=EXCLUDE)

        user = self.service.save(user_id, **deserialized_data)

        return serializer.dump(user), 200

    @api.doc(
        responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.marshal_with(swagger_models.user_sw_model, envelope='data')
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def delete(self, user_id: int) -> tuple:
        serializer = self.get_serializer()
        serializer.load({'id': user_id}, partial=True)

        user = self.service.delete(user_id)

        return serializer.dump(user), 200


@api.route('/search')
class UsersSearchResource(BaseUserResource):
    serializer_classes = {
        'user': serializers.UserSerializer,
        'search': serializers.SearchSerializer,
    }

    @api.doc(
        responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.search_input_sw_model)
    @api.marshal_with(swagger_models.user_search_output_sw_model)
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def post(self) -> tuple:
        serializer = self.get_serializer('user', many=True)
        validated_data = self.get_serializer('search').load(request.get_json())

        doc_data = self.service.get(**validated_data)

        return {
            'data': serializer.dump(list(doc_data['query'])),
            'records_total': doc_data['records_total'],
            'records_filtered': doc_data['records_filtered'],
        }, 200


@api.route('/xlsx')
class ExportUsersExcelResource(BaseUserResource):
    serializer_class = serializers.SearchSerializer

    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        serializer = self.get_serializer()
        deserialized_data = serializer.load(request.get_json())

        task = export_user_data_in_excel_task.apply_async((current_user.id, deserialized_data), countdown=5)

        return {'task': task.id, 'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True)}, 202


@api.route('/word')
class ExportUsersWordResource(BaseUserResource):
    parser = api.parser()
    parser.add_argument('to_pdf', type=int, location='args', required=False, choices=(0, 1))

    serializer_classes = {
        'search': serializers.SearchSerializer,
        'user_export_word': serializers.UserExportWordSerializer,
    }

    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(parser, swagger_models.search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        payload, args = request.get_json(), request.args.to_dict()
        serializer = self.get_serializer('search')
        deserialized_data = serializer.load(payload)
        request_args = self.get_serializer('user_export_word').load(args, unknown=EXCLUDE)
        to_pdf = request_args.get('to_pdf', 0)

        task = export_user_data_in_word_task.apply_async(args=[current_user.id, deserialized_data, to_pdf])

        return {
            'task': task.id,
            'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True),
        }, 202


@api.route('/word_and_xlsx')
class ExportUsersExcelAndWordResource(BaseUserResource):
    parser = api.parser()
    parser.add_argument('to_pdf', type=int, location='args', required=False, choices=(0, 1))

    serializer_classes = {
        'search': serializers.SearchSerializer,
        'user_export_word': serializers.UserExportWordSerializer,
    }

    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(parser, swagger_models.search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        payload, args = request.get_json(), request.args.to_dict()
        serializer = self.get_serializer('search')
        deserialized_data = serializer.load(payload)
        request_args = self.get_serializer('user_export_word').load(args, unknown=EXCLUDE)
        to_pdf = request_args.get('to_pdf', 0)

        create_word_and_excel_documents_task.apply_async(args=[current_user.id, deserialized_data, to_pdf])

        return {}, 202
