import pytest

from app.blueprints.base import SerializerMixin
from app.extensions import ma


class DummySerializer:
    pass


class SchemaSerializer(ma.Schema):
    pass


class TestSerializerMixin:
    @pytest.mark.parametrize(
        'serializer_class_value, expected_error',
        [
            ({}, 'serializer_class must be a class'),
            (DummySerializer, 'serializer_class must inherit from marshmallow.Schema'),
        ],
        ids=['dict', 'not-serializer-class'],
    )
    def test_serializer_class_invalid_raises_type_error(self, serializer_class_value, expected_error):
        with pytest.raises(TypeError) as exc_info:

            class TestResource(SerializerMixin):  # pylint: disable=unused-variable
                serializer_class = serializer_class_value

        assert expected_error in str(exc_info.value)

    def test_serializer_class_valid_does_not_raise(self):
        class TestResource(SerializerMixin):
            serializer_class = SchemaSerializer

        assert issubclass(TestResource, SerializerMixin)

    @pytest.mark.parametrize(
        'serializer_classes_value, expected_error',
        [
            ({'schema': {}}, "serializer_classes['schema'] must be a class"),
            ({'schema': DummySerializer}, "serializer_classes['schema'] must inherit from marshmallow.Schema"),
        ],
        ids=['dict', 'not-serializer-class'],
    )
    def test_serializer_classes_invalid_raises_type_error(self, serializer_classes_value, expected_error):
        with pytest.raises(TypeError) as exc_info:

            class TestResource(SerializerMixin):  # pylint: disable=unused-variable
                serializer_classes = serializer_classes_value

        assert expected_error in str(exc_info.value)

    def test_serializer_classes_valid_does_not_raise(self):
        class TestResource(SerializerMixin):
            serializer_classes = {'schema': SchemaSerializer}

        assert issubclass(TestResource, SerializerMixin)

    def test_serializer_class_and_classes_valid(self):
        class TestResource(SerializerMixin):
            serializer_class = SchemaSerializer
            serializer_classes = {'schema': SchemaSerializer}

        assert issubclass(TestResource, SerializerMixin)

    def test_get_serializer_class_returns_expected_class(self):
        class TestResource(SerializerMixin):
            serializer_class = SchemaSerializer
            serializer_classes = {'schema': SchemaSerializer}

        resource = TestResource()

        assert resource.get_serializer_class() == SchemaSerializer
        assert resource.get_serializer_class('schema') == SchemaSerializer

    def test_get_serializer_raises_value_error_for_unknown_name(self):
        class TestResource(SerializerMixin):
            serializer_classes = {'valid': SchemaSerializer}

        resource = TestResource()

        with pytest.raises(ValueError) as exc_info:
            resource.get_serializer(serializer_name='invalid')

        assert "Serializer 'invalid' not found" in str(exc_info.value)

    def test_get_serializer_returns_instance(self):
        class TestResource(SerializerMixin):
            serializer_classes = {'schema': SchemaSerializer}

        resource = TestResource()
        serializer = resource.get_serializer(serializer_name='schema')

        assert isinstance(serializer, SchemaSerializer)
