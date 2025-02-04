"""Module for creating a Peewee filter query via dynamic way.

Next module is used for creating a Peewee query based on request fields.

References
----------
Query operators
http://docs.peewee-orm.com/en/latest/peewee/query_operators.html

"""
import operator
from functools import reduce
from typing import Type

import peewee
from peewee import CharField
from peewee import Field
from peewee import FixedCharField
from peewee import Model
from peewee import ModelSelect
from peewee import TextField
from peewee import UUIDField

from app.utils.constants import QUERY_OPERATORS
from app.utils.constants import REQUEST_QUERY_DELIMITER
from app.utils.constants import STRING_QUERY_OPERATORS


class Helper:
    @staticmethod
    def build_order_by(db_model: Type[Model], request_data: dict) -> list:
        """Build sorting fields with zero or more Column-like objects to
        order by.

        Example
        -------
        Peewee query: User.select().order_by(User.created_at.asc())

        Request fields:
        >>> from app.models.user import User
        >>> db_model = User
        >>> request_data = {'order': [{'sorting': 'asc', 'field_name': 'created_at'}]}  # noqa
        >>> Helper.build_order_by(db_model, request_data)
        [<peewee.Ordering object at ...>]

        Notes
        -----
        Actually is not posible to order across joins.

        References
        ----------
        http://docs.peewee-orm.com/en/latest/peewee/querying.html#sorting-records
        http://docs.peewee-orm.com/en/latest/peewee/api.html#Query.order_by

        """

        def build_ordering(field_name, sorting) -> peewee.Ordering:
            field = getattr(db_model, field_name)
            return getattr(field, sorting)()

        order_by_values = []
        request_order = request_data.get('order', [{'field_name': 'id', 'sorting': 'asc'}])

        if isinstance(request_order, list):
            order_by_values = [
                build_ordering(item.get('field_name'), item.get('sorting'))
                for item in request_order
            ]
        return order_by_values

    def build_string_clause(self, field: Field, field_operator: str, field_value) -> tuple:
        """Build string clauses.

        You can find next string operators:
        +------------+-----------------------------------------+
        | Name       | Description                             |
        +============+=========================================+
        | eq         | x equals y                              |
        +------------+-----------------------------------------+
        | ne         | x is not equal to y                     |
        +------------+-----------------------------------------+
        | contains   | Wild-card search for substring          |
        +------------+-----------------------------------------+
        | ncontains  | Wild-card not search for substring      |
        +------------+-----------------------------------------+
        | startswith | Search for values beginning with prefix |
        +------------+-----------------------------------------+
        | endswith   | Search for values ending with suffix    |
        +------------+-----------------------------------------+

        Example
        -------
        TODO: Pending to define

        """
        sql_clause = ()

        if field_value.find(REQUEST_QUERY_DELIMITER) != -1:
            field_value = field_value.split(REQUEST_QUERY_DELIMITER)
            sql_clauses = []

            for item in field_value:
                sql_clauses.append(self.build_string_clause(field, field_operator, item))
            sql_clause = reduce(operator.or_, sql_clauses)
        elif field_operator in STRING_QUERY_OPERATORS:
            if field_operator == 'eq':
                sql_clause = field == field_value
            elif field_operator == 'ne':
                sql_clause = ~(field == field_value)
            elif field_operator == 'contains':
                sql_clause = field.contains(field_value)
            elif field_operator == 'ncontains':
                sql_clause = ~(field.contains(field_value))
            elif field_operator == 'startswith':
                sql_clause = field.startswith(field_value)
            elif field_operator == 'endswith':
                sql_clause = field.endswith(field_value)

        return sql_clause

    def build_clause_operators(self, field: Field, field_operator: str, field_value) -> tuple:
        sql_clause = ()

        if isinstance(field_value, str) and field_value.find(REQUEST_QUERY_DELIMITER) != -1:
            field_value = field_value.split(REQUEST_QUERY_DELIMITER)
            sql_clauses = []

            for item in field_value:
                sql_clauses.append(self.build_clause_operators(field, field_operator, item))

            sql_clause = reduce(operator.or_, sql_clauses)
        elif field_operator in QUERY_OPERATORS:
            if field_operator == 'eq':
                sql_clause = field == field_value
            elif field_operator == 'ne':
                sql_clause = field != field_value
            elif field_operator == 'lt':
                sql_clause = field < field_value
            elif field_operator == 'lte':
                sql_clause = field <= field_value
            elif field_operator == 'gt':
                sql_clause = field > field_value
            elif field_operator == 'gte':
                sql_clause = field >= field_value
            elif field_operator == 'in':
                sql_clause = field.in_(field_value.split(REQUEST_QUERY_DELIMITER))
            elif field_operator == 'nin':
                sql_clause = field.not_in(field_value)
            elif field_operator == 'between':
                values = field_value.split(REQUEST_QUERY_DELIMITER)
                sql_clause = field.between(lo=values[0], hi=values[1])
        return sql_clause

    def build_sql_expression(self, field: Field, field_operator: str, field_value):
        if isinstance(field, (CharField, FixedCharField, TextField, UUIDField)):
            sql_clause = self.build_string_clause(field, field_operator, field_value)
        else:
            sql_clause = self.build_clause_operators(field, field_operator, field_value)
        return sql_clause


class RequestQueryOperator:
    @staticmethod
    def create_search_query(
        db_model: Type[Model], query: ModelSelect, data: dict = None
    ) -> ModelSelect:
        if data is None:
            data = {}

        filters = data.get('search', {})
        sql_expressions = []
        helper = Helper()

        for filter in filters:
            field = getattr(db_model, filter['field_name'])
            field_value = filter['field_value']

            if isinstance(field_value, str) and not field_value.strip():
                continue

            sql_expression = helper.build_sql_expression(
                field, filter['field_operator'], field_value
            )
            sql_expressions.append(sql_expression)

        if sql_expressions:
            query = query.where(*sql_expressions)

        return query

    @staticmethod
    def get_request_query_fields(db_model: Type[Model], request_data=None) -> tuple:
        request_data = request_data or {}

        # Page numbers are 1-based, so the first page of results
        # will be page 1.
        # http://docs.peewee-orm.com/en/latest/peewee/querying.html#paginating-records
        page_number = int(request_data.get('page_number', 1))
        items_per_page = int(request_data.get('items_per_page', 10))
        order_by = Helper.build_order_by(db_model, request_data)
        return page_number, items_per_page, order_by
