from marshmallow import ValidationError

from app.helpers.sqlalchemy_query_builder import EQUAL_OP, GREATER_THAN_OP
from app.serializers import SearchSerializer
from tests.base.base_test import TestBase


class TestSearchSerializer(TestBase):
    def setUp(self):
        super().setUp()
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
        self.assertEqual(result, valid_data)

    def test_invalid_operator(self):
        invalid_data = {
            'search': [{'field_name': 'name', 'field_operator': 'invalid_op', 'field_value': 'test'}],
        }

        with self.assertRaises(ValidationError) as context:
            self.serializer.load(invalid_data)

        self.assertDictEqual(
            {
                'search': {
                    0: {
                        'field_operator': [
                            'Must be one of: between, contains, endswith, eq, gt, gte, in, lt, lte, ncontains, ne, nin, startswith.'
                        ]
                    }
                }
            },
            context.exception.messages,
        )

    def test_invalid_sorting(self):
        invalid_data = {
            'order': [{'field_name': 'name', 'sorting': 'wrong'}],
        }

        with self.assertRaises(ValidationError) as context:
            self.serializer.load(invalid_data)

        self.assertDictEqual({'order': {0: {'sorting': ['Must be one of: asc, desc.']}}}, context.exception.messages)

    def test_negative_pagination(self):
        invalid_data = {
            'items_per_page': -1,
            'page_number': -2,
        }

        with self.assertRaises(ValidationError) as context:
            self.serializer.load(invalid_data)

        self.assertDictEqual(
            {
                'items_per_page': ['Must be greater than or equal to 1.'],
                'page_number': ['Must be greater than or equal to 1.'],
            },
            context.exception.messages,
        )

    def test_missing_fields(self):
        with self.assertRaises(ValidationError):
            self.serializer.load({'order': [{'field_name': 'name'}]})

        with self.assertRaises(ValidationError):
            self.serializer.load({'search': [{'field_operator': EQUAL_OP, 'field_value': 'test'}]})
