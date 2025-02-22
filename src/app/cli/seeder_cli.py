import collections
from abc import ABC

from app.cli._base_cli import _BaseCli
from app.extensions import db
from app.utils.dynamic_imports import exists_attr_in_module, get_attr_from_module


class SeederCli(_BaseCli, ABC):
    @staticmethod
    def __get_seeder_instances(modules: list) -> dict:
        """Get Seeder instances."""
        seeders = {}
        for item in modules:
            if exists_attr_in_module(item, 'Seeder'):
                seeder_instance = get_attr_from_module(item, 'Seeder')
                seeders[seeder_instance.priority] = seeder_instance
        return seeders

    def __get_seeders(self) -> dict:
        """Get Blueprints via dynamic way."""
        seeder_modules = [
            'app.database.seeds.document_seeder',
            'app.database.seeds.role_seeder',
            'app.database.seeds.user_seeder',
        ]
        return self.__get_seeder_instances(seeder_modules)

    def run_command(self):
        try:
            seeders = self.__get_seeders()
            ordered_seeders = collections.OrderedDict(sorted(seeders.items()))
            for seed in ordered_seeders.values():
                seed()
            db.session.commit()
            print(' Database seeding completed successfully.')  # noqa
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.close()
