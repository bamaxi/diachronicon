import pytest

import operator

from app.search import query as q


@pytest.fixture
def base_query():
    return q.BaseQuery()

@pytest.fixture
def complex_form():
    return {
        'construction':
            {'constructionId': '', 'formula': 'np*', 'meaning': 'minimizer',
            'in_rus_constructicon': False, 'num_changes_sign': 'le', 'num_changes': 5,
            'csrf_token': None},
        'anchor': {'synt_functions_of_anchor': None, 'anchor_schema': '', 'anchor_ru': '',
                'csrf_token': None},
        'changes': [{'formula': '', 'stage_abs': None, 'level': '', 'type_of_change': '',
                    'duration_sign': 'eq', 'duration': 5, 'first_attested': 1900, 
                    'last_attested': None, 'csrf_token': None},
                    {'formula': 'vp*', 'stage_abs': None, 'level': '', 'type_of_change': '',
                    'duration_sign': '', 'duration': None, 'first_attested': None,
                    'last_attested': None, 'csrf_token': None},
                    {'formula': 'dp*', 'stage_abs': 2, 'level': '', 'type_of_change': '',
                    'duration_sign': '', 'duration': None, 'first_attested': None,
                    'last_attested': None, 'csrf_token': None}
                ], 
        'csrf_token': None
    }


@pytest.fixture
def simple_form():
    return {'formula': 'np*', 'meaning': 'minimizer'}


def test_comparison__init():
    comp1 = q.Comparison("formula", "eq", "np*")
    assert comp1.param == "formula" and comp1.op == operator.eq and comp1.value == "np*"

    comp2 = q.Comparison("formula", operator.eq, "np*")
    assert comp2.param == "formula" and comp2.op == operator.eq and comp2.value == "np*"

    comp3_str = q.Comparison("year", "ge", "1951")
    assert (comp3_str.param == "year" and comp3_str.op == operator.ge
            and comp3_str.value == "1951")
    
    comp3_int = q.Comparison("year", "ge", 1951)
    assert (comp3_int.param == "year" and comp3_int.op == operator.ge
            and comp3_int.value == 1951)
    
    comp4 = q.Comparison("year", "eq", 1951)
    assert (comp4.param == "year" and comp4.op == operator.eq
            and comp4.value == 1951)
    
    comp5 = q.Comparison("year", "gt", 1951)
    assert (comp5.param == "year" and comp5.op == operator.gt
            and comp5.value == 1951)
    
    comp6 = q.Comparison("year", "le", 1951)
    assert (comp6.param == "year" and comp6.op == operator.le
            and comp6.value == 1951)
    
    comp7 = q.Comparison("year", "lt", 1951)
    assert (comp7.param == "year" and comp7.op == operator.lt
            and comp7.value == 1951)

    comp8 = q.Comparison("year", "ne", 1951)
    assert (comp8.param == "year" and comp8.op == operator.ne
            and comp8.value == 1951)


def test_comparison__eq():
    assert q.Comparison("formula", "eq", "np*") == q.Comparison("formula", "eq", "np*")
    assert q.Comparison("year", "eq", 1951) == q.Comparison("year", "eq", 1951)

    assert q.Comparison("year", "eq", "1951") != q.Comparison("year", "eq", 1951)

    assert q.Comparison("formula", "eq", "np*") != q.Comparison("stage", "eq", "np*")
    assert q.Comparison("stage", "eq", "np*") != q.Comparison("formula", "eq", "np*")

    assert q.Comparison("formula", "eq", "np*") != q.Comparison("formula", "ne", "np*")
    assert q.Comparison("formula", "ne", "np*") != q.Comparison("formula", "eq", "np*")

    assert q.Comparison("formula", "eq", "np*") != q.Comparison("formula", "eq", "vp")
    assert q.Comparison("formula", "eq", "vp") != q.Comparison("formula", "eq", "np*")

    assert q.Comparison("formula", "ge", "vp") != q.Comparison("formula", "eq", "np*")

    assert q.Comparison("stage", "ge", "vp") != q.Comparison("formula", "eq", "np*")


def test_conjunction__eq():
    # both eq
    assert q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ]) == q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])

    # one different
    assert q.Conjunction([
        q.Comparison("stage", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ]) != q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])
    
    assert q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("last_year", "ge", 1951),
    ]) != q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])
    assert q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "le", 1951),
    ]) != q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])
    assert q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 2015),
    ]) != q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])

    # both different
    assert q.Conjunction([
        q.Comparison("stage", "eq", "np*"), q.Comparison("year", "ge", 2015),
    ]) != q.Conjunction([
        q.Comparison("formula", "eq", "np*"), q.Comparison("year", "ge", 1951),
    ])


def test_query_creatable():
    assert q.BaseQuery()


def test_simple_form(base_query, simple_form):
    
    result = base_query.parse(simple_form)
    assert result == [q.Comparison("formula", "eq", "np*"),
                      q.Comparison("meaning", "eq", "minimizer")]




