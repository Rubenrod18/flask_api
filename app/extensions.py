"""Registers third party extensions."""
from flask import Flask
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_restx import Api
from flask_security import Security
from playhouse.flask_utils import FlaskDB

from app.celery import MyCelery
from config import Config

db_wrapper = FlaskDB()
security = Security()
mail = Mail()
celery = MyCelery()
ma = Marshmallow()

authorizations = {
    'auth_token': {
        'type': 'apiKey',
        'in': 'header',
        'name': Config.SECURITY_TOKEN_AUTHENTICATION_HEADER,
    },
}
api = Api(prefix='/api', title='Flask Api', description='A simple TodoMVC API',
          authorizations=authorizations)


def init_app(app: Flask) -> None:
    from app.models.user_roles import user_datastore

    db_wrapper.init_app(app)
    security.init_app(app, datastore=user_datastore, register_blueprint=False)
    mail.init_app(app)
    ma.init_app(app)
    api.init_app(app)

    # This hook ensures that a connection is opened to handle any queries
    # generated by the request.
    @app.before_request
    def db_connect() -> None:
        db_wrapper.database.connect(reuse_if_open=True)

    # This hook ensures that the connection is closed when we've finished
    # processing the request.
    @app.teardown_request
    def db_close(exc) -> None:
        if not db_wrapper.database.is_closed():
            db_wrapper.database.close()
