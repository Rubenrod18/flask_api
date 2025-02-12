"""Package for building a Flask application.

The app package loads application configuration and registers
middleware, blueprints, database models, etc.

"""
import logging
import os
import pprint

import flask
from flask import Flask

from app import exceptions
from app import extensions
from app.blueprints import BLUEPRINTS
from app.cli import cli_register
from app.middleware import Middleware


def _create_logging_file(app: Flask) -> str:
    log_basename = os.path.basename(app.config.get('ROOT_DIRECTORY'))
    log_dirname = '{}/app'.format(app.config.get('LOG_DIRECTORY'))
    log_filename = f'{log_dirname}/{log_basename}.log'

    log_directories = [app.config.get('LOG_DIRECTORY'), log_dirname]

    for log_dir in log_directories:
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

    return log_filename


def _init_logging(app: Flask) -> None:
    del app.logger.handlers[:]
    loggers = [
        app.logger,
    ]
    handlers = []

    console_handler = logging.FileHandler(filename=_create_logging_file(app))
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
    cli_register.init_app(app)
    extensions.init_app(app)
    _register_blueprints(app)
    exceptions.init_app(app)

    return app
