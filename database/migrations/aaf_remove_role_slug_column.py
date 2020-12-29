import os

from flask_security import RoleMixin
from playhouse.migrate import migrate, CharField, TimestampField, TextField
from playhouse.shortcuts import model_to_dict

from app.extensions import db_wrapper
from app.models import Base as BaseModel, Role as RoleModel
from database.migrations import migrate_actions, rollback_actions, migrator


class _OldRole(BaseModel, RoleMixin):
    class Meta:
        table_name = 'roles'

    name = CharField()
    description = TextField(null=True)
    slug = CharField(unique=True)
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)


class RemoveRoleSlugColumn:

    def __init__(self):
        self.name = os.path.basename(__file__)[:-3]
        self.table = 'roles'
        self.column_name = 'slug'

    def _exists_column(self) -> bool:
        query = 'PRAGMA table_info("%s")' % self.table
        cursor = db_wrapper.database.execute_sql(query)
        exists = False

        for row in cursor.fetchall():
            if self.column_name == row[1]:
                exists = True
                break

        return exists

    @staticmethod
    def _drop_unique_constraint_roles_table() -> None:
        """ https://www.sqlite.org/lang_altertable.html """
        roles = []

        role_data = _OldRole.select()

        for item in role_data:
            new_role = model_to_dict(item, recurse=False)
            new_role['label'] = new_role['name'].capitalize()
            new_role['name'] = new_role['slug']
            del new_role['slug']

            roles.append(new_role)

        db_wrapper.database.execute_sql('DROP TABLE roles;')

        db_wrapper.database.create_tables([RoleModel])

        for role in roles:
            RoleModel.insert(**role).execute()

    @staticmethod
    def _add_unique_constraint_roles_table() -> None:
        """ https://www.sqlite.org/lang_altertable.html """
        roles = []

        role_data = RoleModel.select()

        for item in role_data:
            new_role = model_to_dict(item, recurse=False)
            new_role['slug'] = new_role.get('name')
            new_role['name'] = new_role.get('label')
            del new_role['label']

            roles.append(new_role)

        db_wrapper.database.execute_sql('DROP TABLE roles;')

        _OldRole._meta.table_name = 'roles'
        db_wrapper.database.create_tables([_OldRole])

        migrate(
            migrator.drop_index(table='roles', index_name='_oldrole_slug'),
            migrator.add_index(table='roles', columns=['slug'], unique=True),
        )

        for role in roles:
            _OldRole.insert(**role).execute()

    @migrate_actions
    def up(self):
        if self._exists_column():
            # TODO: peewee 3.13.3 doesn't have implemented "drop_foreign_key_constraint" method
            self._drop_unique_constraint_roles_table()

    @rollback_actions
    def down(self):
        if not self._exists_column():
            # TODO: peewee 3.13.3 doesn't have implemented "add_foreign_key_constraint" method
            self._add_unique_constraint_roles_table()
