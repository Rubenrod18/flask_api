import logging
import os
import sys
from datetime import datetime

import flask

from .blueprints import blueprints
from . import extensions


def create_app(env_config):
    app = flask.Flask(__name__)
    app.config.from_object(env_config)

    init_app(app)
    register_blueprints(app)

    return app


def init_app(app):
    """Call the method 'init_app' to register the extensions in the flask.Flask
    object passed as parameter.

    :app: flask.Flask object
    :returns: None

    """
    extensions.init_app(app)


def register_blueprints(app):
    """Register all blueprints.

    :app: flask.Flask object
    :returns: None

    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def logging_config():
    # Function for catching unexpected errors
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error('Uncaught exception',
                     exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    log_dirname = 'log/'
    log_filename = '{}.log'.format(datetime.utcnow().strftime('%Y%m%d'))
    log_fullpath = '{}{}'.format(log_dirname, log_filename)

    if not os.path.exists(log_dirname):
        os.mkdir(log_dirname)

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_fullpath,
                        format=FORMAT,
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
