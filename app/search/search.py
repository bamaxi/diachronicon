from typing import Dict, Union, Type

from datetime import datetime
import logging
from operator import (
    le,
    ge,
    eq
)

import pandas as pd
import sqlalchemy.sql.expression
from sqlalchemy import (
    select,
    or_,
    and_
)
from sqlalchemy.orm import aliased
from flask import current_app
from flask import render_template, abort, request, redirect

from app.search import bp
from app.models import (
    Construction,
    Change,
    GeneralInfo,
    Constraint,
    FormulaElement
)
from app.search.plotting import (
    NO_DATE,
    new_plot_single_const_changes,
    super_new_plot_single_const_changes,
    ConstructionChangesPlot
)


# from app.utils import pretty_log
# from ..testing.profiling import profiled

logger = logging.getLogger()

_OPERATORS = {'le': le, 'ge': ge, 'eq': eq}
CHANGE_COLUMNS = [str(col).removeprefix('change.')
                  for col in Change.__table__.columns]

MEANING_VALUES = []  # Construction.contemporary_meaning.unique()
SYNT_FUNCTIONS_ANCHOR = []  # Construction.synt_function_of_anchor.type.enums

pd_na = pd.NA


def parse_year(year: Union[str, int, None], left_bias=0.0):
    """Parse year string into datetime

    :param year:
    :param left_bias:
    :return:
    """
    if not year or year == '-':
        return None
    if isinstance(year, int) or year.isnumeric():
        return year
    if '-' in year:
        if year.endswith('-ые'):
            return int(year.split('-')[0])

        left, right = [int(part) for part in year.split('-')]
        return int(left + (right-left) * (1-left_bias))

    logger.debug(f"unsupported year type: {year}")
    return None


def prepare_graph_data(changes):
    """Update dates and

    :param changes:
    :return:
    """
    changes_data = {}

    for change in changes:
        level_data = changes_data.setdefault(change.level, {})

        for field in ('first_attested', 'last_attested'):
            year = parse_year(getattr(change, field))
            value = datetime(year, 1, 1) if year else NO_DATE

            level_data.setdefault(field, []).append(value)

        # if all(date is NO_DATE for date in level_data.values()):

    return changes_data


@bp.route('/item/<int:index>/')
@bp.route('/construction/<int:index>/')
def construction(index: int):
    print(index, type(index))
    index = int(index)

    session = current_app.db_session
    res_ = session.execute(select(Construction).where(Construction.id == index))
    construction = res_.first() or abort(404)
    construction = construction[0]

    changes_data = prepare_graph_data(construction.changes)
    logger.debug(f"{changes_data}")

    if changes_data:
        graphJSON = str(ConstructionChangesPlot.from_elements(changes_data).to_plotly_json())
        # graphJSON = new_plot_single_const_changes(changes_data)
        # graphJSON = super_new_plot_single_const_changes(changes_data)
    else:
        graphJSON = None

    return render_template(
        'construction.html',
        title=f"Конструкция '{construction.general_info.name}'",
        year=datetime.now().year,
        res_id=construction.id,
        construction=construction,
        graphJSON=graphJSON
    )


HTML_NAME2MODEL = {
    'c': Construction,
    'constraint': Constraint,
    'change': Change,
    # '': GeneralInfo,
}

html_name2table_name = {
    'meaning': 'contemporary_meaning'
}


def make_basic_formula_query(stmt: sqlalchemy.sql.expression.Select,
                             model: Construction, value: str,
                             *args, **kwargs):
    return stmt.where(getattr(model, 'formula').like(f"%{value}%"))


def _make_skip_optional_subquery(cur_elem, distance, model=FormulaElement):
    return select(model.id).where(
        FormulaElement.construction_id == cur_elem.construction_id,
        FormulaElement.is_optional == True,
        cur_elem.order == FormulaElement.order + distance,
    )


def make_byelem_formula_query(
    stmt: sqlalchemy.sql.expression.Select,
    model: Type[FormulaElement], value: str,
    params_values
):
    """Update stmt to filter by formula elementwise, allowing simple regex/logic

    :param stmt:
    :param model:
    :param value:
    :return:
    """
    elements = value.split(' ')
    print(elements)

    element_tables = [aliased(FormulaElement) for i in range(len(elements))]

    # params = {}

    stmt = stmt.where(getattr(model, 'id') == element_tables[0].construction_id)

    for i, element_value in enumerate(elements):
        cur_elem_table = element_tables[i]

        # TODO: опционально пропускать при поиске по элементам те, что в скобках
        # TODO: asterisk instead of element
        if i != 0:
            stmt = stmt.where(
                cur_elem_table.construction_id == element_tables[0].construction_id,
                or_(
                    cur_elem_table.order == element_tables[i-1].order + 1,
                    and_(
                        cur_elem_table.order == element_tables[i-1].order + 2,
                        _make_skip_optional_subquery(cur_elem_table, 1).exists()
                    )
                )
            )

        # params[f'gloss{i}'] = value  # or text(value)
        corrected_val = element_value.replace('*', '%')
        stmt = stmt.where(getattr(cur_elem_table, 'value').ilike(corrected_val))

    return stmt


def make_formula_query(stmt, model, value, params_values):
    if '*' in value:
        return make_byelem_formula_query(stmt, model, value)
    return make_basic_formula_query(stmt, model, value)


def make_duration_query(stmt, model, duration_value, params_values):
    duration_sign = params_values.get('duration_sign')
    logger.debug(f"in duration: {duration_sign}, {duration_value}")
    if not duration_sign:
        logger.warning(f"no argument in form: `duration-sign`")
        return stmt

    op = _OPERATORS[duration_sign]
    logger.info(f"op and value are: {op} {duration_value}")
    print(f"op and value are: {op} {duration_value}")
    return stmt.where(
        # op(model.last_attested - model.first_attested, duration_value)
        op(getattr(model, "last_attested") - getattr(model, "first_attested"),
           duration_value)
    )


param2query_maker = {
    # 'formula': make_formula_query,
    'formula': make_formula_query,
    'element': make_basic_formula_query,
    'duration': make_duration_query
}


def build_query(
    items: Dict[str, str], parts_sep='-', ready_only=False,
    # i_to_zero_base=True
) -> sqlalchemy.sql.expression.Select:
    """Collect html params into database query"""
    items_by_model = {}

    for key, value in items:
        if not value:
            continue

        logger.debug(f"{key} -- {value}")

        key_model_part, key_param_part = key.split(parts_sep, maxsplit=1)
        key_param_part = html_name2table_name.get(key_param_part) or key_param_part

        # there could be multiple constraints or changes coded
        #   in html as `constraint-3-element` for example
        if parts_sep not in key_param_part:
            items_by_model.setdefault(
                    HTML_NAME2MODEL[key_model_part], {}
            )[key_param_part] = value
            continue

        # the key is of the type `change-1-first_attested`
        i, key_param = key_param_part.split(parts_sep, maxsplit=1)
        model_list = items_by_model.setdefault(HTML_NAME2MODEL[key_model_part], [])

        i = int(i)

        print(i, key_param, model_list, len(model_list) < i)

        if len(model_list) < i:
            model_list.append({key_param: value})
        else:
            model_list[i-1][key_param] = value

    if ready_only:
        items_by_model[Construction]['status'] = 'ready'

    print(items_by_model)
    if not items_by_model:
        return

    # make the query itself
    stmt = select(*[model for model in items_by_model])
    for model, params_values in items_by_model.items():
        if not isinstance(params_values, list):
            pass
        else:
            # code for aliases? How should multiple constraints or multiple
            #   changes be connected?
            params_values = params_values[0]

        for param, val in params_values.items():
            print("model, param, val:", model, param, val)
            if '_' in param:  # a helper parameter
                continue
            if param in param2query_maker:
                # special processing of certain search fields
                print(param)
                stmt = param2query_maker[param](stmt, model, val, params_values)
            else:
                # a simple equality testing
                stmt = stmt.where(getattr(model, param) == val)

    print(stmt)

    return stmt


# TODO: add wtforms instead of manual handling
@bp.route('/search/', methods=['GET', 'POST'])
def search():

    # TODO: implement as singletons?
    try:
        meaning_values = Construction.contemporary_meaning.unique()
    except (ValueError, TypeError):
        meaning_values = MEANING_VALUES
    # current_app.db_session.execute(
    #     select(Construction.contemporary_meaning)
    # ).scalars().all()
    try:
        synt_functions_anchor = Construction.synt_function_of_anchor.type.enums
    except (ValueError, TypeError):
        synt_functions_anchor = SYNT_FUNCTIONS_ANCHOR

    query_args = list(request.args.items())
    print(*query_args, sep='\n')
    logger.debug(f"{query_args}")

    # a GET request with no parameters or unfilled parameters
    if (request.method != 'POST'
            and (not (request.args and any(val for key, val in query_args))
                 or request.args.get('no-search') == '1')
   ):
        # logger.debug(f"no query, returning clear form")

        return render_template(
            'search.html',
            title='Поиск',
            year=datetime.now().year,
            meaning_values=meaning_values,
            synt_functions_anchor=synt_functions_anchor,
            query=request.args,
        )

    print(f'in conditional')

    print(request.form)
    print(request.data)

    stmt = build_query(query_args)

    results = current_app.db_session.execute(stmt)

    all_results = results.scalars().all()

    print(f"len results: {len(all_results)}")

    return render_template(
        'search.html',
        title='Поиск: результаты',
        year=datetime.now().year,
        meaning_values=meaning_values,
        synt_functions_anchor=synt_functions_anchor,
        form_input=request.form,
        results=all_results,
        n_param_results=len(all_results),
        query=request.args
    )


@bp.route('/simple-search/')
def simple_search():
    return render_template(
        'search_simple.html',
        # '/errors/404.html',
        # message="Page under construction"
    ), 404
