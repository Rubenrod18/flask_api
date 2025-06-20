import pytest
from flask import current_app

from app.celery import ContextTask


# pylint: disable=attribute-defined-outside-init
class TestCeleryAppContext:
    @pytest.fixture(autouse=True)
    def setup(self):
        from app import create_app  # pylint: disable=import-outside-toplevel
        from app.celery import make_celery  # pylint: disable=import-outside-toplevel

        self.app = create_app('config.TestConfig')
        self.celery = make_celery(self.app)

    def test_task_runs_with_app_context(self):
        result_holder = {}

        @self.celery.task(base=ContextTask)
        def dummy_task():
            result_holder['app_name'] = current_app.name
            return True

        dummy_task()

        assert result_holder['app_name'] == self.app.name
