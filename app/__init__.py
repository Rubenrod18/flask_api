import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import flask
from flask import Flask

from .blueprints import blueprints
from . import extensions


def create_app(env_config: str) -> Flask:
    app = flask.Flask(__name__)
    app.config.from_object(env_config)

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
    log_dirname = app.config.get('LOG_DIRECTORY')
    log_filename = '{}/{}.log'.format(log_dirname, datetime.utcnow().strftime('%Y%m%d'))

    if not os.path.exists(log_dirname):
        os.mkdir(log_dirname)

    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=3, utc=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    kwargs = {
        'handlers': [handler],
        'level': logging.DEBUG,
    }

    logging.basicConfig(**kwargs)
    logger = logging.getLogger(__name__)
