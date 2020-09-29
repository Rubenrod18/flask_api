"""Package for building a Flask application.

The app package loads application configuration and registers middleware,
blueprints, database models, etc.

"""
import logging
import os

import flask
from flask import Flask

from app import extensions
from app.blueprints import blueprints
from app.middleware import Middleware


def create_app(env_config: str) -> Flask:
    """Builds an application based on environment configuration.

    Parameters
    ----------
    env_config : str
        Environment configuration values.

            config.ProdConfig: production
            config.DevConfig: development
            config.TestConfig: test

    Returns
    -------
    Flask
        A `flask.flask` instance.

    """
    app = flask.Flask(__name__)
    app.config.from_object(env_config)
    app.wsgi_app = Middleware(app)

    init_logging(app)
    init_app(app)
    register_blueprints(app)

    return app


def init_app(app: Flask) -> None:
    """Call the method 'init_app' to register the extensions in the flask.Flask
    object passed as parameter."""
    extensions.init_app(app)


def register_blueprints(app: Flask) -> None:
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
