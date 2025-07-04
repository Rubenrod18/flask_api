import os

import pytest

from app.celery import ContextTask, make_celery
from app.celery.word.tasks import export_user_data_in_word_task_logic
from app.extensions import db
from app.file_storages import LocalStorage
from app.models import Document
from app.utils.constants import MS_WORD_MIME_TYPE, PDF_MIME_TYPE
from tests.factories.user_factory import UserFactory


# pylint: disable=attribute-defined-outside-init
class TestWordTask:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.local_storage = LocalStorage()
        self.celery = make_celery(app)

    @pytest.mark.parametrize(
        'to_pdf,expected_mimetype,file_ext',
        [
            (1, PDF_MIME_TYPE, 'pdf'),
            (0, MS_WORD_MIME_TYPE, 'docx'),
        ],
    )
    def test_export_user_data_in_word_task(self, to_pdf, expected_mimetype, file_ext):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        doc_id = 0

        @self.celery.task(bind=True, base=ContextTask)
        def test_task(self, created_by, request_data, to_pdf):
            return export_user_data_in_word_task_logic(self, created_by, request_data, to_pdf)

        task_result = test_task.apply(
            kwargs={'created_by': user.id, 'request_data': request_data, 'to_pdf': to_pdf}
        ).get()

        # NOTE: Commit to refresh the test session and see changes made by the Celery task
        #       Keep this here to avoid stale data issues in assertions.
        db.session.commit()
        doc_id += 1

        assert isinstance(task_result, dict), task_result
        assert task_result.get('current') == 3, task_result
        assert task_result.get('total') == 3, task_result
        assert task_result.get('status') == 'Task completed!', task_result
        assert isinstance(task_result.get('result'), dict), task_result
        assert task_result['result'].get('id') == doc_id, task_result
        assert task_result['result'].get('name').find(f'_users.{file_ext}') != -1, task_result
        assert task_result['result'].get('mime_type') == expected_mimetype, task_result
        assert task_result['result'].get('size') > 0, task_result
        assert task_result['result'].get('created_at'), task_result
        assert task_result['result'].get('updated_at'), task_result
        assert task_result['result'].get('deleted_at') is None, task_result
        assert task_result['result'].get('url') == f'http://{os.getenv("SERVER_NAME")}/api/documents/{doc_id}', (
            task_result
        )
        assert task_result['result'].get('created_by') == {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'last_name': user.last_name,
        }, task_result

        query = db.session.query(Document)
        assert len(query.filter(Document.mime_type == expected_mimetype).all()) == 1
        assert os.path.exists(query.first().get_filepath())
        assert self.local_storage.get_filesize(query.first().get_filepath()) > 0
