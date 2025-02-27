from marshmallow import fields, validate

from app.extensions import ma
from app.helpers.sqlalchemy_query_builder import ALL_OPERATORS
from app.managers import BaseManager


class ManagerMixin:
    manager_classes = {}

    def get_manager(self, manager_name: str) -> type[BaseManager]:
        return self._get_manager_class(manager_name)

    def _get_manager_class(self, manager_name: str) -> type[BaseManager]:
        return self.manager_classes.get(manager_name)()


class _SearchValueSerializer(ma.Schema):
    field_name = fields.Str(required=True)
    field_operator = fields.Str(required=True, validate=validate.OneOf(sorted(ALL_OPERATORS)))
    field_value = fields.Raw(required=True)


class _SearchOrderSerializer(ma.Schema):
    field_name = fields.Str(required=True)
    sorting = fields.Str(required=True, validate=validate.OneOf(['asc', 'desc']))


class SearchSerializer(ma.Schema):
    search = fields.List(fields.Nested(_SearchValueSerializer))
    order = fields.List(fields.Nested(_SearchOrderSerializer))
    items_per_page = fields.Integer(validate=validate.Range(min=1))
    page_number = fields.Integer(validate=validate.Range(min=1))
