import pytest

import typing as T
import operator

from app.search import query as q


@pytest.fixture
def base_query():
    return q.BaseQuery()


# conftest.py
# @pytest.fixture
def complex_form(): ...


@pytest.fixture
def simple_form():
    return {'formula': 'np*', 'meaning': 'minimizer'}

# conftest.py
# @pytest.fixture
def derivable_form() -> T.Dict[str, str | int]: ...


# conftest.py
# @pytest.fixture
def construction_subform() -> T.Dict[str, T.Dict[str, str | int]]: ...


# conftest.py
# @pytest.fixture
def two_subforms_form() -> T.Dict[str, T.Dict[str, str | int]]: ...
    # return {"construction": {"duration": 200, "duration_sign": "ge", "formula": "np*"},
    #         "anchor": {"synt_functions_of_anchor": "Subject"}}


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


def test_stringPattern():
    assert q.StringPattern("formula", "np*") == q.StringPattern("formula", "np*")


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


def test_conjunctionCopies__eq():
    assert q.ConjunctionCopies([
        q.Comparison("year", "ge", 1850), q.Comparison("year", "ge", 1951),
    ]) == q.ConjunctionCopies([
        q.Comparison("year", "ge", 1850), q.Comparison("year", "ge", 1951),
    ])

    assert q.ConjunctionCopies([
        q.Comparison("year", "ge", 1850), q.Comparison("year", "ge", 1951),
    ]) != q.Conjunction([
        q.Comparison("year", "ge", 1850), q.Comparison("year", "ge", 1951),
    ])


class TestValueWithSignDerivation:
    def test_basic(self, derivable_form):
        dur_deriv = q.ValueWithSignDerivation("duration", "duration_sign")
        result = dur_deriv(derivable_form)
        assert result == q.Comparison("duration", "ge", 200)
    
    def test_derived_class(self, derivable_form):
        class SpecialComparison(q.Comparison): ...

        dur_deriv_2 = q.ValueWithSignDerivation("duration", "duration_sign", SpecialComparison)
        result = dur_deriv_2(derivable_form)
        assert result == SpecialComparison("duration", "ge", 200)


# def test_SubForm():
#     assert True

@pytest.fixture
def duration_derivation():
    return q.ValueWithSignDerivation("duration", "duration_sign")


# class BaseTestQuery:
#     def test_creatable(self): ...
#     def test_basic(self, query: q.BaseQuery, form): ...
#     def test_subform(self, query: q.BaseQuery, subform): ...
#     def test_two_subforms(self, query: q.BaseQuery, subform): ...
#     def test__init__with_derivation(self, query: q.BaseQuery, ): ...
#     def test_add_derivation(self, *args, **kwargs): ...


class TestBaseQuery():
    def test_creatable(self):
        assert q.BaseQuery()
    
    def test_basic(self, base_query: q.BaseQuery, derivable_form):
        result = base_query.parse_form(derivable_form)
        assert result == q.Conjunction([q.Comparison("duration", "eq", 200),
                                        q.Comparison("duration_sign", "eq", "ge"), 
                                        q.Comparison("formula", "eq", "np*")])

    def test_subform(self, base_query: q.BaseQuery, construction_subform):
        result = base_query.parse_form(construction_subform)

        assert (type(result) == q.Conjunction and len(result.items) == 1
                and result.items[0] == q.SubForm("construction", q.Conjunction(
                    [q.Comparison("duration", "eq", 200),
                    q.Comparison("duration_sign", "eq", "ge"), 
                    q.Comparison("formula", "eq", "np*")])
                )
        )

    def test_two_subforms(self, base_query: q.BaseQuery, two_subforms_form):
        result = base_query.parse_form(two_subforms_form)

        assert (type(result) == q.Conjunction and len(result.items) == 2
                and result.items[0] == q.SubForm("construction", q.Conjunction(
                    [q.Comparison("duration", "eq", 200),
                    q.Comparison("duration_sign", "eq", "ge"), 
                    q.Comparison("formula", "eq", "np*")])
                )
                and result.items[1] == q.SubForm("anchor", q.Conjunction(
                    [q.Comparison("synt_functions_of_anchor", "eq", "Subject"),
                     q.Comparison("anchor_schema", "eq", "part VP"),
                     q.Comparison("anchor_ru", "eq", "хоть")])
                )
        )

    def test__init__with_derivation(self, duration_derivation, construction_subform):
        base_query = q.BaseQuery({"construction": [duration_derivation]})
        result = base_query.parse_form(construction_subform)
        assert result == q.Conjunction([
            q.SubForm("construction", q.Conjunction(
                [q.Comparison("duration", "ge", 200), 
                 q.Comparison("formula", "eq", "np*")])
        )])

    def test_add_derivation(self, duration_derivation, construction_subform):
        base_query = q.BaseQuery()
        base_query.add_derivation("construction", duration_derivation)
        result = base_query.parse_form(construction_subform)
        
        assert result == q.Conjunction([
            q.SubForm("construction", q.Conjunction(
                [q.Comparison("duration", "ge", 200), 
                 q.Comparison("formula", "eq", "np*")]))
        ])


def test_simple_form(base_query, simple_form):
    result = base_query.parse(simple_form)
    assert result == [q.Comparison("formula", "eq", "np*"),
                      q.Comparison("meaning", "eq", "minimizer")]

