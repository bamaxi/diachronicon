import pytest
import unittest

from app.models import (
    ConstructionVariant,
    FormulaElement,
)
import app.update_db.update as u
from app.update_db.update import (
    read_until,
    tokenize_formula,
    flatten_span,
    parse_formula,
    get_formula_element_variants,
    parse_formula_old
)


FORMULA2TOKENS = dict((
    # 'np vp': [{'value': 'np'}, {'value': 'vp'}],
    ("N-Gen.Pl Cop (хоть) пруд пруди",
     [{'val': 'N-Gen.Pl'}, {'val': 'Cop'}, {'type': 'maybe_span', 'val':
        [{'val': 'хоть'}]}, {'val': 'пруд'}, {'val': 'пруди'}]),
    ("Prep N-Dat.Sg не по адресу",
     [{'val': 'Prep'}, {'val': 'N-Dat.Sg'}, {'val': 'не'}, {'val': 'по'},
      {'val': 'адресу'}]),
    ("((N-Nom) Cop) без понятия",
     [{'type': 'maybe_span', 'val': [{'type': 'maybe_span', 'val': [{'val': 'N-Nom'}]},
                                     {'val': 'Cop'}]},
      {'val': 'без'}, {'val': 'понятия'}]
     )
    # "в точности PronDem",
    # "NumCrd N с гаком",
    # "NP Cop не что (иное) как NP",
    # "NP-Gen не*густо",
    # "(NP) все до одного (NP-Gen)",
    # "ни капли N-Gen",
    # "ни капли не VP",
    # "(у NP-Gen) руки не доходят / дойдут / дошли / дойдут (Inf / до NP-Gen)",
    # "на кой NP-Nom (NP-Dat) сдаться-Pst",
    # "NP-Dat Cop до лампочки (NP-Nom)",
    # "не ахти ((PronInt) NP) / не ахти ((PronInt) AdvP)",
    # "((N-Nom) Cop) без понятия",
    # "N-Nom знает ((PronInt) (NP))",
    # "Фиг NP-Dat",
    # "(N-Nom) ни рыба ни мясо",
    # "(у NP-Gen | в NP-Loc | не Cop) ни стыда ни совести",
))


TEST_NAME2FORM_TOKS = {
    'test_simple':
        ("Prep N-Dat.Sg не по адресу",
         [{'val': 'Prep'}, {'val': 'N-Dat.Sg'}, {'val': 'не'}, {'val': 'по'},
          {'val': 'адресу'}]),
    'test_optional':
        ("N-Gen.Pl Cop (хоть) пруд пруди",
         [{'val': 'N-Gen.Pl'}, {'val': 'Cop'}, {'type': 'maybe_span', 'val':
            [{'val': 'хоть'}]}, {'val': 'пруд'}, {'val': 'пруди'}]),
    'test_nested_spans':
        ("((N-Nom x) Cop) xx",
         [{'type': 'maybe_span', 'val': [{'type': 'maybe_span',
                                          'val': [{'val': 'N-Nom'}, {'val': 'x'}]},
                                         {'val': 'Cop'}]},
          {'val': 'xx'}]
         ),
    'test_alt_spans':
        ("ни души (NP-Gen/не VP)",
         [],
         )
}


class ReadWhileTestCase(unittest.TestCase):
    def test_simple_space(self):
        s = "N-Gen.Pl Cop (хоть) пруд пруди"
        read, stopped_at = read_until(iter(s), lambda char: char == ' ')
        assert read == 'N-Gen.Pl' and stopped_at == ' ', \
               f"actually read: `{read}`, stopped_at: `{stopped_at}`"

    def test_brackets_space(self):
        s = "(N-Nom) ни рыба ни мясо"
        read, stopped_at = read_until(iter(s), lambda char: char == ' ')
        assert read == '(N-Nom)' and stopped_at == ' ', \
               f"actually read: `{read}`, stopped_at: `{stopped_at}`"

    def test_brackets_space_bracket(self):
        s = "(N-Nom) ни рыба ни мясо"
        read, stopped_at = read_until(iter(s), lambda char: char in ' )')
        assert read == '(N-Nom' and stopped_at == ')', \
               (f"actually read: `{read}`, stopped_at: `{stopped_at}`"
                f"\n{read=='(N-nom'} {stopped_at==')'}")

        s_iter = iter(s)
        read, stopped_at = read_until(s_iter, lambda char: char in ' ()')
        assert read == '' and stopped_at == '(', \
               f"actually read: `{read}`, stopped_at: `{stopped_at}`"

        symb = next(s_iter)
        read, stopped_at = read_until(s_iter, lambda char: char in ' ()')
        assert symb + read == 'N' + '-Nom' and stopped_at == ')', \
            f"actually read: `{read}`, stopped_at: `{stopped_at}`"


class FormulaElemVariantsTestCase(unittest.TestCase):
    def test_one_line(self):
        assert get_formula_element_variants(
            'N-Nom: дьявол, бес, ляд, бог, х*й, хрен, х*р, пес, шут, кто, фиг'
        ) == {
            'N-Nom': ['дьявол', 'бес', 'ляд', 'бог', 'х*й', 'хрен', 'х*р',
                      'пес', 'шут', 'кто', 'фиг']
        }


class TokenizeFormulaTestCase(unittest.TestCase):
    # def test_simple(self):
    #     for formula, tokens in FORMULA2TOKENS.items():
    #         with self.subTest(formula=formula, expected_tokens=tokens):
    #             assert tokenize_formula(formula) == tokens
    def test_simple(self):
        formula, tokens = TEST_NAME2FORM_TOKS['test_simple']
        assert tokenize_formula(formula) == tokens

    def test_optional(self):
        formula, tokens = TEST_NAME2FORM_TOKS['test_optional']
        assert tokenize_formula(formula) == tokens

    def test_nested_spans(self):
        formula, tokens = TEST_NAME2FORM_TOKS['test_nested_spans']
        assert tokenize_formula(formula) == tokens

    def test_alt_spans(self):
        formula, tokens = TEST_NAME2FORM_TOKS["test_alt_spans"]
        assert not tokenize_formula(formula)


class TokenizeSpanFlattenTestCase(unittest.TestCase):
    def test_optional(self):
        tokens = [{'type': 'maybe_span', 'val': [{'val': 'N-Nom'}]}, {'val': 'Cop'}]
        formula_elems = [{'value': 'N-Nom', 'is_optional': True, 'depth': 1},
                         {'value': 'Cop', 'is_optional': False, 'depth': 1}]
        assert flatten_span(tokens) == formula_elems
        assert flatten_span(tokenize_formula("((N-Nom) Cop)")[0]['val']) \
               == formula_elems

    def test_nested_spans(self):
        tokens = [{'type': 'maybe_span', 'val': [{'val': 'N-Nom'}, {'val': '_'}]},
                  {'val': 'Cop'}]
        formula_elems = [{'value': 'N-Nom', 'is_optional': False, 'depth': 2},
                         {'value': '_', 'is_optional': False, 'depth': 2},
                         {'value': 'Cop', 'is_optional': False, 'depth': 1}]

        assert flatten_span(tokens) == formula_elems
        assert flatten_span(tokenize_formula("((N-Nom _) Cop)")[0]['val']) \
               == formula_elems
        
    # def test_alt_spans(self):
        



class TestToFormula:
    def test_basic(self):
        formula = "Prep N-Dat.Sg не по адресу"
        
        elems = u.to_formula(formula)

        proper_elems = [
            FormulaElement(value="Prep", order=0),
            FormulaElement(value="N-Dat.Sg", order=1),
            FormulaElement(value="не", order=2),
            FormulaElement(value="по", order=3),
            FormulaElement(value="адресу", order=4),
        ]

        assert len(elems) == len(proper_elems) and all(
            elem.shallow_eq(proper_elem) for elem, proper_elem in zip(elems, proper_elems)
        )


if __name__ == "__main__":
    unittest.main()

