from datetime import datetime

from marshmallow import fields, validate

from app.extensions import ma
from app.utils import QUERY_OPERATORS, STRING_QUERY_OPERATORS


class TimestampField(fields.Field):
    """Field that serializes to timestamp integer and deserializes to a
    datetime.datetime class."""

    def _serialize(self, value, attr, obj, **kwargs):
        if not isinstance(value, datetime):
            return None
        return (datetime.fromtimestamp(value.timestamp())
                .strftime('%Y-%m-%d %H:%M:%S'))

    def _deserialize(self, value, attr, data, **kwargs):
        return datetime.timestamp(value)


class _SearchValueSchema(ma.Schema):
    field_name = fields.Str()
    field_operator = fields.Str(
        validate=validate.OneOf(set(QUERY_OPERATORS + STRING_QUERY_OPERATORS))
    )
    field_value = fields.Raw()


class _SearchOrderSchema(ma.Schema):
    field_name = fields.Str()
    sorting = fields.Str(validate=validate.OneOf(['asc', 'desc']))


class SearchSchema(ma.Schema):
    search = fields.List(fields.Nested(_SearchValueSchema))
    order = fields.List(fields.Nested(_SearchOrderSchema))
    items_per_page = fields.Integer()
    page_number = fields.Integer()
