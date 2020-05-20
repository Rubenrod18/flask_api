import logging

from celery.local import PromiseProxy
from flask import Blueprint
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from app.extensions import db_wrapper
from app.utils import class_for_name

from app.utils.decorators import authenticated

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
            raise NotFound(description='Task not found')

        return task


@api.resource('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @authenticated
    def get(self, task_id: str):
        task_promise = self.get_task(task_id)

        task = task_promise.AsyncResult(task_id)
        status_code = 200
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current': 0,
                'total': 1,
                'status': 'Pending...',
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', ''),
            }

            if 'result' in task.info:
                response['result'] = task.info['result']
        else:
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),
            }

        return response, status_code
