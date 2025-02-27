"""Package for building a Flask application.

The app package loads application configuration and registers
middleware, blueprints, database models, etc.

"""

import logging
import pprint

import flask
from flask import Flask, send_from_directory
from werkzeug.utils import import_string

from app import exceptions, extensions
from app.blueprints import BLUEPRINTS
from app.cli import cli_register
from app.middleware import Middleware


def _init_logging(app: Flask) -> None:
    del app.logger.handlers[:]
    loggers = [
        app.logger,
    ]
    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(app.config.get('LOGGING_LEVEL'))
    console_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
        )
    )
    handlers.append(console_handler)

    for logger in loggers:
        for handler in handlers:
            logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(app.config.get('LOGGING_LEVEL'))

    app.logger.debug(pprint.pformat(app.config, indent=4))
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def _register_blueprints(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


def _register_static_routes(app: Flask) -> None:
    @app.route('/static/<path:path>')
    def static_files(path: str):
        return send_from_directory(app.config['STATIC_FOLDER'], path)


def create_app(env_config: str | type['Config']) -> Flask:
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
    config = env_config

    if isinstance(env_config, str):
        config = import_string(env_config)

    app = flask.Flask(__name__, static_url_path=config.STATIC_FOLDER, template_folder=config.TEMPLATES_FOLDER)
    app.config.from_object(env_config)
    app.wsgi_app = Middleware(app)

    _init_logging(app)
    cli_register.init_app(app)
    extensions.init_app(app)
    _register_blueprints(app)
    _register_static_routes(app)
    exceptions.init_app(app)

    return app
