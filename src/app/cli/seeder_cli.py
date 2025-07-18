import collections

import flask_sqlalchemy

from app.cli.base_cli import BaseCli
from tests import seeds


class SeederCli(BaseCli):
    def __init__(self, db: flask_sqlalchemy.SQLAlchemy):
        self.db = db

    def run_command(self, *args, **kwargs):
        try:
            seeders = seeds.get_seeders()
            ordered_seeders = collections.OrderedDict(sorted(seeders.items()))
            for seeder in ordered_seeders.values():
                seeder.seed()
            self.db.session.commit()
            print(' Database seeding completed successfully.')  # noqa: T201
        except Exception as exc:
            self.db.session.rollback()
            raise exc
        finally:
            self.db.session.close()
