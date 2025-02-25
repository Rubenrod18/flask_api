from dependency_injector.wiring import inject, Provide
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_security import roles_accepted

from app.blueprints.base import BaseResource
from app.containers import Container
from app.extensions import api as root_api
from app.models.role import ROLES
from app.services.task import TaskService

blueprint = Blueprint('tasks', __name__, url_prefix='/api/tasks')
api = root_api.namespace('tasks', description='Tasks endpoints')


class TaskResource(BaseResource):
    @inject
    def __init__(self, rest_api: str, service: TaskService = Provide[Container.task_service], *args, **kwargs):
        super().__init__(rest_api, service, *args, **kwargs)


@api.route('/status/<string:task_id>')
class TaskStatusResource(TaskResource):
    @api.doc(
        responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not found', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @jwt_required()
    @roles_accepted(*ROLES)
    def get(self, task_id: str):
        return self.service.check_task_status(task_id), 200
