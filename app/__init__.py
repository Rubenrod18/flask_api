import logging
import os

import flask
from celery import Celery
from flask import Flask

from app.extensions import ContextTask


def create_app(env_config: str) -> Flask:
    app = flask.Flask(__name__)
    app.config.from_object(env_config)

    celery = init_celery(app)
    init_app(app)
    register_blueprints(app)

    return app


def init_app(app: Flask) -> None:
    """Call the method 'init_app' to register the extensions in the flask.Flask
    object passed as parameter.

    :app: flask.Flask object
    :returns: None

    """
    from . import extensions
    extensions.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Register all blueprints.

    :app: flask.Flask object
    :returns: None

    """
    from .blueprints import blueprints

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def init_logging(app: Flask) -> None:
    log_basename = os.path.basename(app.config.get('ROOT_DIRECTORY'))
    log_dirname = '{}/app'.format(app.config.get('LOG_DIRECTORY'))
    log_filename = f'{log_dirname}/{log_basename}.log'

    config = {
        'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        'level': logging.DEBUG,
        'filename': log_filename,
    }

    logging.basicConfig(**config)


def init_celery(app: Flask):
    celery = Celery(app.import_name, broker_url=app.config.get('CELERY_BROKER_URL'),
                    result_backend=app.config.get('CELERY_RESULT_BACKEND'), include=app.config.get('CELERY_INCLUDE'), )
    celery.conf.update(
        # General settings
        accept_content=app.config.get('CELERY_ACCEPT_CONTENT'),

        # Broker settings
        broker_url=app.config.get('CELERY_BROKER_URL'),

        # Task result backend settings
        result_backend=app.config.get('CELERY_RESULT_BACKEND'),
        result_serializer=app.config.get('CELERY_RESULT_SERIALIZER'),
        result_expires=app.config.get('CELERY_RESULT_EXPIRES'),
        result_extended=app.config.get('CELERY_RESULT_EXTENDED'),

        # Task settings
        task_serializer=app.config.get('CELERY_TASK_SERIALIZER'),

        # Time and date settings
        timezone=app.config.get('CELERY_TIMEZONE'),
        enable_utc=app.config.get('CELERY_ENABLE_UTC'),

        # Worker
        include=app.config.get('CELERY_INCLUDE'),

        # Task execution settings
        task_track_started=app.config.get('CELERY_TASK_TRACK_STARTED'),

        # Logging
        worker_log_format=app.config.get('CELERY_WORKER_LOG_FORMAT'),
        worker_task_log_format=app.config.get('CELERY_WORKER_TASK_LOG_FORMAT'),
    )

    TaskBase = celery.Task

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

    ContextTask.__call__ = __call__

    celery.register_task(ContextTask())
    return celery
