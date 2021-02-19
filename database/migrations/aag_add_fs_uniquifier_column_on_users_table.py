import os

from peewee import TextField
from playhouse.migrate import migrate

from app.extensions import db_wrapper
from app.models.user import User as UserModel
from database.migrations import migrate_actions, rollback_actions, migrator


class AddFsUniquifierColumnOnUsersTable:

    def __init__(self):
        self.name = os.path.basename(__file__)[:-3]
        self.table = 'users'
        self.column_name = 'fs_uniquifier'
        self.field = TextField(null=False)
        self.columns = UserModel.get_fields()

    def _exists_column(self) -> bool:
        query = 'PRAGMA table_info("%s")' % self.table
        cursor = db_wrapper.database.execute_sql(query)
        exists = False

        for row in cursor.fetchall():
            if self.column_name == row[1]:
                exists = True
                break

        return exists

    @migrate_actions
    def up(self):
        if not self._exists_column():
            migrate(
                migrator.add_column(self.table, self.column_name, self.field)
            )

    @rollback_actions
    def down(self):
        if self._exists_column():
            migrate(
                migrator.drop_column(self.table, self.column_name)
            )
