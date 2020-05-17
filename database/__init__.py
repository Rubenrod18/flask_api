import functools
import time

from faker import Faker
from faker.providers import person, file
from faker.providers import date_time

fake = Faker()
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(file)

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