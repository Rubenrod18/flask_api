import os

from peewee import FixedCharField
from playhouse.migrate import SqliteMigrator, migrate

from app.extensions import db_wrapper
from app.models.user import User as UserModel
from database.migrations import migrate_actions, rollback_actions

migrator = SqliteMigrator(db_wrapper.database)


class AddGenreColumnOnUserTable():
    name = os.path.basename(__file__)[:-3]
    table = 'users'
    column_name = 'genre'
    field = FixedCharField(max_length=1, choices=(('m', 'male',), ('f', 'female')), null=True)
    columns = UserModel.get_fields()

    @classmethod
    def _exists_genre_column(cls) -> bool:
        query = 'PRAGMA table_info("%s")' % cls.table
        cursor = db_wrapper.database.execute_sql(query)
        exists = False

        for row in cursor.fetchall():
            if cls.column_name == row[1]:
                exists = True
                break

        return exists

    @classmethod
    @migrate_actions
    def up(cls):
        if not cls._exists_genre_column():
            migrate(
                migrator.add_column(cls.table, cls.column_name, cls.field)
            )

    @classmethod
    @rollback_actions
    def down(cls):
        if cls._exists_genre_column():
            migrate(
                migrator.drop_column(cls.table, cls.column_name)
            )
