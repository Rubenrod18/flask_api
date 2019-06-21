from datetime import datetime

from peewee import *

from ..extensions import db_wrapper as db


class User(db.Model):
    class Meta:
        table_name = 'users'
    name = CharField()
    last_name = CharField()
    age = IntegerField()
    mother = CharField()
    father = CharField()
    birth_date = DateField()
    created_at = TimestampField(default=datetime.utcnow())
    updated_at = TimestampField(default=datetime.utcnow())
    deleted_at = TimestampField(default=None, null=True)
