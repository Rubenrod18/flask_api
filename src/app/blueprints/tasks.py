from celery import states
from celery.result import AsyncResult
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_restx import Resource
from flask_security import roles_accepted

from app.extensions import api as root_api
from app.models.role import ROLES

blueprint = Blueprint('tasks', __name__, url_prefix='/api/tasks')
api = root_api.namespace('tasks', description='Tasks endpoints')


@api.route('/status/<string:task_id>')
class TaskStatusResource(Resource):
    @jwt_required()
    @roles_accepted(*ROLES)
    @api.doc(
        responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    def get(self, task_id: str):
        task_data = AsyncResult(task_id)
        response = {'state': task_data.state}

        if task_data.state == states.PENDING:
            response.update({'current': 0, 'total': 1})
        elif task_data.state in [states.STARTED, states.SUCCESS]:
            response.update(task_data.info)
        else:
            response.update({'current': 1, 'total': 1})

        return response, 200
