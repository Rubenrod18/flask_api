from datetime import datetime, date

from peewee import CharField, IntegerField, DateField, TimestampField

from . import fake
from app.utils import difference_in_years
from ..extensions import db_wrapper as db


class User(db.Model):
    class Meta:
        table_name = 'users'

    name = CharField()
    last_name = CharField()
    age = IntegerField()
    birth_date = DateField()
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def save(self, *args, **kwargs):
        current_date = datetime.utcnow()

        if self.id is None:
            self.created_at = current_date

        if self.deleted_at is None:
            self.updated_at = current_date
        else:
            self.updated_at = self.deleted_at

        return super(User, self).save(*args, **kwargs)

    @property
    def serialize(self):
        birth_date = self.birth_date
        deleted_at = self.deleted_at

        if isinstance(deleted_at, datetime):
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%M:%S')

        if isinstance(birth_date, date):
            birth_date = birth_date.strftime('%Y-%m-%d')

        data = {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name,
            'age': self.age,
            'birth_date': birth_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': deleted_at
        }

        return data

    @classmethod
    def fake(cls):
        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        age = difference_in_years(birth_date, current_date)

        return User(
            name=fake.name(),
            last_name=fake.last_name(),
            age=age,
            birth_date=birth_date.strftime('%Y-%m-%d'),
            created_at=datetime.utcnow()
        )

    @classmethod
    def seed(cls):
        user = User.fake()
        user.save()

        db.database.commit()
        db.database.close()
