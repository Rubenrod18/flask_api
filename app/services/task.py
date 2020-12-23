from celery.local import PromiseProxy
from werkzeug.exceptions import NotFound

from app.managers import BaseManager
from app.utils import get_attr_from_module


class TaskService(object):

    def __init__(self):
        self.manager = BaseManager()

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
