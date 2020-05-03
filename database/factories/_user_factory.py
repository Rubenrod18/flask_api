from datetime import datetime, timedelta
from random import randint

from peewee import fn

from app.models.role import Role as RoleModel
from app.models.user import User as UserModel
from database import fake


class _UserFactory():
    def _fill(self, params: dict = None) -> dict:
        if params is None:
            params = {}

        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(31, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in params:
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        role = (RoleModel.select()
                .where(RoleModel.deleted_at.is_null())
                .order_by(fn.Random())
                .get())

        return {
            'role': params.get('role') if params.get('role') else role,
            'name': params.get('name') if params.get('name') else fake.name(),
            'last_name': params.get('last_name') if params.get('last_name') else fake.last_name(),
            'email': params.get('email') if params.get('email') else fake.random_element(
                [fake.email(), fake.safe_email(), fake.free_email(), fake.company_email()]),
            'genre': params.get('genre') if params.get('genre') else fake.random_element(['m', 'f']),
            'password': params.get('password') if params.get('password') else '123456',
            'birth_date': params.get('birth_date') if params.get('birth_date') else birth_date.strftime('%Y-%m-%d'),
            'active': params.get('active') if params.get('active') else fake.boolean(),
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

    def make(self, params: dict = None) -> UserModel:
        data = self._fill(params)

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

    def create(self, params: dict = None) -> UserModel:
        if params is None:
            params = {}

        data = self._fill(params)

        return UserModel.create(**data)

    def bulk_create(self, total: int, params: dict = None) -> None:
        if params is None:
            params = {}

        data = []

        for item in range(total):
            data.append(self.make(params))

        UserModel.bulk_create(data)
