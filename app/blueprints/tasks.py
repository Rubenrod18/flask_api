import logging

from celery.local import PromiseProxy
from flask import Blueprint
from flask_restful import Api, Resource
from flask_security import roles_accepted
from werkzeug.exceptions import NotFound

from app.extensions import db_wrapper
from app.utils import class_for_name

from app.utils.decorators import token_required

blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class TaskResource(Resource):
    def get_task(self, task_id: str) -> PromiseProxy:
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
                task = class_for_name(module_name, class_name)
        except TypeError:
            raise NotFound('Task not found')

        return task


@api.resource('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, task_id: str):
        task = self.get_task(task_id)

        data = task.AsyncResult(task_id)
        if data.state == 'PENDING':
            response = {
                'state': data.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...',
            }
        elif task.state != 'FAILURE':
            response = {
                'state': data.state,
                'current': data.info.get('current', 0),
                'total': data.info.get('total', 1),
                'status': data.info.get('status', ''),
            }

            if 'result' in data.info:
                response['result'] = data.info['result']
        else:
            response = {
                'state': data.state,
                'current': 1,
                'total': 1,
                'status': str(data.info),
            }

        return response, 200
