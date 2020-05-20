from flask import Blueprint
from flask_restful import Api, Resource

from app.celery.excel.tasks import user_data_export_in_excel

from app.utils.decorators import token_required

blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')
api = Api(blueprint)


@api.resource('/status/<string:task_id>')
class TaskStatusResource(Resource):
    @token_required
    def get(self, task_id: str):
        response, status_code = {}, 404

        # TODO: pending to do this endpoint dynamic
        task = user_data_export_in_excel.AsyncResult(task_id)

        if task:
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
