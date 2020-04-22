from flask import Flask
from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()


def init_app(app: Flask) -> None:
    db_wrapper.init_app(app)
