import logging
import os
import os.path
from pydoc import locate

from faker import Faker
from faker.providers import person
from faker.providers import date_time

logger = logging.getLogger(__name__)

fake = Faker()
fake.add_provider(person)
fake.add_provider(date_time)


def get_models() -> list:
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    models = []

    dirs.remove(os.path.basename(__file__))

    for filename in dirs:
        basename = filename[:-3]

        if filename.endswith('.py'):
            path = '{}.{}.{}'.format(__name__, basename, basename.capitalize())
            model_class = locate(path)
            models.append(model_class)

    return models
