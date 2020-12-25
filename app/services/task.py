from celery.local import PromiseProxy
from flask_login import current_user
from marshmallow import ValidationError, EXCLUDE
from werkzeug.exceptions import NotFound, UnprocessableEntity

from app.celery.excel.tasks import export_user_data_in_excel
from app.celery.tasks import create_user_email, create_word_and_excel_documents
from app.celery.word.tasks import export_user_data_in_word
from app.managers import BaseManager
from app.serializers import SearchSerializer, UserExportWordSerializer
from app.utils import get_attr_from_module


class TaskService(object):

    def __init__(self):
        self.manager = BaseManager()
        self.search_serializer = SearchSerializer()
        self.user_word_export_serializer = UserExportWordSerializer()

    def find_by_id(self, task_id: str) -> PromiseProxy:
        # TODO: pending to define documentation
        def build_task_import(row: str) -> tuple:
            row_list = row.split('.')
            class_name = row_list.pop(len(row_list) - 1)
            row_list.append('tasks')
            return '.'.join(row_list), class_name

        query = f'SELECT name FROM celery_taskmeta WHERE task_id = "{task_id}"'
        cursor = self.manager.raw(query)

        try:
            task = ''
            for row in cursor.fetchone():
                module_name, class_name = build_task_import(row)
                task = get_attr_from_module(module_name, class_name)
        except TypeError:
            raise NotFound('Task not found')
        return task

    def send_create_user_email(self, **kwargs):
        # TODO: Pending to add fields validation
        create_user_email.delay(kwargs)

    def export_user_data_in_excel(self, data):
        try:
            data = self.search_serializer.load(data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return export_user_data_in_excel.apply_async(
            (current_user.id, data),
            countdown=5
        )

    def export_user_data_in_word(self, data: dict, args: dict):
        try:
            data = self.search_serializer.load(data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        try:
            request_args = self.user_word_export_serializer.load(args,
                                                                 unknown=EXCLUDE)
            to_pdf = request_args.get('to_pdf', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return export_user_data_in_word.apply_async(
            args=[current_user.id, data, to_pdf]
        )

    def export_user_data_in_excel_and_word(self, data, args):
        try:
            request_data = self.search_serializer.load(data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        try:
            request_args = self.user_word_export_serializer.load(args,
                                                                 unknown=EXCLUDE)
            to_pdf = request_args.get('to_pdf', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        return create_word_and_excel_documents.apply_async(
            args=[current_user.id, request_data, to_pdf]
        )
