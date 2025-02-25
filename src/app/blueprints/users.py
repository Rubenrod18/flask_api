from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, url_for
from flask_jwt_extended import jwt_required
from flask_security import roles_accepted
from marshmallow import EXCLUDE

from app import serializers
from app.blueprints.base import BaseResource
from app.containers import Container
from app.extensions import api as root_api
from app.models.role import ADMIN_ROLE, ROLES, TEAM_LEADER_ROLE
from app.serializers import UserExportWordSerializer
from app.services.task import TaskService
from app.services.user import UserService
from app.swagger import search_input_sw_model, user_input_sw_model, user_search_output_sw_model, user_sw_model

blueprint = Blueprint('users', __name__)
api = root_api.namespace('users', description='Users with role admin or team_leader can manage these endpoints.')


class BaseUserResource(BaseResource):
    serializer_class = serializers.UserSerializer

    @inject
    def __init__(
        self,
        rest_api: str,
        service: UserService = Provide[Container.user_service],
        task_service: TaskService = Provide[Container.task_service],
        *args,
        **kwargs,
    ):
        super().__init__(rest_api, service, *args, **kwargs)
        self.task_service = task_service


class BaseUserTaskResource(BaseUserResource):
    serializer_class = serializers.SearchSerializer


@api.route('')
class NewUserResource(BaseUserResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.expect(user_input_sw_model)
    @api.marshal_with(user_sw_model, envelope='data', code=201)
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def post(self) -> tuple:
        serializer = self.serializer_class()
        validated_data = serializer.load(request.get_json())

        user = self.service.create(validated_data)
        user_data = serializer.dump(user)
        self.task_service.send_create_user_email(**user_data)

        return user_data, 201


@api.route('/<int:user_id>')
class UserResource(BaseUserResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.marshal_with(user_sw_model, envelope='data')
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
    @api.expect(user_input_sw_model)
    @api.marshal_with(user_sw_model, envelope='data')
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
    @api.marshal_with(user_sw_model, envelope='data')
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def delete(self, user_id: int) -> tuple:
        serializer = self.get_serializer()
        serializer.load({'id': user_id}, partial=True)

        user = self.service.delete(user_id)

        return serializer.dump(user), 200


@api.route('/search')
class UsersSearchResource(BaseUserResource):
    @api.doc(
        responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(search_input_sw_model)
    @api.marshal_with(user_search_output_sw_model)
    @jwt_required()
    @roles_accepted(*{ADMIN_ROLE, TEAM_LEADER_ROLE})
    def post(self) -> tuple:
        serializer = self.get_serializer(many=True)
        validated_data = serializers.SearchSerializer().load(request.get_json())

        doc_data = self.service.get(**validated_data)

        return {
            'data': serializer.dump(list(doc_data['query'])),
            'records_total': doc_data['records_total'],
            'records_filtered': doc_data['records_filtered'],
        }, 200


@api.route('/xlsx')
class ExportUsersExcelResource(BaseUserTaskResource):
    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        serializer = self.get_serializer()
        deserialized_data = serializer.load(request.get_json())

        task = self.task_service.export_user_data_in_excel(deserialized_data)

        return {'task': task.id, 'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True)}, 202


@api.route('/word')
class ExportUsersWordResource(BaseUserTaskResource):
    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        payload, args = request.get_json(), request.args.to_dict()
        serializer = self.get_serializer()
        deserialized_data = serializer.load(payload)
        request_args = UserExportWordSerializer().load(args, unknown=EXCLUDE)

        task = self.task_service.export_user_data_in_word(deserialized_data, request_args)

        return {
            'task': task.id,
            'url': url_for('tasks_task_status_resource', task_id=task.id, _external=True),
        }, 202


@api.route('/word_and_xlsx')
class ExportUsersExcelAndWordResource(BaseUserTaskResource):
    @api.doc(
        responses={202: 'Accepted', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(search_input_sw_model)
    @jwt_required()
    @roles_accepted(*ROLES)
    def post(self) -> tuple:
        payload, args = request.get_json(), request.args.to_dict()
        serializer = self.get_serializer()
        deserialized_data = serializer.load(payload)
        request_args = UserExportWordSerializer().load(args, unknown=EXCLUDE)

        self.task_service.export_user_data_in_excel_and_word(deserialized_data, request_args)

        return {}, 202
