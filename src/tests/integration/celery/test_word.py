import os

from app.celery import ContextTask, make_celery
from app.celery.word.tasks import export_user_data_in_word_task_logic
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.file_storages import LocalStorage
from app.models import Document
from app.utils.constants import MS_WORD_MIME_TYPE, PDF_MIME_TYPE
from tests.base.base_test import BaseTest


class WordTaskTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.local_storage = LocalStorage()
        self.celery = make_celery(self.app)

    def test_export_user_data_in_word_task(self):
        user = UserFactory()
        request_data = {
            'search': [],
            'order': [
                {'field_name': 'name', 'sorting': 'asc'},
            ],
            'items_per_page': 100,
            'page_number': 1,
        }
        test_cases = [
            ({'created_by': user.id, 'request_data': request_data, 'to_pdf': 1}, PDF_MIME_TYPE, 'pdf'),
            ({'created_by': user.id, 'request_data': request_data, 'to_pdf': 0}, MS_WORD_MIME_TYPE, 'docx'),
        ]
        doc_id = 0

        @self.celery.task(bind=True, base=ContextTask)
        def test_task(self, created_by, request_data, to_pdf):
            return export_user_data_in_word_task_logic(self, created_by, request_data, to_pdf)

        for kwargs, mimetype, file_ext in test_cases:
            task_result = test_task.apply(kwargs=kwargs).get()
            # NOTE: Commit to refresh the test session and see changes made by the Celery task
            #       Keep this here to avoid stale data issues in assertions.
            db.session.commit()
            doc_id += 1

            self.assertTrue(isinstance(task_result, dict), task_result)
            self.assertEqual(task_result.get('current'), 3, task_result)
            self.assertEqual(task_result.get('total'), 3, task_result)
            self.assertEqual(task_result.get('status'), 'Task completed!', task_result)
            self.assertTrue(isinstance(task_result.get('result'), dict), task_result)
            self.assertEqual(task_result['result'].get('id'), doc_id, task_result)
            self.assertTrue(task_result['result'].get('name').find(f'_users.{file_ext}') != -1, task_result)
            self.assertEqual(task_result['result'].get('mime_type'), mimetype, task_result)
            self.assertGreater(task_result['result'].get('size'), 0, task_result)
            self.assertIsNotNone(task_result['result'].get('created_at'), task_result)
            self.assertIsNotNone(task_result['result'].get('updated_at'), task_result)
            self.assertIsNone(task_result['result'].get('deleted_at'), task_result)
            self.assertEqual(
                task_result['result'].get('url'),
                f'http://{os.getenv("SERVER_NAME")}/api/documents/{doc_id}',
                task_result,
            )
            self.assertEqual(
                task_result['result'].get('created_by'),
                {'id': user.id, 'email': user.email, 'name': user.name, 'last_name': user.last_name},
                task_result,
            )

            query = db.session.query(Document)
            self.assertEqual(len(query.filter(Document.mime_type == mimetype).all()), 1)
            self.assertTrue(os.path.exists(query.first().get_filepath()))
            self.assertGreater(self.local_storage.get_filesize(query.first().get_filepath()), 0)
