from peewee import *

from ..extensions import db_wrapper as db


class Person(db.Model):
    name = CharField()
    last_name = CharField()
    age = IntegerField()
    mother = CharField()
    father = CharField()
    birthplace = DateField()
