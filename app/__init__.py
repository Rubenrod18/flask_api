import logging
import os

import flask
from celery import Celery
from flask import Flask

from app import extensions
from app.blueprints import blueprints


def create_app(env_config: str) -> Flask:
    app = flask.Flask(__name__)
    app.config.from_object(env_config)

    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    init_app(app)
    register_blueprints(app)

    return app


def init_app(app: Flask) -> None:
    """Call the method 'init_app' to register the extensions in the flask.Flask
    object passed as parameter.

    :app: flask.Flask object
    :returns: None

    """
    extensions.init_app(app)


def register_blueprints(app: Flask) -> None:
    """Register all blueprints.

    :app: flask.Flask object
    :returns: None

    """
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
