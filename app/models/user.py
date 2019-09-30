from datetime import datetime

from peewee import *

from app.utils import difference_in_years
from ..extensions import db_wrapper as db


class User(db.Model):
    class Meta:
        table_name = 'users'
    name = CharField()
    last_name = CharField()
    age = IntegerField()
    birth_date = DateField()
    created_at = TimestampField(default=datetime.utcnow())
    updated_at = TimestampField(default=datetime.utcnow())
    deleted_at = TimestampField(default=None, null=True)

    @classmethod
    def seed(cls, fake):
        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.now()

        age = difference_in_years(birth_date, current_date)

        user = User(
            name = fake.name(),
            last_name = fake.last_name(),
            age = age,
            birth_date = birth_date.strftime('%Y-%m-%d')
        )
        user.save()
