from marshmallow import fields, validate

from app.extensions import ma
from app.helpers.sqlalchemy_query_builder import ALL_OPERATORS
from app.repositories.base import BaseRepository


class RepositoryMixin:
    repository_classes = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._validate_repository_classes()

    @classmethod
    def _validate_repository_classes(cls):
        if cls.repository_classes:
            for name, repository in cls.repository_classes.items():
                if not isinstance(repository, type):
                    raise TypeError(f"{cls.__name__}.repository_classes['{name}'] must be a class")
                if not issubclass(repository, BaseRepository):
                    raise TypeError(f"{cls.__name__}.repository_classes['{name}'] must inherit from BaseRepository")

    def get_repository(self, repository_name: str) -> type[BaseRepository]:
        return self._get_repository_class(repository_name)

    def _get_repository_class(self, repository_name: str) -> type[BaseRepository]:
        repository_class = self.repository_classes.get(repository_name)
        if repository_class:
            return repository_class()
        raise ValueError(f"Repository '{repository_name}' not found in {self.__class__.__name__}")


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
