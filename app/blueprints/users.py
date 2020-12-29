from flask import Blueprint, request, url_for
from flask_security import roles_accepted

from app.blueprints.base import BaseResource
from app.extensions import api as root_api
from app.serializers import UserSerializer
from app.services.task import TaskService
from app.services.user import UserService
from app.swagger import (user_input_sw_model, user_output_sw_model,
                         user_search_output_sw_model, search_input_sw_model)
from app.utils.decorators import token_required

_API_DESCRIPTION = ('Users with role admin or team_leader can manage '
                    'these endpoints.')

blueprint = Blueprint('users', __name__)
api = root_api.namespace('users', description=_API_DESCRIPTION)


class UserBaseResource(BaseResource):
    user_service = UserService()
    task_service = TaskService()
    user_serializer = UserSerializer()


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
        user = self.user_service.create(request.get_json())
        user_data = self.user_serializer.dump(user)
        self.task_service.send_create_user_email(**user_data)
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
        user = self.user_service.find(user_id)
        return {'data': self.user_serializer.dump(user)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(user_input_sw_model)
    @api.marshal_with(user_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def put(self, user_id: int) -> tuple:
        user = self.user_service.save(user_id, **request.get_json())
        return {'data': self.user_serializer.dump(user)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 422: 'Unprocessable Entity'},
             security='auth_token')
    @api.marshal_with(user_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader')
    def delete(self, user_id: int) -> tuple:
        user = self.user_service.delete(user_id)
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
        user_data = self.user_service.get(**request.get_json())
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
        task = self.task_service.export_user_data_in_excel(request.get_json())
        return {'task': task.id,
                'url': url_for('tasks_task_status_resource', task_id=task.id,
                               _external=True)
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
        payload, args = request.get_json(), request.args.to_dict()
        task = self.task_service.export_user_data_in_word(payload, args)
        return {'task': task.id,
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
        payload, args = request.get_json(), request.args.to_dict()
        self.task_service.export_user_data_in_excel_and_word(payload, args)
        return {}, 202
