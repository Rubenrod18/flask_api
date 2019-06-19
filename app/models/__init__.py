import os
import os.path
import peewee

from ..extensions import db_wrapper
from .person import Person

def init_app(app):
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    models = []

    for filename in dirs:
        basename = filename[:-3]

        if basename.istitle() and filename.endswith('.py'):
            models.append(basename)

    # TODO: This can do it better
    models = [Person]

    db_wrapper.database.create_tables(models)
