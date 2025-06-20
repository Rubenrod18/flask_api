import pytest
from marshmallow import ValidationError

from app.helpers.sqlalchemy_query_builder import EQUAL_OP, GREATER_THAN_OP
from app.repositories.base import BaseRepository
from app.serializers import SearchSerializer
from app.serializers.core import RepositoryMixin


class DummyRepository:
    pass


class SampleRepository(BaseRepository):
    def __init__(self):
        super().__init__(model={})


class TestRepositoryMixin:
    @pytest.mark.parametrize(
        'repository_classes_value, expected_error',
        [
            ({'sample': {}}, "repository_classes['sample'] must be a class"),
            ({'sample': DummyRepository}, "repository_classes['sample'] must inherit from BaseRepository"),
        ],
        ids=['dict', 'not-repository-class'],
    )
    def test_repository_classes_invalid_raises_type_error(self, repository_classes_value, expected_error):
        with pytest.raises(TypeError) as exc_info:

            class TestSerializer(RepositoryMixin):  # pylint: disable=unused-variable
                repository_classes = repository_classes_value

        assert expected_error in str(exc_info.value)

    def test_repository_classes_valid_does_not_raise(self):
        class TestSerializer(RepositoryMixin):
            repository_classes = {'sample': SampleRepository}

        assert issubclass(TestSerializer, RepositoryMixin)

    def test_repository_classes_valid(self):
        class TestSerializer(RepositoryMixin):
            repository_classes = {'sample': SampleRepository}

        assert issubclass(TestSerializer, RepositoryMixin)

    def test_get_repository_raises_value_error_for_unknown_name(self):
        class TestSerializer(RepositoryMixin):
            repository_classes = {'valid': SampleRepository}

        resource = TestSerializer()

        with pytest.raises(ValueError) as exc_info:
            resource.get_repository('invalid')

        assert "Repository 'invalid' not found" in str(exc_info.value)

    def test_get_repository_returns_instance(self):
        class TestSerializer(RepositoryMixin):
            repository_classes = {'sample': SampleRepository}

        resource = TestSerializer()
        repository = resource.get_repository('sample')

        assert isinstance(repository, SampleRepository)


# pylint: disable=attribute-defined-outside-init
class TestSearchSerializer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.serializer = SearchSerializer()

    def test_valid_search(self):
        valid_data = {
            'search': [
                {'field_name': 'name', 'field_operator': EQUAL_OP, 'field_value': 'test'},
                {'field_name': 'age', 'field_operator': GREATER_THAN_OP, 'field_value': 18},
            ],
            'order': [{'field_name': 'name', 'sorting': 'asc'}],
            'items_per_page': 10,
            'page_number': 1,
        }

        result = self.serializer.load(valid_data)
        assert result == valid_data

    def test_invalid_operator(self):
        invalid_data = {
            'search': [{'field_name': 'name', 'field_operator': 'invalid_op', 'field_value': 'test'}],
        }

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load(invalid_data)

        assert {
            'search': {
                0: {
                    'field_operator': [
                        (
                            'Must be one of: '
                            'between, contains, endswith, eq, gt, gte, in, lt, lte, ncontains, ne, nin, startswith.'
                        )
                    ]
                }
            }
        } == exc_info.value.messages

    def test_invalid_sorting(self):
        invalid_data = {
            'order': [{'field_name': 'name', 'sorting': 'wrong'}],
        }

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load(invalid_data)

        assert {'order': {0: {'sorting': ['Must be one of: asc, desc.']}}} == exc_info.value.messages

    def test_negative_pagination(self):
        invalid_data = {
            'items_per_page': -1,
            'page_number': -2,
        }

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load(invalid_data)

        assert {
            'items_per_page': ['Must be greater than or equal to 1.'],
            'page_number': ['Must be greater than or equal to 1.'],
        } == exc_info.value.messages

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            self.serializer.load({'order': [{'field_name': 'name'}]})

        with pytest.raises(ValidationError):
            self.serializer.load({'search': [{'field_operator': EQUAL_OP, 'field_value': 'test'}]})
