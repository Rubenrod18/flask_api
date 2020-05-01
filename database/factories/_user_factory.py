from datetime import datetime, timedelta
from random import randint

from peewee import fn

from app.models.role import Role as RoleModel
from app.models.user import User as UserModel
from database import fake


class _UserFactory():
    def _fill(self, data: dict = None) -> dict:
        if data is None:
            data = {}

        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(1, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in data:
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        role = (RoleModel.select()
                .where(RoleModel.deleted_at.is_null())
                .order_by(fn.Random())
                .get())

        return {
            'role': data.get('role') if data.get('role') else role,
            'name': data.get('name') if data.get('name') else fake.name(),
            'last_name': data.get('last_name') if data.get('last_name') else fake.last_name(),
            'email': data.get('email') if data.get('email') else fake.random_element(
                [fake.email(), fake.safe_email(), fake.free_email(), fake.company_email()]),
            'genre': data.get('genre') if data.get('genre') else fake.random_element(['m', 'f']),
            'password': data.get('password') if data.get('password') else '123456',
            'birth_date': data.get('birth_date') if data.get('birth_date') else birth_date.strftime('%Y-%m-%d'),
            'active': data.get('active') if data.get('active') else fake.boolean(),
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

    def make(self, data: dict = None) -> UserModel:
        data = self._fill(data)

        user = UserModel()
        user.role = data.get('role')
        user.name = data.get('name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        user.genre = data.get('genre')
        user.password = data.get('password')
        user.birth_date = data.get('birth_date')
        user.active = data.get('active')
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        user.deleted_at = data.get('deleted_at')

        return user

    def create(self, data: dict = None) -> UserModel:
        kwargs = self._fill(data)

        return UserModel.create(**kwargs)
