from datetime import datetime

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
        if self.id is None:
            self.created_at = datetime.utcnow()

        if self.deleted_at is None:
            self.updated_at = datetime.utcnow()
        else:
            self.updated_at = self.deleted_at

        return super(User, self).save(*args, **kwargs)

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
