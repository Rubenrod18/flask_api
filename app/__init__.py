"""Package for building a Flask application.

The app package loads application configuration and registers middleware,
blueprints, database models, etc.

"""
import logging
import os

import flask
from flask import Flask

from app import extensions, exceptions
from app.blueprints import BLUEPRINTS
from app.middleware import Middleware


def _register_blueprints(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


def _init_logging(app: Flask) -> None:
    log_basename = os.path.basename(app.config.get('ROOT_DIRECTORY'))
    log_dirname = '{}/app'.format(app.config.get('LOG_DIRECTORY'))
    log_filename = f'{log_dirname}/{log_basename}.log'

    config = {
        'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        'level': logging.DEBUG,
        'filename': log_filename,
    }

    logging.basicConfig(**config)


def create_app(env_config: str) -> Flask:
    """Builds an application based on environment configuration.

    Parameters
    ----------
    env_config
        Environment configuration.

    Returns
    -------
    Flask
        A `flask.flask` instance.

    Notes
    -----
    Environment configuration values could be::

            config.ProdConfig
            config.DevConfig
            config.TestConfig

    """
    app = flask.Flask(__name__)
    app.config.from_object(env_config)
    app.wsgi_app = Middleware(app)

    _init_logging(app)
    extensions.init_app(app)
    _register_blueprints(app)
    exceptions.init_app(app)

    return app
