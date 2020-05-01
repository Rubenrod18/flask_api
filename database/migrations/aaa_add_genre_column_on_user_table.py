import os

from peewee import FixedCharField
from playhouse.migrate import SqliteMigrator, migrate

from app.extensions import db_wrapper
from database.migrations import migrate_actions, rollback_actions

migrator = SqliteMigrator(db_wrapper.database)

class AddGenreColumnOnUserTable():
    name = os.path.basename(__file__)[:-3]
    table = 'users'
    column_name = 'genre'
    field = FixedCharField(max_length=1, choices=(('m', 'male',), ('f', 'female')), null=True)

    @classmethod
    @migrate_actions
    def up(self):
        migrate(
            migrator.add_column(self.table, self.column_name, self.field)
        )

    @classmethod
    @rollback_actions
    def down(self):
        migrate(
            migrator.drop_column(self.table, self.column_name)
        )