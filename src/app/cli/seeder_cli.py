import collections

from app.cli._base_cli import _BaseCli
from app.database import seeds
from app.extensions import db


class SeederCli(_BaseCli):
    def run_command(self):
        try:
            seeders = seeds.get_seeders()
            ordered_seeders = collections.OrderedDict(sorted(seeders.items()))
            for seeder in ordered_seeders.values():
                seeder.seed()
            db.session.commit()
            print(' Database seeding completed successfully.')  # noqa
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.close()
