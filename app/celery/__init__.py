from celery import Celery
from flask import Flask

from app.extensions import ContextTask


def init_celery(app: Flask) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    TaskBase = celery.Task

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

    ContextTask.__call__ = __call__

    celery.register_task(ContextTask())
    return celery
