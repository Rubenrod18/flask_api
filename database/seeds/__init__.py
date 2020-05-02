import functools
import os
import time

from app.extensions import db_wrapper
from app.utils import class_for_name


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


def get_seeders() -> list:
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    seeders = []

    dirs.remove(os.path.basename(__file__))

    for filename in dirs:
        basename = filename[:-3]
        seed_class = basename[4:].title().replace('_', '')

        if filename.endswith('.py'):
            module_path = '{}.{}'.format(__name__, basename)
            seed = class_for_name(module_path, seed_class)

            seeders.append(seed)

    return seeders


def init_seed() -> None:
    seeders = get_seeders()

    with db_wrapper.database.atomic():
        for seed in seeders:
            seed()
        print(' Database seeding completed successfully.')