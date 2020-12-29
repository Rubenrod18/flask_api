"""Registers database models.

TODO: pending to define models with suffix "Model".

There is not posible to rename the models with suffix "Model" because
Flask-Security-Too doesn't allow it. Maybe in the next major version could be
available.
https://github.com/Flask-Middleware/flask-security/issues/395

"""
import logging
import os
import os.path
from pydoc import locate

from .base import Base
from .document import Document
from .role import Role
from .user import User
from .user_roles import UserRoles, user_datastore

logger = logging.getLogger(__name__)


def get_db_models() -> list:
    def build_model_class_name(basename: str) -> str:
        if basename.find('_'):
            tmp = [item.capitalize() for item in basename.split('_')]
            class_name = ''.join(tmp)
        else:
            class_name = basename.capitalize()

        return class_name

    def get_db_modules() -> list:
        abs_path = os.path.abspath(__file__)
        path = os.path.dirname(abs_path)
        dirs = os.listdir(path)

        dirs.remove(os.path.basename(__file__))
        dirs.remove(os.path.basename('base.py'))

        return dirs

    def get_db_classes(modules: list) -> list:
        models = []

        for module in modules:
            basename = module[:-3]

            if module.endswith('.py'):
                class_name = build_model_class_name(basename)
                class_path = '{}.{}.{}'.format(__name__, basename, class_name)
                model = locate(class_path)

                if model:
                    models.append(model)

        return models

    db_modules = get_db_modules()
    db_models = get_db_classes(db_modules)

    return db_models
