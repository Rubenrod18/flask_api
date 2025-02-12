"""Package for managing the database.

The database package can creates and migrates tables and it can
fills them with fake data.

"""

import functools
import time

from faker import Faker
from faker.providers import date_time, file, person
from sqlalchemy import inspect

from app.extensions import db

fake = Faker()
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(file)


def init_database() -> None:
    print(' Creating tables...')  # noqa
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    if not table_names:
        db.create_all()

    print(' Tables created!')  # noqa


def seed_actions(fnc):
    @functools.wraps(fnc)
    def message(*args, **kwargs):
        seeder = args[0]

        print(' Seeding: %s' % seeder.name)  # noqa
        exec_time = 0
        try:
            start = time.time()
            res = fnc(*args, **kwargs)
            exec_time = round((time.time() - start), 2)
        finally:
            print(f' Seeded:  {seeder.name} ( {exec_time} seconds )')  # noqa
        return res

    return message
