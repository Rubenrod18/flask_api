import logging

from flask import Blueprint
from flask_restx import Resource
from flask_security import roles_accepted

from app.extensions import api as root_api
from app.services.task import TaskService
from app.utils.decorators import token_required

blueprint = Blueprint('tasks', __name__, url_prefix='/api/tasks')
api = root_api.namespace('tasks', description='Tasks endpoints')
logger = logging.getLogger(__name__)


class TaskResource(Resource):
    task_service = TaskService()

    def check_task_status(self, task_id) -> dict:
        task = self.task_service.find_by_id(task_id)

        task_data = task.AsyncResult(task_id)
        if task_data.state == 'PENDING':
            response = {
                'state': task_data.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...',
            }
        elif task_data.state != 'FAILURE':
            response = {
                'state': task_data.state,
                'current': task_data.info.get('current', 0),
                'total': task_data.info.get('total', 1),
                'status': task_data.info.get('status', ''),
            }

            if 'result' in task_data.info:
                response['result'] = task_data.info['result']
        else:
            response = {
                'state': task_data.state,
                'current': 1,
                'total': 1,
                'status': str(task_data.info),
            }

        return response


@api.route('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden',
                        404: 'Not found', 422: 'Unprocessable Entity'},
             security='auth_token')
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, task_id: str):
        return self.check_task_status(task_id), 200
