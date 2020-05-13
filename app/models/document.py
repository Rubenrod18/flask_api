from peewee import CharField, ForeignKeyField, TimestampField, IntegerField

from app.models.base import Base as BaseModel
from app.models.user import User as UserModel


class Document(BaseModel):
    class Meta:
        table_name = 'documents'

    created_by = ForeignKeyField(UserModel, column_name='created_by')
    name = CharField()
    internal_name = CharField(unique=True)
    mime_type = CharField()
    filepath = CharField()
    size = IntegerField()
    created_at = TimestampField()
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)


