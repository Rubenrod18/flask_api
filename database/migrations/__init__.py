import functools
import os
import time

from peewee import CompositeKey, CharField
from playhouse.migrate import SqliteMigrator

from app.extensions import db_wrapper
from app.utils import get_attr_from_module

migrator = SqliteMigrator(db_wrapper.database)


class Migration(db_wrapper.Model):
    class Meta:
        table_name = 'migrations'
        primary_key = CompositeKey('name')

    name = CharField(unique=True, index=True)


def migrate_actions(fnc):
    @functools.wraps(fnc)
    def message(*args, **kwargs):
        migration = args[0]

        print(' Migrating: %s' % migration.name)
        exec_time = 0
        try:
            start = time.time()
            res = fnc(*args, **kwargs)

            with db_wrapper.database.atomic():
                Migration.create(name=migration.name)

            exec_time = round((time.time() - start), 2)
        finally:
            print(' Migrated:  %s ( %s seconds )' % (migration.name, exec_time))
        return res

    return message


def rollback_actions(fnc):
    @functools.wraps(fnc)
    def message(*args, **kwargs):
        migration = args[0]

        print(' Rolling back: %s' % migration.name)
        exec_time = 0
        try:
            start = time.time()
            res = fnc(*args, **kwargs)

            with db_wrapper.database.atomic():
                query = (Migration.delete()
                         .where(Migration.name == migration.name))
                query.execute()

            exec_time = round((time.time() - start), 2)
        finally:
            print(' Rolled back: %s ( %s seconds )' % (migration.name, exec_time))
        return res

    return message


def get_migration_names() -> list:
    abs_path = os.path.abspath(__file__)
    path = os.path.dirname(abs_path)
    dirs = os.listdir(path)

    migrations = []

    dirs.remove(os.path.basename(__file__))
    dirs.sort()

    for filename in dirs:
        basename = filename[:-3]

        if filename.endswith('.py'):
            migrations.append(basename)

    return migrations


def init_migrations(rollback: bool = False) -> None:
    migration_names = get_migration_names()

    rows = Migration.select()
    db_migration_names = [item.name for item in rows]

    if db_migration_names > migration_names:
        diff = list(set(db_migration_names) - set(migration_names))
    else:
        diff = list(set(migration_names) - set(db_migration_names))
    diff.sort()

    with db_wrapper.database.atomic():
        if rollback:
            if rows:
                migration_filename = rows[-1].name
                class_name = migration_filename[4:].title().replace('_', '')

                module_path = '{}.{}'.format(__name__, migration_filename)
                migration = get_attr_from_module(module_path, class_name)()

                migration.down()
            else:
                print(' There aren\'t any migration created.')
        else:
            if diff:
                for migration_filename in diff:
                    class_name = migration_filename[4:].title().replace('_', '')

                    module_path = '{}.{}'.format(__name__, migration_filename)
                    migration = get_attr_from_module(module_path, class_name)()

                    exists = Migration.get_or_none(name=migration.name)

                    if not exists:
                        migration.up()
            else:
                print(' Nothing to migrate.')
    db_wrapper.database.close()
