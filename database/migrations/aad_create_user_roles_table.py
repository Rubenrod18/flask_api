import os

from flask_login import UserMixin
from playhouse.migrate import migrate, ForeignKeyField, CharField, FixedCharField, DateField, BooleanField, \
    TimestampField
from playhouse.shortcuts import model_to_dict

from app.extensions import db_wrapper
from app.models.base import Base as BaseModel
from app.models.role import Role as RoleModel
from app.models.user import User as UserModel, UserRoles as UserRolesModel
from database.migrations import migrate_actions, rollback_actions, migrator


class _OldUser(BaseModel, UserMixin):
    class Meta:
        table_name = 'users'

    created_by = ForeignKeyField('self', null=True, backref='children', column_name='created_by')
    role = ForeignKeyField(RoleModel, backref='roles')
    name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField(null=False)
    genre = FixedCharField(max_length=1, choices=(('m', 'male',), ('f', 'female')), null=True)
    birth_date = DateField()
    active = BooleanField(default=True)
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)


class CreateUserRolesTable():

    def __init__(self):
        self.name = os.path.basename(__file__)[:-3]
        self.table = 'users_roles_through'

    def _exists_table(self) -> bool:
        exists = False
        tables = db_wrapper.database.get_tables()

        for table in tables:
            if table == self.table:
                exists = True
                break

        return exists

    def _drop_foreign_key_constraint_users_table(self) -> list:
        """ https://www.sqlite.org/lang_altertable.html """

        UserModel._meta.table_name = 'new_users'
        db_wrapper.database.create_tables([UserModel])

        user_data = _OldUser.select()
        user_roles_relations = []

        for item in user_data:
            new_user = model_to_dict(item, recurse=False)
            role_id = new_user.get('role')

            user_roles_relations.append({
                'user_id': new_user.get('id'),
                'role_id': role_id,
            })
            if 'role' in new_user:
                del new_user['role']

            UserModel.create(**new_user)

        db_wrapper.database.execute_sql('DROP TABLE users;')

        migrate(
            migrator.rename_table(old_name='new_users', new_name='users')
        )

        migrate(
            migrator.add_index(table='users', columns=['email'], unique=True),
            migrator.add_index(table='users', columns=['created_by']),
        )

        return user_roles_relations

    def _add_foreign_key_constraint_users_table(self) -> None:
        """ https://www.sqlite.org/lang_altertable.html """

        _OldUser._meta.table_name = 'old_users'
        db_wrapper.database.create_tables([_OldUser])

        user_data = UserModel.select()

        for item in user_data:
            old_user = model_to_dict(item, recurse=False)
            old_user['role'] = item.roles[0].id

            if 'roles' in old_user:
                del old_user['roles']

            _OldUser.create(**old_user)

        db_wrapper.database.execute_sql('DROP TABLE users;')
        db_wrapper.database.execute_sql('DROP TABLE users_roles_through;')

        migrate(
            migrator.drop_index(table='old_users', index_name='_olduser_email'),
            migrator.drop_index(table='old_users', index_name='_olduser_created_by'),
            migrator.drop_index(table='old_users', index_name='_olduser_role_id'),
            migrator.rename_table(old_name='old_users', new_name='users')
        )

        migrate(
            migrator.add_index(table='users', columns=['email'], unique=True),
            migrator.add_index(table='users', columns=['created_by']),
            migrator.add_index(table='users', columns=['role_id']),
        )

    @migrate_actions
    def up(self):
        if not self._exists_table():
            # TODO: peewee 3.13.3 doesn't have implemented "drop_foreign_key_constraint" method
            # migrate(migrator.drop_foreign_key_constraint('users', 'user_role_id'))
            user_roles_relations = self._drop_foreign_key_constraint_users_table()

            db_wrapper.database.create_tables([UserRolesModel])
            for user_role_relation in user_roles_relations:
                UserRolesModel(**user_role_relation).save()

    @rollback_actions
    def down(self):
        if self._exists_table():
            # TODO: peewee 3.13.3 doesn't have implemented "add_foreign_key_constraint" method
            # migrate(migrator.add_foreign_key_constraint('users', 'user_role_id'))
            self._add_foreign_key_constraint_users_table()
