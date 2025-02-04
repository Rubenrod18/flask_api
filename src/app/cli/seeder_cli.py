import collections
from abc import ABC

from app.blueprints import get_blueprint_modules
from app.blueprints.base.tests.base_factory import BaseSeedFactory
from app.cli._base_cli import _BaseCli
from app.helpers import ModuleHelper


class SeederCli(_BaseCli, ABC):
    @staticmethod
    def __get_seeder_instances(modules: list) -> dict:
        """Get Seeder instances."""
        seeders = {}
        for item in modules:
            if ModuleHelper.exists_attr_in_module(item, 'Seeder'):
                seeder_instance = ModuleHelper.get_attr_from_module(item, 'Seeder')
                seeders[seeder_instance.priority] = seeder_instance
        return seeders

    def __get_seeders(self) -> dict:
        """Get Blueprints via dynamic way."""
        seeder_modules = [f'{item}.tests.seeder' for item in get_blueprint_modules()]
        return self.__get_seeder_instances(seeder_modules)

    def run_command(self):
        session = BaseSeedFactory.get_db_session()
        try:
            seeders = self.__get_seeders()
            ordered_seeders = collections.OrderedDict(sorted(seeders.items()))
            for seed in ordered_seeders.values():
                seed()
            session.commit()
            print(' Database seeding completed successfully.')  # noqa
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
