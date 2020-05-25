import logging
import os
import os.path
from pydoc import locate

logger = logging.getLogger(__name__)


def get_models() -> list:
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    models = []

    dirs.remove(os.path.basename(__file__))
    dirs.remove(os.path.basename('base.py'))

    for filename in dirs:
        basename = filename[:-3]

        if filename.endswith('.py'):
            path = '{}.{}.{}'.format(__name__, basename, basename.capitalize())
            model_class = locate(path)
            models.append(model_class)

    path = '{}.{}.{}'.format(__name__, 'user', 'UserRoles')
    model_class = locate(path)
    models.append(model_class)

    return models
