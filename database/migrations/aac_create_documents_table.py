import os

from app.extensions import db_wrapper
from app.models.document import Document as DocumentModel
from database.migrations import migrate_actions, rollback_actions


class CreateDocumentsTable():

    def __init__(self):
        self.name = os.path.basename(__file__)[:-3]
        self.table = DocumentModel._meta.table_name

    def _exists_table(self) -> bool:
        exists = False
        tables = db_wrapper.database.get_tables()

        for table in tables:
            if table == self.table:
                exists = True
                break

        return exists

    @migrate_actions
    def up(self):
        if not self._exists_table():
            db_wrapper.database.create_tables([DocumentModel])

    @rollback_actions
    def down(self):
        if self._exists_table():
            db_wrapper.database.drop_tables([DocumentModel])
