from celery import states
from celery.result import AsyncResult
from flask_login import current_user
from marshmallow import EXCLUDE

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.tasks import create_user_email_task, create_word_and_excel_documents_task, reset_password_email_task
from app.celery.word.tasks import export_user_data_in_word_task
from app.managers import BaseManager
from app.serializers import SearchSerializer, UserExportWordSerializer


class TaskService(object):
    def __init__(self):
        self.manager = BaseManager()
        self.search_serializer = SearchSerializer()
        self.user_word_export_serializer = UserExportWordSerializer()

    @staticmethod
    def check_task_status(task_id: str) -> dict:
        task_data = AsyncResult(task_id)
        response = {'state': task_data.state}

        if task_data.state == states.PENDING:
            response.update({'current': 0, 'total': 1})
        elif task_data.state in [states.STARTED, states.SUCCESS]:
            response.update(task_data.info)
        else:
            response.update({'current': 1, 'total': 1})

        return response

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
