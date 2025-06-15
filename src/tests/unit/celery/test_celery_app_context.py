import unittest

from flask import current_app

from app.celery import ContextTask


class TestCeleryAppContext(unittest.TestCase):
    def setUp(self):
        from app import create_app  # pylint: disable=import-outside-toplevel
        from app.celery import make_celery  # pylint: disable=import-outside-toplevel

        self.app = create_app('config.TestConfig')
        self.app.config['CELERY_BROKER_URL'] = 'memory://'
        self.app.config['CELERY_RESULT_BACKEND'] = 'rpc://'
        self.celery = make_celery(self.app)

    def test_task_runs_with_app_context(self):
        result_holder = {}

        @self.celery.task(base=ContextTask)
        def dummy_task():
            result_holder['app_name'] = current_app.name
            return True

        dummy_task()

        self.assertEqual(result_holder['app_name'], self.app.name)

    def test_task_runs_without_app_context(self):
        def __call__(self, *args, **kwargs):
            return self.run(*args, **kwargs)

        ContextTask.__call__ = __call__
        self.celery.Task = ContextTask

        result_holder = {}

        @self.celery.task(base=ContextTask)
        def dummy_task():
            result_holder['app_name'] = current_app.name
            return True

        with self.assertRaises(RuntimeError) as context:
            dummy_task()

        self.assertTrue(str(context.exception).find('Working outside of application context') != -1, context.exception)
