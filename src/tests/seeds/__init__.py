"""Registers Seeders.

NOTE: Seeders could be not follow strictly SOLID principles so they're
developing in this way to be easily to import in a dynamic way in the
`SeederCli`.

"""

import functools
import os
import time

from app.utils.dynamic_imports import get_attr_from_module


def seed_actions(fnc):
    @functools.wraps(fnc)
    def message(*args, **kwargs):
        seeder = args[0]

        print(f' Seeding: {seeder.name}')  # noqa: T201
        exec_time = 0
        try:
            start = time.time()
            res = fnc(*args, **kwargs)
            exec_time = round((time.time() - start), 2)
        finally:
            print(f' Seeded:  {seeder.name} ( {exec_time} seconds )')  # noqa: T201
        return res

    return message


def get_seeders() -> dict:
    """Get seeders via dynamic way."""

    def get_seeder_modules() -> list:
        """Get seeders modules."""
        abs_path = os.path.abspath(__file__)
        path = os.path.dirname(abs_path)
        dirs = os.listdir(path)

        dirs.remove(os.path.basename(__file__))

        return dirs

    def get_seeder_instances(modules: list) -> dict:
        """Get seeders instances."""
        seeders = {}

        for item in modules:
            if item != 'base_seeder.py' and item.endswith('.py'):
                abs_path_module = f'{__name__}.{item[:-3]}'
                seeder_instance = get_attr_from_module(abs_path_module, 'Seeder')()
                seeders[seeder_instance.priority] = seeder_instance

        return seeders

    seeder_modules = get_seeder_modules()
    return get_seeder_instances(seeder_modules)


SEEDERS = get_seeders()
