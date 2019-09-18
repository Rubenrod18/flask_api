import flask

from .blueprints import blueprints
from . import models
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
    models.init_app(app)

def register_blueprints(app):
    """Register all blueprints.

    :app: flask.Flask object
    :returns: None

    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
