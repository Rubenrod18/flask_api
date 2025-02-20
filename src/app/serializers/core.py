from marshmallow import fields, validate

from app.extensions import ma
from app.utils.request_query_operator import QUERY_OPERATORS, STRING_QUERY_OPERATORS


class _SearchValueSerializer(ma.Schema):
    field_name = fields.Str()
    field_operator = fields.Str(validate=validate.OneOf(set(QUERY_OPERATORS + STRING_QUERY_OPERATORS)))
    field_value = fields.Raw()


class _SearchOrderSerializer(ma.Schema):
    field_name = fields.Str()
    sorting = fields.Str(validate=validate.OneOf(['asc', 'desc']))


class SearchSerializer(ma.Schema):
    search = fields.List(fields.Nested(_SearchValueSerializer))
    order = fields.List(fields.Nested(_SearchOrderSerializer))
    items_per_page = fields.Integer(min=1)
    page_number = fields.Integer(min=1)
