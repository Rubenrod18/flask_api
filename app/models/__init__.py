import logging
import os
import os.path

from ..extensions import db_wrapper
from .user import User

logger = logging.getLogger(__name__)

def init_app():
    pass
    # TODO: I need to think about what place it's better for this logic
    #create_tables()

def create_tables():
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    models = []

    for filename in dirs:
        basename = filename[:-3]

        if basename.istitle() and filename.endswith('.py'):
            models.append(basename)

    models = [User]

    # This line makes next error: raise OperationalError('Connection already opened.')
    tables = db_wrapper.database.get_tables()

    if tables == 0:
        db_wrapper.database.create_tables(models)
