from celery.result import AsyncResult
from flask_login import current_user
from marshmallow import EXCLUDE
from werkzeug.exceptions import NotFound

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.tasks import create_user_email_task, create_word_and_excel_documents_task, reset_password_email_task
from app.celery.word.tasks import export_user_data_in_word_task
from app.managers import BaseManager
from app.serializers import SearchSerializer, UserExportWordSerializer
from app.utils import get_attr_from_module


class TaskService(object):
    def __init__(self):
        self.manager = BaseManager()
        self.search_serializer = SearchSerializer()
        self.user_word_export_serializer = UserExportWordSerializer()

    def find_by_id(self, task_id: str) -> AsyncResult:
        def build_task_import(task_path: str) -> tuple:
            """Build a task import path.

            Parameters
            ----------
            task_path : str
                Task module path without `task` package.

            Returns
            -------
            tuple
                Contains two items:

                Task module path: task module path with `task` package
                and without task module.

                Task module: task module.

            Example
            -------
            >>> path = 'app.celery.word.export_user_data_in_word_task'
            >>> build_task_import(path)
            ('app.celery.word.tasks', 'export_user_data_in_word_task')

            """
            new_task_path = task_path.split('.')
            task_name = new_task_path.pop(len(new_task_path) - 1)
            new_task_path.append('tasks')
            return '.'.join(new_task_path), task_name

        query = f'SELECT name FROM celery_taskmeta WHERE task_id = "{task_id}"'
        cursor = self.manager.raw(query)

        try:
            task = ''
            for row in cursor.fetchone():
                module_path, module_name = build_task_import(row)
                task = get_attr_from_module(module_path, module_name)
        except TypeError:
            raise NotFound('Task not found')
        else:
            return task.AsyncResult(task_id)

    def send_create_user_email(self, **kwargs):
        # TODO: Pending to add fields validation
        create_user_email_task.delay(kwargs)

    def reset_password_email(self, **kwargs):
        reset_password_email_task.delay(kwargs)

    def export_user_data_in_excel(self, data):
        data = self.search_serializer.load(data)

        return export_user_data_in_excel_task.apply_async((current_user.id, data), countdown=5)

    def export_user_data_in_word(self, data: dict, args: dict):
        data = self.search_serializer.load(data)
        request_args = self.user_word_export_serializer.load(args, unknown=EXCLUDE)

        to_pdf = request_args.get('to_pdf', 0)
        return export_user_data_in_word_task.apply_async(args=[current_user.id, data, to_pdf])

    def export_user_data_in_excel_and_word(self, data, args):
        request_data = self.search_serializer.load(data)
        request_args = self.user_word_export_serializer.load(args, unknown=EXCLUDE)
        to_pdf = request_args.get('to_pdf', 0)

        return create_word_and_excel_documents_task.apply_async(args=[current_user.id, request_data, to_pdf])

    def check_task_status(self, task_id: str) -> dict:
        task_data = self.find_by_id(task_id)
        response = {'state': task_data.state}

        if task_data.state == 'PENDING':
            response.update(
                {
                    'current': 0,
                    'total': 1,
                }
            )
        elif task_data.state != 'FAILURE':
            response.update(
                {
                    'current': task_data.info.get('current', 0),
                    'total': task_data.info.get('total', 1),
                    'result': task_data.info.get('result'),
                }
            )
        else:
            response.update(
                {
                    'current': 1,
                    'total': 1,
                    'status': str(task_data.info),
                }
            )

        return response
