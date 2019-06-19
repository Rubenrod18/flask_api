from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()

def init_app(app):
    db_wrapper.init_app(app)
