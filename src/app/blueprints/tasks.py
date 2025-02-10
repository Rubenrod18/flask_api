from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from flask_security import roles_accepted

from app.extensions import api as root_api
from app.services.task import TaskService

blueprint = Blueprint('tasks', __name__, url_prefix='/api/tasks')
api = root_api.namespace('tasks', description='Tasks endpoints')


class TaskResource(Resource):
    task_service = TaskService()


@api.route('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @jwt_required()
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, task_id: str):
        return self.task_service.check_task_status(task_id), 200
