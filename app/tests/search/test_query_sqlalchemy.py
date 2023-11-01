import pytest

import typing as T
import operator

from sqlalchemy import (
    select,
    or_,
    and_
)

from app.models import (
    Construction,
    Change,
    FormulaElement,
)
from app.database import engine

from app.search import query as _q, query_sqlalchemy as q



@pytest.fixture
def sql_query():
    return q.SQLQuery()


@pytest.fixture
def duration_derivation():
    return q.ValueWithSignDerivation("duration", "duration_sign", q.SQLDurationComparison)


@pytest.fixture
def num_changes_derivation():
    return q.ValueWithSignDerivation("num_changes", "num_changes_sign",
                                     q.SQLNumChangesComparison)

@pytest.fixture
def default_derivations_dict(duration_derivation, num_changes_derivation):
    return {"construction": [duration_derivation, num_changes_derivation]}

@pytest.fixture
def default_full_query(default_derivations_dict):
    return q.SQLQuery(default_derivations_dict)


@pytest.fixture
def full_construction_form():
    return {'construction':
        {'formula': 'np* *v', 'meaning': 'minimizer',
         'in_rus_constructicon': True, 'num_changes_sign': 'le', 'num_changes': 5}
    }


@pytest.fixture
def construction_anchor_form():
    return {
        'construction':
            {'formula': 'np* *v', 'meaning': 'minimizer',
             'in_rus_constructicon': True, 'num_changes_sign': 'le', 'num_changes': 5},
        "anchor": 
            {'synt_functions_of_anchor': 'Subject',
             'anchor_schema': 'part VP', 'anchor_ru': 'хоть'}
    }


class TestSQLQuery:
    def test_creatable(self):
        assert q.SQLQuery()

    def test_basic(self, sql_query: q.SQLQuery, derivable_form):
        result = sql_query.parse_form(derivable_form)
        assert result == q.SQLConjunction([
            q.SQLComparison("duration", "eq", 200),
            q.SQLComparison("duration_sign", "eq", "ge"), 
            q.SQLComparison("formula", "eq", "np*")]
        )
    
    def test_form_names(self, sql_query: q.SQLQuery):
        assert sql_query.parse_form_name("anchor") == "construction"

    def test_subform(self, sql_query: q.SQLQuery, construction_subform):
        result = sql_query.parse_form(construction_subform)

        assert (type(result) == q.SQLConjunction and len(result.items) == 1
                and result.items[0] == q.SQLSubForm("construction", q.SQLConjunction(
                    [q.SQLComparison("duration", "eq", 200),
                    q.SQLComparison("duration_sign", "eq", "ge"), 
                    q.SQLTokensQuery("formula", "np*")])
                )
        )

    def test_two_subforms(self, sql_query: q.SQLQuery, two_subforms_form):
        result = sql_query.parse_form(two_subforms_form)

        assert (type(result) == q.SQLConjunction and len(result.items) == 2
                and result.items[0] == q.SQLSubForm("construction", q.SQLConjunction(
                    [q.SQLComparison("duration", "eq", 200),
                     q.SQLComparison("duration_sign", "eq", "ge"), 
                     q.SQLTokensQuery("formula", "np*")])
                ) and result.items[1] == q.SQLSubForm("construction", q.SQLConjunction(
                    [q.SQLComparison("synt_functions_of_anchor", "eq", "Subject"),
                     q.SQLComparison("anchor_schema", "eq", "part VP"),
                     q.SQLComparison("anchor_ru", "eq", "хоть")])
                )
        )

    def test__init__with_derivation(self, duration_derivation, construction_subform):
        query = q.SQLQuery({"construction": [duration_derivation]})

        result = query.parse_form(construction_subform)
        assert result == q.SQLConjunction([
            q.SQLSubForm("construction", q.SQLConjunction(
                [q.SQLDurationComparison("duration", "ge", 200), 
                 q.SQLTokensQuery("formula", "np*")])
        )])

    def test_add_derivation(self, duration_derivation, construction_subform):
        query = q.SQLQuery()
        query.add_derivation("construction", duration_derivation)
        result = query.parse_form(construction_subform)
        
        assert result == q.SQLConjunction([
            q.SQLSubForm("construction", q.SQLConjunction(
                [q.SQLDurationComparison("duration", "ge", 200), 
                 q.SQLTokensQuery("formula", "np*")])
            )
        ])

    def test_full_construction(self, default_full_query: q.SQLQuery,
                               full_construction_form):
        query = default_full_query

        result = query.parse_form(full_construction_form)
        assert result == q.SQLConjunction([
            q.SQLSubForm("construction", q.SQLConjunction(
                [q.SQLNumChangesComparison("num_changes", "le", 5),
                 q.SQLTokensQuery("formula", "np* *v"),
                 q.SQLComparison("meaning", "eq", "minimizer"),
                 q.SQLComparison("in_rus_constructicon", "eq", True),
                ]
            ))
        ])

    def test_full_construction_with_anchor(
        self, default_full_query: q.SQLQuery, construction_anchor_form
    ):
        query = default_full_query

        result = query.parse_form(construction_anchor_form)
        assert result == q.SQLConjunction([
            q.SQLSubForm("construction", q.SQLConjunction(
                [q.SQLNumChangesComparison("num_changes", "le", 5), 
                 q.SQLTokensQuery("formula", "np* *v"),
                 q.SQLComparison("meaning", "eq", "minimizer"),
                 q.SQLComparison("in_rus_constructicon", "eq", True),
                ]
            )),
            q.SQLSubForm("construction", q.SQLConjunction(
                [q.SQLComparison("synt_functions_of_anchor", "eq", "Subject"),
                 q.SQLComparison("anchor_schema", "eq", "part VP"),
                 q.SQLComparison("anchor_ru", "eq", "хоть")])
            ),
        ])

    # TODO: tests for changes
    def test_change(self): ...


class TestSQL:
    def test_subform_deriv(self, duration_derivation, proper_construction_subform):
        sql_query = q.SQLQuery({"change": [duration_derivation]})

        result: q.BaseQueryElement = sql_query.parse_form(proper_construction_subform) 

        stmt = sql_query.query()
        print(stmt.compile(compile_kwargs={"literal_binds": True}))

