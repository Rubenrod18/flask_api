"""Package for managing the database.

The database package can creates and migrates tables and it can fills them
with fake data.

"""
import functools
import time

from faker import Faker
from faker.providers import person, file
from faker.providers import date_time

from app.extensions import db_wrapper
from app.models import get_models
from database.migrations import Migration

fake = Faker()
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(file)


def init_database() -> None:
    print(' Creating tables...')
    table_names = db_wrapper.database.get_tables()

    if not table_names:
        models = get_models()
        db_wrapper.database.create_tables(models)

    table_name = Migration._meta.table_name
    exists = db_wrapper.database.table_exists(table_name)

    if not exists:
        db_wrapper.database.create_tables([Migration])
    print(' Tables created!')


def seed_actions(fnc):
    @functools.wraps(fnc)
    def message(*args, **kwargs):
        seeder = args[0]

        print(' Seeding: %s' % seeder.name)
        exec_time = 0
        try:
            start = time.time()
            res = fnc(*args, **kwargs)
            exec_time = round((time.time() - start), 2)
        finally:
            print(' Seeded:  %s ( %s seconds )' % (seeder.name, exec_time))
        return res

    return message
