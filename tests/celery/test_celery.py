from flask import Flask

from app.celery import make_celery, ContextTask


def test_register_context_task(app: Flask):
    celery = make_celery(app)
    assert isinstance(celery.tasks.get('app.celery.ContextTask'), ContextTask)
