import functools
import os
import time

from peewee import CompositeKey, CharField

from app.extensions import db_wrapper
from app.models import get_models
from app.utils import class_for_name


class _Migration(db_wrapper.Model):
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
                _Migration.create(name=migration.name)

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
                query = _Migration.delete().where(_Migration.name == migration.name)
                query.execute()

            exec_time = round((time.time() - start), 2)
        finally:
            print(' Rolled back: %s ( %s seconds )' % (migration.name, exec_time))
        return res

    return message


def init_database() -> None:
    print(' Creating tables...')
    table_names = db_wrapper.database.get_tables()

    if not table_names:
        models = get_models()
        db_wrapper.database.create_tables(models)

    table_name = _Migration._meta.table_name
    exists = db_wrapper.database.table_exists(table_name)

    if not exists:
        db_wrapper.database.create_tables([_Migration])
    print(' Tables created!')


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

    rows = _Migration.select()
    db_migration_names = [item.name for item in rows]

    if db_migration_names > migration_names:
        diff = list(set(db_migration_names) - set(migration_names))
    else:
        diff = list(set(migration_names) - set(db_migration_names))

    with db_wrapper.database.atomic():
        if rollback == True:
            if rows:
                migration_filename = rows[-1].name
                class_name = migration_filename[4:].title().replace('_', '')

                module_path = '{}.{}'.format(__name__, migration_filename)
                migration = class_for_name(module_path, class_name)()

                migration.down()
            else:
                print(' There aren\'t any migration created.')
        else:
            if diff:
                for migration_filename in diff:
                    class_name = migration_filename[4:].title().replace('_', '')

                    module_path = '{}.{}'.format(__name__, migration_filename)
                    migration = class_for_name(module_path, class_name)()

                    exists = _Migration.get_or_none(name=migration.name)

                    if not exists:
                        migration.up()
            else:
                print(' Nothing to migrate.')
    db_wrapper.database.close()
