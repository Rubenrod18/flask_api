import logging

from celery.local import PromiseProxy
from flask import Blueprint
from flask_restx import Resource
from flask_security import roles_accepted
from werkzeug.exceptions import NotFound

from app.extensions import db_wrapper, api as root_api
from app.utils import get_attr_from_module

from app.utils.decorators import token_required

blueprint = Blueprint('tasks', __name__, url_prefix='/api/tasks')
api = root_api.namespace('tasks', description='Tasks endpoints')
logger = logging.getLogger(__name__)


class TaskResource(Resource):
    @staticmethod
    def get_task(task_id: str) -> PromiseProxy:
        def build_task_import(row: str) -> tuple:
            row_list = row.split('.')
            class_name = row_list.pop(len(row_list) - 1)
            row_list.append('tasks')
            return '.'.join(row_list), class_name

        query = f'SELECT name FROM celery_taskmeta WHERE task_id = "{task_id}"'
        cursor = db_wrapper.database.execute_sql(query)

        task = ''

        try:
            for row in cursor.fetchone():
                module_name, class_name = build_task_import(row)
                task = get_attr_from_module(module_name, class_name)
        except TypeError:
            raise NotFound('Task not found')

        return task


@api.route('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden',
                        404: 'Not found', 422: 'Unprocessable Entity'},
             security='auth_token')
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, task_id: str):
        task = self.get_task(task_id)

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

        return response, 200
