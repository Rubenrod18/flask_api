"""Registers third party extensions."""

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy

from app.celery import MyCelery
from app.helpers.custom_api import CustomApi
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
security = Security()
mail = Mail()
migrate = Migrate()
celery = MyCelery()
jwt = JWTManager()

authorizations = {
    'auth_token': {
        'type': 'apiKey',
        'in': 'header',
        'name': Config.SECURITY_TOKEN_AUTHENTICATION_HEADER,
    },
}
api = CustomApi(
    prefix='/api',
    title='Flask Api',
    description='A simple TodoMVC API',
    authorizations=authorizations,
)


def init_app(app: Flask) -> None:
    api.init_app(app)
    # Order matters: Initialize SQLAlchemy before Marshmallow
    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    _init_flask_security_too_app(app)
    jwt.init_app(app)
    _init_python_dependency_injector(app)

    @app.teardown_request
    def teardown_request_context(_) -> None:
        if not app.config['TESTING']:
            db.session.commit()
            db.session.remove()


def _init_flask_security_too_app(flask_app: Flask):
    from app.models.user import user_datastore

    security.init_app(flask_app, datastore=user_datastore, register_blueprint=False)


def _init_python_dependency_injector(flask_app: Flask):
    from app.containers import Container

    flask_app.container = Container()
