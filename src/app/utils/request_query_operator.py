"""Module for creating a SQLAlchemy filter query via dynamic way.

Next module is used for creating a SQLAlchemy query based on request fields.

Notes
-----
    REQUEST_QUERY_DELIMITER is used for converting requests field
    values to a list, for example:
        Request send these values:
            field_operator: contains
            field_values: valueA;valueB;valueC

        The delimiter operator splits values to a list of values:
            field_values: [valueA, valueB, valueC]

References
----------
Query operators: https://docs.sqlalchemy.org/en/20/core/operators.html
Comparison Operators: https://docs.sqlalchemy.org/en/20/core/operators.html#comparison-operators

"""

from typing import Type

import sqlalchemy as sa
from flask_sqlalchemy.query import Query as FlaskQuery

from app.extensions import db

REQUEST_QUERY_DELIMITER = ';'

# General operators
EQUAL_OP = 'eq'
NOT_EQUAL_OP = 'ne'

# Strings query operators
CONTAINS_OP = 'contains'
NOT_CONTAINS_OP = 'ncontains'
STARTS_WITH_OP = 'startswith'
ENDS_WITH_OP = 'endswith'

STRING_QUERY_OPERATORS = [
    EQUAL_OP,
    NOT_EQUAL_OP,
    CONTAINS_OP,
    NOT_CONTAINS_OP,
    STARTS_WITH_OP,
    ENDS_WITH_OP,
]

# No-String query operators
LESS_THAN_OP = 'lt'
LESS_THAN_OR_EQUAL_TO_OP = 'lte'
GREATER_THAN_OP = 'gt'
GREATER_THAN_OR_EQUAL_TO_OP = 'gte'
IN_OP = 'in'
NOT_IN_OP = 'nin'
BETWEEN_OP = 'between'

QUERY_OPERATORS = [
    EQUAL_OP,
    NOT_EQUAL_OP,
    LESS_THAN_OP,
    LESS_THAN_OR_EQUAL_TO_OP,
    GREATER_THAN_OP,
    GREATER_THAN_OR_EQUAL_TO_OP,
    IN_OP,
    NOT_IN_OP,
    BETWEEN_OP,
]


class OrderingHelper:
    @staticmethod
    def build_order_by(db_model: Type[db.Model], request_data: dict) -> list[sa.UnaryExpression]:
        """Build sorting fields with zero or more Column-like objects to
        order by.

        Example
        -------
        SQLAlchemy query: db.session.query(User).order_by(User.created_at.desc())

        Request fields:
        >>> from app.models.user import User
        >>> db_model = User
        >>> request_data = {'order': [{'sorting': 'asc', 'field_name': 'created_at'}]}  # noqa
        >>> OrderingHelper.build_order_by(db_model, request_data)
        <flask_sqlalchemy.query.Query object at 0x7f9edf6954f0>

        References
        ----------
        https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.order_by

        """
        order_by_values = []
        request_order = request_data.get('order', [{'field_name': 'id', 'sorting': 'asc'}])

        for item in request_order:
            field_name = item.get('field_name')
            sorting = item.get('sorting', 'asc')

            field = getattr(db_model, field_name, None)
            if field is not None:
                if sorting == 'desc':
                    order_by_values.append(field.desc())
                else:
                    order_by_values.append(field.asc())

        return order_by_values


class StringClauseHelper:
    def __init__(self):
        self.operator_map = {
            'eq': self._eq,
            'ne': self._ne,
            'contains': self._contains,
            'ncontains': self._ncontains,
            'startswith': self._startswith,
            'endswith': self._endswith,
        }

    @staticmethod
    def _eq(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field == field_value

    @staticmethod
    def _ne(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field != field_value

    @staticmethod
    def _contains(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field.like(f'%{field_value}%')

    @staticmethod
    def _ncontains(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return ~field.like(f'%{field_value}%')

    @staticmethod
    def _startswith(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field.like(f'{field_value}%')

    @staticmethod
    def _endswith(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field.like(f'%{field_value}')

    def build_clause(
        self, field: sa.orm.InstrumentedAttribute, field_operator: str, field_value: str
    ) -> sa.BinaryExpression:
        if field_operator not in self.operator_map:
            raise ValueError(f'Unsupported operator: {field_operator}')

        return self.operator_map[field_operator](field, field_value)

    def build_clause_with_multiple_values(
        self, field: sa.orm.InstrumentedAttribute, field_operator: str, field_value: str
    ) -> sa.BinaryExpression:
        if REQUEST_QUERY_DELIMITER in field_value:
            values = field_value.split(REQUEST_QUERY_DELIMITER)
            sql_clause = sa.or_(*(self.build_clause(field, field_operator, value) for value in values))
        else:
            sql_clause = self.build_clause(field, field_operator, field_value)

        return sql_clause


class OperatorClauseHelper:
    def __init__(self):
        self.operator_map = {
            'eq': self._eq,
            'ne': self._ne,
            'lt': self._lt,
            'lte': self._lte,
            'gt': self._gt,
            'gte': self._gte,
            'in': self._in,
            'nin': self._nin,
            'between': self._between,
        }

    @staticmethod
    def _eq(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field == field_value

    @staticmethod
    def _ne(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field != field_value

    @staticmethod
    def _lt(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field < field_value

    @staticmethod
    def _lte(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field <= field_value

    @staticmethod
    def _gt(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field > field_value

    @staticmethod
    def _gte(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field >= field_value

    @staticmethod
    def _in(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return field.in_(field_value.split(REQUEST_QUERY_DELIMITER))

    @staticmethod
    def _nin(field: sa.orm.InstrumentedAttribute, field_value: str) -> sa.BinaryExpression:
        return ~field.in_(field_value.split(REQUEST_QUERY_DELIMITER))

    @staticmethod
    def _between(field: sa.orm.InstrumentedAttribute, field_value: any) -> sa.BinaryExpression:
        values = field_value.split(REQUEST_QUERY_DELIMITER)
        return field.between(values[0], values[1])

    def build_clause(
        self, field: sa.orm.InstrumentedAttribute, field_operator: str, field_value: any
    ) -> sa.BinaryExpression:
        if field_operator not in self.operator_map:
            raise ValueError(f'Unsupported operator: {field_operator}')

        return self.operator_map[field_operator](field, field_value)

    def build_clause_with_multiple_values(
        self, field: sa.orm.InstrumentedAttribute, field_operator: str, field_value: any
    ) -> sa.BinaryExpression:
        if (
            isinstance(field_value, str)
            and REQUEST_QUERY_DELIMITER in field_value
            and field_operator not in [BETWEEN_OP, IN_OP, NOT_IN_OP]
        ):
            values = field_value.split(REQUEST_QUERY_DELIMITER)
            sql_clause = sa.or_(*(self.build_clause(field, field_operator, value) for value in values))
        else:
            sql_clause = self.build_clause(field, field_operator, field_value)

        return sql_clause


class QueryHelper:
    def __init__(self):
        self.string_clause_helper = StringClauseHelper()
        self.operator_clause_helper = OperatorClauseHelper()

    def build_sql_expression(
        self, field: sa.orm.InstrumentedAttribute, field_operator: str, field_value: any
    ) -> sa.sql.expression.ClauseElement:
        if isinstance(field.type, (sa.String, sa.Text, sa.UUID)):
            sql_clause = self.string_clause_helper.build_clause_with_multiple_values(field, field_operator, field_value)
        else:
            sql_clause = self.operator_clause_helper.build_clause_with_multiple_values(
                field, field_operator, field_value
            )

        return sql_clause


class RequestQueryOperator:
    def __init__(self, query_helper: QueryHelper = None, ordering_helper: OrderingHelper = None):
        self.query_helper = query_helper or QueryHelper()
        self.ordering_helper = ordering_helper or OrderingHelper()

    def create_search_query(self, db_model: Type[db.Model], query: FlaskQuery, data: dict = None) -> FlaskQuery:
        if data is None:
            data = {}

        search_criteria = data.get('search', {})
        sql_expressions = []

        for criteria in search_criteria:
            field_name = criteria.get('field_name')
            field = getattr(db_model, field_name, None)

            if field is None:
                raise ValueError(f'Invalid field name: {field_name}')

            field_value = criteria['field_value']

            if isinstance(field_value, str) and not field_value.strip():
                continue

            sql_expression = self.query_helper.build_sql_expression(field, criteria['field_operator'], field_value)
            sql_expressions.append(sql_expression)

        if sql_expressions:
            query = query.where(*sql_expressions)

        return query

    def get_request_query_fields(
        self, db_model: Type[db.Model], request_data=None
    ) -> tuple[int, int, list[sa.UnaryExpression]]:
        request_data = request_data or {}
        page_number = int(request_data.get('page_number', 1)) - 1
        items_per_page = int(request_data.get('items_per_page', 10))

        order_by = self.ordering_helper.build_order_by(db_model, request_data)

        return page_number, items_per_page, order_by
