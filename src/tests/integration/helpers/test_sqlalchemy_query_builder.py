# pylint: disable=attribute-defined-outside-init, unused-argument
from datetime import datetime, UTC

import pytest
import sqlalchemy as sa
from freezegun import freeze_time
from sqlalchemy.orm import Query

import app.helpers.sqlalchemy_query_builder as rqo
from app.database.factories.document_factory import LocalDocumentFactory
from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.extensions import db
from app.models import Document, Role, User


class _TestBaseCreateSearchQuery:
    @staticmethod
    def _search_request(
        field_name: str | list[str],
        field_op: str | list[str],
        field_value: str | list[str],
    ):
        if isinstance(field_name, list) and isinstance(field_op, list) and isinstance(field_value, list):
            search_value = [
                {'field_name': field_name[i], 'field_operator': field_op[i], 'field_value': field_value[i]}
                for i in range(len(field_name))
            ]
        else:
            search_value = [{'field_name': field_name, 'field_operator': field_op, 'field_value': field_value}]

        return {'search': search_value}

    @staticmethod
    def _get_values(query: Query) -> set[int]:
        return {item[0] for item in query.all()}


class TestOrderByClauseBuilder:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        with freeze_time('2020-01-01'):
            self.doc = LocalDocumentFactory(name='Invoice 2024-01')

        with freeze_time('2015-01-01'):
            self.doc_2 = LocalDocumentFactory(name='Employee Contract John Doe')

    @pytest.mark.parametrize(
        'sorting, field_name, expected_name',
        [
            ('asc', 'name', 'Employee Contract John Doe'),
            ('desc', 'name', 'Invoice 2024-01'),
        ],
        ids=['sort ascending', 'sort descending'],
    )
    def test_ordering_asc_and_desc(self, sorting, field_name, expected_name):
        order = rqo.OrderByClauseBuilder.build_order_by(
            Document, request_data={'order': [{'sorting': sorting, 'field_name': field_name}]}
        )
        query = db.session.query(Document).order_by(*order)

        assert query.first().name == expected_name

    @pytest.mark.parametrize(
        'sorting, expected_name',
        [
            (
                [{'sorting': 'asc', 'field_name': 'name'}, {'sorting': 'desc', 'field_name': 'created_at'}],
                'Employee Contract John Doe',
            ),
            (
                [{'sorting': 'desc', 'field_name': 'name'}, {'sorting': 'asc', 'field_name': 'created_at'}],
                'Invoice 2024-01',
            ),
        ],
        ids=['sort asc/desc', 'sort desc/asc'],
    )
    def test_ordering_with_more_than_one_criteria(self, sorting, expected_name):
        order = rqo.OrderByClauseBuilder.build_order_by(Document, request_data={'order': sorting})
        query = db.session.query(Document).order_by(*order)

        assert query.first().name == expected_name


class TestStringQueryClauseBuilder:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.string_clause_helper = rqo.StringQueryClauseBuilder()

    @pytest.mark.parametrize(
        'description, test_case_builder, expected_clause_builder, expected_clauses',
        [
            (
                'equals',
                lambda u1, *_: (User.name, rqo.EQUAL_OP, u1.name),
                lambda u1, *_: User.name == u1.name,
                None,
            ),
            (
                'not equals',
                lambda _, u2, __: (User.name, rqo.NOT_EQUAL_OP, u2.name),
                lambda _, u2, __: User.name != u2.name,
                None,
            ),
            (
                'contains',
                lambda _, __, u3: (User.name, rqo.CONTAINS_OP, u3.name),
                lambda _, __, u3: User.name.like(f'%{u3.name}%'),
                None,
            ),
            (
                'not contains',
                lambda _, __, u3: (User.name, rqo.NOT_CONTAINS_OP, u3.name),
                lambda _, __, u3: ~User.name.like(f'%{u3.name}%'),
                None,
            ),
            (
                'starts with',
                lambda _, u2, __: (User.name, rqo.STARTS_WITH_OP, u2.name),
                lambda _, u2, __: User.name.like(f'{u2.name}%'),
                None,
            ),
            (
                'ends with',
                lambda _, u2, __: (User.name, rqo.ENDS_WITH_OP, u2.name),
                lambda _, u2, __: User.name.like(f'%{u2.name}'),
                None,
            ),
            (
                'multiple values',
                lambda _, u2, u3: (User.name, rqo.ENDS_WITH_OP, f'{u2.name}{rqo.REQUEST_QUERY_DELIMITER}{u3.name}'),
                lambda _, u2, u3: sa.or_(User.name.like(f'%{u2.name}'), User.name.like(f'%{u3.name}')),
                lambda _, u2, u3: (f'%{u2.name}', f'%{u3.name}'),
            ),
        ],
        ids=['eq', 'ne', 'contains', 'not_contains', 'starts_with', 'ends_with', 'multiple_values'],
    )
    def test_create_search_query_str(self, description, test_case_builder, expected_clause_builder, expected_clauses):
        user = UserFactory(name='Alice', last_name='Johnson')
        user_2 = UserFactory(name='John', last_name='Smith')
        user_3 = UserFactory(name='Michael', last_name='Williams')

        field, operator, value = test_case_builder(user, user_2, user_3)
        expected = expected_clause_builder(user, user_2, user_3)

        clause = self.string_clause_helper.build_clause_with_multiple_values(field, operator, value)

        assert clause.operator == expected.operator, f'Operator mismatch for: {description}'

        if description == 'multiple values':
            expected_values = expected_clauses(user, user_2, user_3)
            for i, subclause in enumerate(clause.clauses):
                assert subclause.right.value == expected_values[i], f'{description} value mismatch'
        else:
            assert clause.right.value == expected.right.value, f'{description} value mismatch'


class TestComparisonClauseBuilder:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.operator_clause_helper = rqo.ComparisonClauseBuilder()

    @pytest.mark.parametrize(
        'description, test_case_builder, expected_clause_builder, expected_clauses',
        [
            (
                'equal',
                lambda doc, *_: (Document.created_at, rqo.EQUAL_OP, doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                lambda doc, *_: (Document.created_at == doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'not equal',
                lambda doc, *_: (
                    Document.created_at,
                    rqo.NOT_EQUAL_OP,
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
                lambda doc, *_: (Document.created_at != doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'less than',
                lambda doc, *_: (
                    Document.created_at,
                    rqo.LESS_THAN_OP,
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
                lambda doc, *_: (Document.created_at < doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'less than or equal',
                lambda doc, *_: (
                    Document.created_at,
                    rqo.LESS_THAN_OR_EQUAL_TO_OP,
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
                lambda doc, *_: (Document.created_at <= doc.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'great than',
                lambda _, __, doc_3: (
                    Document.created_at,
                    rqo.GREATER_THAN_OP,
                    doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
                lambda _, __, doc_3: (Document.created_at > doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'great than or equal',
                lambda _, __, doc_3: (
                    Document.created_at,
                    rqo.GREATER_THAN_OR_EQUAL_TO_OP,
                    doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
                lambda _, __, doc_3: (Document.created_at >= doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S')),
                None,
            ),
            (
                'between',
                lambda _, doc_2, doc_3: (
                    Document.created_at,
                    rqo.BETWEEN_OP,
                    (
                        f'{doc_2.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
                        f'{doc_3.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    ),
                ),
                lambda _, doc_2, doc_3: Document.created_at.between(doc_2.created_at, doc_3.created_at),
                lambda _, doc_2, doc_3: (
                    doc_2.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
            ),
            (
                'multiple values',
                lambda doc, _, doc_3: (
                    Document.created_at,
                    rqo.GREATER_THAN_OP,
                    f'{doc_3.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    f'{rqo.REQUEST_QUERY_DELIMITER}'
                    f'{doc.created_at.strftime("%Y-%m-%d %H:%M:%S")}',
                ),
                lambda doc, _, doc_3: (
                    sa.or_(
                        *(
                            Document.created_at > doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            Document.created_at > doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        )
                    )
                ),
                lambda doc, _, doc_3: (
                    doc_3.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ),
            ),
        ],
        ids=[
            'equal',
            'not equal',
            'less than',
            'less than or equal to',
            'greater than',
            'greater than or equal to',
            'between',
            'multiple values',
        ],
    )
    def test_create_search_query_datetime(
        self, description, test_case_builder, expected_clause_builder, expected_clauses
    ):
        with freeze_time('2020-01-01'):
            doc = LocalDocumentFactory(name='Invoice 2024-01', created_at=datetime.now(UTC))

        with freeze_time('2015-01-01'):
            doc_2 = LocalDocumentFactory(name='Employee Contract John Doe', created_at=datetime.now(UTC))

        with freeze_time('2010-01-01'):
            doc_3 = LocalDocumentFactory(name='Monthly Sales Report March', created_at=datetime.now(UTC))

        field, operator, value = test_case_builder(doc, doc_2, doc_3)
        expected = expected_clause_builder(doc, doc_2, doc_3)

        clause = self.operator_clause_helper.build_clause_with_multiple_values(field, operator, value)
        assert clause.operator == expected.operator, f'Operator mismatch for: {description}'

        if description == 'multiple values':
            expected_values = expected_clauses(doc, doc_2, doc_3)
            for index, _ in enumerate(clause.clauses):
                assert clause.clauses[index].right.value == expected_values[index], description
        elif description == 'between':
            expected_values = expected_clauses(doc, doc_2, doc_3)
            for index, _ in enumerate(clause.right.clauses):
                assert clause.right.clauses[index].value == expected_values[index], description
        else:
            assert clause.right.value == expected.right.value, description

    @pytest.mark.parametrize(
        'description, test_case_builder, expected_clause_builder, expected_clauses',
        [
            (
                'equals',
                lambda doc, *_: (Document.size, rqo.EQUAL_OP, doc.size),
                lambda doc, *_: (Document.size == doc.size),
                None,
            ),
            (
                'not equals',
                lambda doc, *_: (Document.size, rqo.NOT_EQUAL_OP, doc.size),
                lambda doc, *_: (Document.size != doc.size),
                None,
            ),
            (
                'less than',
                lambda _, doc_2, __: (Document.size, rqo.LESS_THAN_OP, doc_2.size),
                lambda _, doc_2, __: (Document.size < doc_2.size),
                None,
            ),
            (
                'less than or equal',
                lambda _, doc_2, __: (Document.size, rqo.LESS_THAN_OR_EQUAL_TO_OP, doc_2.size),
                lambda _, doc_2, __: (Document.size <= doc_2.size),
                None,
            ),
            (
                'great than',
                lambda _, doc_2, __: (Document.size, rqo.GREATER_THAN_OP, doc_2.size),
                lambda _, doc_2, __: (Document.size > doc_2.size),
                None,
            ),
            (
                'great than or equal',
                lambda _, doc_2, __: (Document.size, rqo.GREATER_THAN_OR_EQUAL_TO_OP, doc_2.size),
                lambda _, doc_2, __: (Document.size >= doc_2.size),
                None,
            ),
            (
                'in',
                lambda doc, doc_2, doc_3: (
                    Document.size,
                    rqo.IN_OP,
                    f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                lambda doc, doc_2, doc_3: (Document.size.in_([f'{doc_3.size}', f'{doc_2.size}', f'{doc.size}'])),
                None,
            ),
            (
                'not in',
                lambda doc, doc_2, doc_3: (
                    Document.size,
                    rqo.NOT_IN_OP,
                    f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc_2.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                lambda doc, doc_2, doc_3: (~Document.size.in_([f'{doc_3.size}', f'{doc_2.size}', f'{doc.size}'])),
                None,
            ),
            (
                'multiple values',
                lambda doc, _, doc_3: (
                    Document.size,
                    rqo.GREATER_THAN_OP,
                    f'{doc_3.size}{rqo.REQUEST_QUERY_DELIMITER}{doc.size}',
                ),
                lambda doc, _, doc_3: (sa.or_(*(Document.size > doc_3.size, Document.size > doc.size))),
                lambda doc, _, doc_3: (f'{doc_3.size}', f'{doc.size}'),
            ),
        ],
        ids=[
            'equals',
            'not equals',
            'less than',
            'less than or equal to',
            'greater than',
            'greater than or equal to',
            'in',
            'not in',
            'multiple values',
        ],
    )
    def test_create_search_query_integer(
        self, description, test_case_builder, expected_clause_builder, expected_clauses
    ):
        doc = LocalDocumentFactory(name='Invoice 2024-01', size=1_000_000)
        doc_2 = LocalDocumentFactory(name='Employee Contract John Doe', size=2_000_000)
        doc_3 = LocalDocumentFactory(name='Monthly Sales Report March', size=3_000_000)

        field, operator, value = test_case_builder(doc, doc_2, doc_3)
        expected = expected_clause_builder(doc, doc_2, doc_3)

        clause = self.operator_clause_helper.build_clause_with_multiple_values(field, operator, value)
        assert clause.operator == expected.operator, f'Operator mismatch for: {description}'

        if description == 'multiple values':
            expected_values = expected_clauses(doc, doc_2, doc_3)
            for index, _ in enumerate(clause.clauses):
                assert clause.clauses[index].right.value == expected_values[index], description
        elif description == 'between':
            expected_values = expected_clauses(doc, doc_2, doc_3)
            for index, _ in enumerate(clause.right.clauses):
                assert clause.right.clauses[index].value == expected_values[index], description
        else:
            assert clause.right.value == expected.right.value, description


class TestSQLAlchemyQueryBuilderStrings(_TestBaseCreateSearchQuery):
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.query_helper = rqo.QueryClauseBuilder()
        self.ordering_helper = rqo.OrderByClauseBuilder()
        self.rqo = rqo.SQLAlchemyQueryBuilder(self.query_helper, self.ordering_helper)

    @pytest.mark.parametrize(
        'description,request_data,get_expected_ids',
        [
            ('equals', lambda self: self._search_request('name', 'eq', 'Michael'), lambda self: {self.user_3.id}),
            (
                'not equals',
                lambda self: self._search_request('name', 'ne', 'Michael'),
                lambda self: {self.user.id, self.user_2.id},
            ),
            (
                'contains',
                lambda self: self._search_request('name', 'contains', 'e'),
                lambda self: {self.user.id, self.user_3.id},
            ),
            (
                'not contains',
                lambda self: self._search_request('last_name', 'ncontains', 'i'),
                lambda self: {self.user.id},
            ),
            (
                'starts with',
                lambda self: self._search_request('last_name', 'startswith', 'S'),
                lambda self: {self.user_2.id},
            ),
            (
                'ends with',
                lambda self: self._search_request('last_name', 'endswith', 'h'),
                lambda self: {self.user_2.id},
            ),
            (
                'multiple queries',
                lambda self: self._search_request(
                    field_name=['name', 'last_name'],
                    field_op=['contains', 'ncontains'],
                    field_value=['a', 'o'],
                ),
                lambda self: {self.user_3.id},
            ),
        ],
    )
    def test_create_search_query_str(self, description, request_data, get_expected_ids):
        self.user = UserFactory(name='Alice', last_name='Johnson')
        self.user_2 = UserFactory(name='John', last_name='Smith')
        self.user_3 = UserFactory(name='Michael', last_name='Williams')

        query = self.rqo.create_search_query(User, db.session.query(User.id), request_data(self))
        assert self._get_values(query) == get_expected_ids(self), description

    @pytest.mark.parametrize(
        'description, request_data, expected_ids',
        [
            (
                'equals',
                lambda self, desc: self._search_request('description', 'eq', desc),
                lambda self, role, *_: {role.id},
            ),
            (
                'not equals',
                lambda self, desc: self._search_request('description', 'ne', desc),
                lambda self, _, role_2, role_3: {role_2.id, role_3.id},
            ),
            (
                'contains',
                lambda self, _: self._search_request('description', 'contains', 'develops'),
                lambda self, role, role_2, __: {role.id, role_2.id},
            ),
            (
                'not contains',
                lambda self, _: self._search_request('description', 'ncontains', 'develops'),
                lambda self, _, __, role_3: {role_3.id},
            ),
            (
                'starts with',
                lambda self, _: self._search_request('description', 'startswith', 'D'),
                lambda self, role, role_2, __: {role.id, role_2.id},
            ),
            (
                'ends with',
                lambda self, _: self._search_request('description', 'endswith', '.'),
                lambda self, role, role_2, role_3: {role.id, role_2.id, role_3.id},
            ),
            (
                'multiple queries',
                lambda self, _: self._search_request(
                    field_name=['name', 'description'],
                    field_op=['contains', 'contains'],
                    field_value=['ing', 'develops'],
                ),
                lambda self, _, role_2, __: {role_2.id},
            ),
        ],
    )
    def test_create_search_query_text(self, description, request_data, expected_ids):
        software_engineer_description = 'Designs, develops, and maintains software applications.'
        role = RoleFactory(name='software_engineer', description=software_engineer_description)
        role_2 = RoleFactory(name='marketing_manager', description='Develops and implements marketing strategies.')
        role_3 = RoleFactory(
            name='hr_specialist',
            description='Manages recruitment, employee relations, performance, and ensures compliance with labor laws.',
        )

        query = self.rqo.create_search_query(
            Role,
            db.session.query(Role.id),
            request_data(self, software_engineer_description),
        )
        assert self._get_values(query) == expected_ids(self, role, role_2, role_3), description

    @pytest.mark.parametrize(
        'description, request_data, expected_ids',
        [
            (
                'equals',
                lambda self, user: self._search_request('fs_uniquifier', 'eq', user.fs_uniquifier),
                lambda self, user, user_2, user_3: {user.id},
            ),
            (
                'not equals',
                lambda self, user: self._search_request('fs_uniquifier', 'ne', user.fs_uniquifier),
                lambda self, _, user_2, user_3: {user_2.id, user_3.id},
            ),
        ],
    )
    def test_create_search_query_uuid(self, description, request_data, expected_ids):
        user = UserFactory()
        user_2 = UserFactory()
        user_3 = UserFactory()

        query = self.rqo.create_search_query(User, db.session.query(User.id), request_data(self, user))
        assert self._get_values(query) == expected_ids(self, user, user_2, user_3), description


class TestSQLAlchemyQueryBuilderNoStrings(_TestBaseCreateSearchQuery):
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.query_helper = rqo.QueryClauseBuilder()
        self.ordering_helper = rqo.OrderByClauseBuilder()
        self.rqo = rqo.SQLAlchemyQueryBuilder(self.query_helper, self.ordering_helper)

    @pytest.mark.parametrize(
        'description, request_builder, expected_ids_fn',
        [
            (
                'equals',
                lambda self, u, *_: self._search_request('birth_date', 'eq', u.birth_date.strftime('%Y-%m-%d')),
                lambda self, u, *_: {u.id},
            ),
            (
                'not equals',
                lambda self, u, *_: self._search_request('birth_date', 'ne', u.birth_date.strftime('%Y-%m-%d')),
                lambda self, _, u2, u3: {u2.id, u3.id},
            ),
            (
                'less than',
                lambda self, u, *_: self._search_request('birth_date', 'lt', u.birth_date.strftime('%Y-%m-%d')),
                lambda self, _, u2, u3: {u2.id, u3.id},
            ),
            (
                'less than equals',
                lambda self, u, *_: self._search_request('birth_date', 'lte', u.birth_date.strftime('%Y-%m-%d')),
                lambda self, u, u2, u3: {u.id, u2.id, u3.id},
            ),
            (
                'great than',
                lambda self, _, __, u3: self._search_request('birth_date', 'gt', u3.birth_date.strftime('%Y-%m-%d')),
                lambda self, u, u2, _: {u.id, u2.id},
            ),
            (
                'great than equals',
                lambda self, _, __, u3: self._search_request('birth_date', 'gte', u3.birth_date.strftime('%Y-%m-%d')),
                lambda self, u, u2, u3: {u.id, u2.id, u3.id},
            ),
            (
                'between',
                lambda self, _, u2, u3: self._search_request(
                    'birth_date',
                    'between',
                    (
                        f'{u3.birth_date.strftime("%Y-%m-%d")}'
                        f'{rqo.REQUEST_QUERY_DELIMITER}'
                        f'{u2.birth_date.strftime("%Y-%m-%d")}'
                    ),
                ),
                lambda self, _, u2, u3: {u2.id, u3.id},
            ),
            (
                'multiple queries',
                lambda self, u, _, u3: self._search_request(
                    ['birth_date', 'birth_date'],
                    ['gt', 'gte'],
                    [u3.birth_date.strftime('%Y-%m-%d'), u.birth_date.strftime('%Y-%m-%d')],
                ),
                lambda self, u, *_: {u.id},
            ),
        ],
    )
    def test_create_search_query_date(self, description, request_builder, expected_ids_fn):
        with freeze_time('2020-01-01'):
            user = UserFactory(birth_date=datetime.now(UTC))
        with freeze_time('2015-01-01'):
            user_2 = UserFactory(birth_date=datetime.now(UTC))
        with freeze_time('2010-01-01'):
            user_3 = UserFactory(birth_date=datetime.now(UTC))

        request_data = request_builder(self, user, user_2, user_3)
        expected_ids = expected_ids_fn(self, user, user_2, user_3)
        query = self.rqo.create_search_query(User, db.session.query(User.id), request_data)
        assert self._get_values(query) == expected_ids, description

    @pytest.mark.parametrize(
        'description, request_builder, expected_ids_fn',
        [
            (
                'equals',
                lambda self, d, *_: self._search_request('size', 'eq', d.size),
                lambda self, d, *_: {d.id},
            ),
            (
                'not equals',
                lambda self, d, *_: self._search_request('size', 'ne', d.size),
                lambda self, _, d2, d3: {d2.id, d3.id},
            ),
            (
                'less than',
                lambda self, _, d2, __: self._search_request('size', 'lt', d2.size),
                lambda self, d, *_: {d.id},
            ),
            (
                'less than equals',
                lambda self, _, d2, __: self._search_request('size', 'lte', d2.size),
                lambda self, d, d2, _: {d.id, d2.id},
            ),
            (
                'great than',
                lambda self, _, d2, d3: self._search_request('size', 'gt', d2.size),
                lambda self, _, __, d3: {d3.id},
            ),
            (
                'great than equals',
                lambda self, _, d2, d3: self._search_request('size', 'gte', d2.size),
                lambda self, _, d2, d3: {d2.id, d3.id},
            ),
            (
                'in',
                lambda self, d, d2, d3: self._search_request(
                    'size',
                    'in',
                    f'{d3.size}{rqo.REQUEST_QUERY_DELIMITER}{d2.size}{rqo.REQUEST_QUERY_DELIMITER}{d.size}',
                ),
                lambda self, d, d2, d3: {d.id, d2.id, d3.id},
            ),
            (
                'nin',
                lambda self, d, d2, d3: self._search_request(
                    'size',
                    'nin',
                    f'{d3.size}{rqo.REQUEST_QUERY_DELIMITER}{d2.size}',
                ),
                lambda self, d, *_: {d.id},
            ),
            (
                'multiple queries',
                lambda self, d, _, d3: self._search_request(
                    ['size', 'size'],
                    ['gt', 'gte'],
                    [d.size, d3.size + 1],
                ),
                lambda *_: set(),
            ),
        ],
    )
    def test_create_search_query_integer(self, description, request_builder, expected_ids_fn):
        doc = LocalDocumentFactory(size=1_000_000)
        doc_2 = LocalDocumentFactory(size=2_000_000)
        doc_3 = LocalDocumentFactory(size=3_000_000)

        request_data = request_builder(self, doc, doc_2, doc_3)
        expected_ids = expected_ids_fn(self, doc, doc_2, doc_3)
        query = self.rqo.create_search_query(Document, db.session.query(Document.id), request_data)
        assert self._get_values(query) == expected_ids, description
