import pytest

from app.celery.tasks import (
    create_word_and_excel_documents_task,
)
from app.database.factories.user_factory import UserFactory
from app.file_storages import LocalStorage


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestWordAndExcelTask:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.local_storage = LocalStorage()

    def test_create_word_and_excel_documents_tasks_are_called(self):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        kwargs = {'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}

        # NOTE: I didn't find the way to check that the tasks called in this task
        #       ran as I expected, the only way to check it out is to do a test
        #       per each task.
        result = create_word_and_excel_documents_task.apply(kwargs=kwargs).get()

        assert result
