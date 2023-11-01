import pytest
import typing as T


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
def derivable_form() -> T.Dict[str, str | int]:
    return {"duration": 200, "duration_sign": "ge", "formula": "np*"}


@pytest.fixture
def construction_subform() -> T.Dict[str, T.Dict[str, str | int]]:
    return {"construction": {"duration": 200, "duration_sign": "ge", "formula": "np*"}}


@pytest.fixture
def proper_construction_subform() -> T.Dict[str, T.Dict[str, str | int]]:
    return {"construction": {"formula": "np*", "meaning": "Minimizer"}}


@pytest.fixture
def two_subforms_form() -> T.Dict[str, T.Dict[str, str | int]]:
    return {"construction": {"duration": 200, "duration_sign": "ge", "formula": "np*"},
            "anchor": {"synt_functions_of_anchor": "Subject",
                       'anchor_schema': 'part VP', 'anchor_ru': 'хоть'}}

