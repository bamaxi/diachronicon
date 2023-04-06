import re
from typing import Tuple, List, Dict, Union, Type, Optional

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
from sqlalchemy.orm import (
    aliased,
    joinedload,
    selectinload,
    Load,
    load_only
)
from flask import current_app
from flask import render_template, abort, request, redirect

from app.models import (
    Construction,
    Change,
    GeneralInfo,
    Constraint,
    FormulaElement,
    ConstructionVariant
)
from app.search import bp
from app.search.plotting import (
    NO_DATE,
    new_plot_single_const_changes,
    super_new_plot_single_const_changes,
    ConstructionChangesPlot
)


DBModel = Type[Union[
    Construction, Change, GeneralInfo, Constraint, FormulaElement,
    ConstructionVariant
]]
Model2Field2Val = Dict[DBModel, Union[Dict[str, Optional[str]],
                                      List[Dict[str, Optional[str]]]]]

logger = logging.getLogger(f"diachronicon.{__name__}")

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
    stmt = select(Construction).where(Construction.id == index).options(
        selectinload("*"))
    res_ = session.execute(stmt)

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
                             *args, column="formula", **kwargs
                             ):
    return stmt.where(getattr(model, column).like(f"%{value}%"))


def _make_skip_optional_subquery(cur_elem, distance, model=FormulaElement):
    return select(model.id).where(
        FormulaElement.construction_id == cur_elem.construction_id,
        FormulaElement.is_optional == True,
        cur_elem.order == FormulaElement.order + distance,
    )


def make_byelem_formula_query(
    stmt: sqlalchemy.sql.expression.Select,
    model: Type[FormulaElement], value: str,
    *args
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


def make_duration_query(stmt, model, _, params_values):
    # TODO: mutating while iterating is baaad
    duration_value = params_values.pop('duration')
    duration_sign = params_values.pop('duration_sign')
    # logger.debug(f"in duration: {duration_sign}, {duration_value}, {type(duration_value)} ")
    if not duration_sign:
        raise ValueError
    # if not duration_sign:
    #     logger.warning(f"no argument in form: `duration-sign`")
    #     return stmt

    # if not duration_value.isdigit():
    #     logger.warning(f"")

    op = _OPERATORS[duration_sign]
    logger.info(f"op and value are: {op} {duration_value}")
    return stmt.where(
        # op(model.last_attested - model.first_attested, duration_value)
        op(getattr(model, "last_attested") - getattr(model, "first_attested"),
           duration_value)
    )


param2query_maker = {
    # 'formula': make_formula_query,
    'formula': make_formula_query,
    "anchor_ru": make_formula_query,
    "anchor_en": lambda *args, **kwargs: make_basic_formula_query(
        *args, **kwargs, column="anchor_en"),
    "anchor_eng": lambda *args, **kwargs: make_basic_formula_query(
        *args, **kwargs, column="anchor_eng"),
    'duration': make_duration_query,
    'duration_sign': make_duration_query,
    "stage": lambda *args, **kwargs: make_basic_formula_query(
        *args, **kwargs, column="stage"),
    'element': lambda *args, **kwargs: make_basic_formula_query(
        *args, **kwargs, column="element"),
}


param2type_caster = {
    "first_attested": int,
    "last_attested": int,
    "duration": int,
    "in_rus_constructicon": lambda val: True if val == "on" else False
}


class BaseQuery:
    name_sep = "-"
    name_prefix: str
    basic_query_model = Construction
    basic_query_fields = ["id", "formula"]

    def __init__(self, **kwargs):
        super().__init__()
        for name, val in kwargs.items():
            setattr(self, name, val)

    @classmethod
    def from_submitted_args(cls, args):
        queried = {}

        prefix = cls.name_prefix + cls.name_sep
        len_prefix = len(prefix)

        logger.debug(str(prefix))
        for name, val in args.items():
            print(name, name.startswith(prefix), bool(val), val)
            if name.startswith(prefix) and val:
                actual_name = name[len_prefix:]
                queried[actual_name] = val

        logger.debug(str(queried))
        return cls(**queried)

    def _make_basic_query(self, *models: DBModel):
        basic_model = self.basic_query_model
        basic_fields = []
        if not basic_model in models:
            basic_fields = [getattr(basic_model, field)
                            for field in self.basic_query_fields]

        stmt = select(*basic_fields, *models)
        logger.info(f"base sql:\n{str(stmt)}")
        return stmt

    def make_basic_query(self):
        return self._make_basic_query()

    @staticmethod
    def tokenize_formula(formula):
        return [elem.replace("*", "%") for elem in formula.split()]

    def query_formula_element_regex(
        self, formula: str, formula_of_model: DBModel,
        cur_stmt: sqlalchemy.sql.expression.Select = None
    ):
        if cur_stmt is None:
            cur_stmt = self._make_basic_query(formula_of_model)

        elements = self.tokenize_formula(formula)

        first_element = elements[0]
        first_table = FormulaElement

        stmt = cur_stmt.where(formula_of_model.id == first_table.construction_id,
                              first_table.value.ilike(first_element))

        remaining_elements = elements[1:]
        element_tables = (
            [first_table]
            + [aliased(FormulaElement) for _ in range(len(remaining_elements))]
        )

        for i, element_value in enumerate(remaining_elements):
            cur_elem_table = element_tables[i]

            # TODO: опционально пропускать при поиске по элементам те, что в скобках
            # TODO: asterisk instead of element
            stmt = stmt.where(
                cur_elem_table.construction_id == first_table.construction_id,
                or_(
                    cur_elem_table.order == element_tables[i - 1].order + 1,
                    and_(
                        cur_elem_table.order == element_tables[i - 1].order + 2,
                        _make_skip_optional_subquery(cur_elem_table, 1).exists()
                    ))
            )

            # params[f'gloss{i}'] = value  # or text(value)
            stmt = stmt.where(getattr(cur_elem_table, 'value').ilike(element_value))

        return stmt

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({ ', '.join(f'{key}={val!r}' for key, val in vars(self).items()) })"
        )


class ChangeQuery(BaseQuery):
    name_prefix = "change"
    # __slots__ = ("construction_id", "stage", "level", "type_of_change",
    #              "first_attested")


class ConstraintQuery(BaseQuery):
    name_prefix = "change"


class ConstructionQuery(BaseQuery):
    name_prefix = "c"


# def _make_basic_select_list(columns=("id", "formula")) -> List[sqlalchemy.column]:
#     return [getattr(Construction, column)
#             for column in columns]


def make_select(
    model2items: Model2Field2Val, basic_construction_columns=("id", "formula"),
    count_construction_columns=("variants", "changes", "construction"),
    # non_queried_to_join = (ConstructionVariant),
    ignore_params=re.compile(r"duration")
) -> sqlalchemy.sql.expression.Select:
    """Make a minimal select based on mapping of model to params and values"""
    # basic_select_list = _make_basic_select_list(basic_construction_columns)
    print("in make_select")

    no_construction_model2items = {model: items
                                   for model, items in model2items.items()
                                   if model is not Construction}
    print(no_construction_model2items)
    # we always query construction
    stmt = select(Construction, *no_construction_model2items)
    print(stmt)

    # other models, like `Change` or `Constraint` must be joined to Construction
    #  (this is helped by `relationship` in their definition)
    # TODO: does querying variants or formula_element's require select here?
    for model, items in model2items.items():
        if model is Construction:
            continue

        print(model, items)
        stmt = stmt.join_from(Construction, model)
        print(f"updated stmt: {stmt}")

    construction_columns = list(basic_construction_columns)
    print(model2items.get(Construction, []))
    for column in model2items.get(Construction, []):
        print(column)
        if column not in basic_construction_columns:
            construction_columns.append(column)
    print(f"constr cols: {construction_columns}")

    # TODO: does filtering by `__dict__` always work? False positives/negatives?
    # load basic and queried columns of Construction
    stmt = stmt.options(
        Load(Construction).load_only(
            *[getattr(Construction, column) for column in construction_columns
              if column in Construction.__dict__])
    )

    print(f"select with load_only and join:\n{stmt}")

    # load queried columns of other tables
    for model, items in no_construction_model2items.items():
        print(f"model, items: {model}, {items}")
        for item in items:
            stmt = stmt.options(Load(model).load_only(
                *[getattr(model, column) for column in item
                  if column in model.__dict__])
            )
            print(f"updated statement:\n{stmt}")

    return stmt


def extract_queried(
    args: Dict[str, str], parts_sep='-', do_conversion=True
) -> Tuple[Model2Field2Val, Model2Field2Val]:
    """Extract query parameters and map them to models

    :return
    """
    print(f"in extract")

    model2field2val = current_model2query = {}
    model2derivable_param2val = {}

    for key, value in args.items():
        if not value:
            continue

        logger.debug(f"{key} -- {value}")

        key_model_part, key_param_part = key.split(parts_sep, maxsplit=1)
        key_param_part = html_name2table_name.get(key_param_part) or key_param_part

        current_model = HTML_NAME2MODEL[key_model_part]
        # there could be multiple constraints or changes coded
        #   in html as `constraint-3-element` for example
        if parts_sep not in key_param_part:
            is_param_singleton = True
            key_param = key_param_part
        else:
            is_param_singleton = False
            i, key_param = key_param_part.split(parts_sep, maxsplit=1)

        print(key_param, current_model, key_param in current_model.__dict__,
              current_model.__dict__)
        if key_param not in current_model.__dict__:
            current_model2query = model2derivable_param2val

        if key_param in param2type_caster:
            cast_func = param2type_caster[key_param]
            value = cast_func(value)

        if is_param_singleton:
            current_model2query.setdefault(
                current_model, {}
            )[key_param_part] = value
            continue

        # here the key is of the type `change-1-first_attested`
        model_list = current_model2query.setdefault(current_model, [])

        i = int(i)

        print(i, key_param, model_list, len(model_list) < i)

        if len(model_list) < i:
            model_list.append({key_param: value})
        else:
            model_list[i-1][key_param] = value

    print(f"end of extract:\n{model2field2val}\n{model2derivable_param2val}")
    return model2field2val, model2derivable_param2val


def add_base_fields_for_derivable(
    model2field2val: Model2Field2Val,
    model2derivable_param2val: Model2Field2Val
) -> None:
    print(f"in add_base_fields_for_derivable")

    # duration
    for i, change_desc in enumerate(model2derivable_param2val.get(Change, [])):
        if "duration" in change_desc:
            # TODO: we could also add it only to the first dict,
            #   which is enough to be included?
            orig_changes = model2field2val.setdefault(Change, [])
            if i < len(orig_changes):
                orig_changes[i].update({"first_attested": None,
                                        "last_attested": None})
            else:  # TODO: is this proper?
                orig_changes.append({"first_attested": None, "last_attested": None})

    # attestation
    for i, change_desc in enumerate(model2field2val.get(Change, [])):
        if ("first_attested" in change_desc) ^ ("last_attested" in change_desc):
            change_desc["first_attested"] = change_desc.get("first_attested", None)
            change_desc["last_attested"] = change_desc.get("last_attested", None)


def build_query(
    args: Dict[str, str], parts_sep='-', ready_only=False,
    # i_to_zero_base=True
) -> sqlalchemy.sql.expression.Select:
    """Collect html params into database query"""
    # TODO: use Bundles? One for that which is constant and duplicated in rows
    #   and the other for what was queried at the start

    model2field2val, model2derivable_param2val = extract_queried(args)

    print(model2field2val, model2derivable_param2val, sep="\n")
    # if not model2field2val:
    #     return

    add_base_fields_for_derivable(model2field2val, model2derivable_param2val)
    print("after add_base_..")
    print(model2field2val, model2derivable_param2val, sep="\n")

    if ready_only:
        model2field2val.setdefault(GeneralInfo, {})['status'] = 'ready'

    # make the query itself
    # stmt = select(*[model for model in items_by_model])
    stmt = make_select(model2field2val)
    print(f"the basic select is\n{stmt}")

    for model, params_values in model2field2val.items():
        if not isinstance(params_values, list):
            pass
        else:
            # TODO
            #   code for aliases? How should multiple constraints or multiple
            #   changes be connected?
            params_values = params_values[0]

        for param, val in params_values.items():
            print(f"model, param, val: {model}, {param}, {val}")
            # if '_' in param:  # a helper parameter
            #     continue

            if val is None:
                continue

            if param in param2query_maker:
                # special processing of certain search fields
                print(param)
                stmt = param2query_maker[param](stmt, model, val, params_values)
            else:
                # a simple equality testing
                stmt = stmt.where(getattr(model, param) == val)

    changes = model2derivable_param2val.get(Change, [])
    for change in changes:
        if "duration" in change:
            stmt = make_duration_query(stmt, Change, change["duration"], change)
        # TODO: remove once searching many is supported
        break

    print(f"final select is:\n{stmt}")

    return stmt


def group_rows_by_construction(rows: List[Dict]) -> Dict:
    row_id2data = {}

    for row in rows:
        id_ = row["id"]
        row_id2data.setdefault(id_, []).append(row)

    return row_id2data


# TODO: add wtforms instead of manual handling
@bp.route('/search/', methods=['GET', 'POST'])
def search():
    """Search view"""

    # TODO: implement as singletons?
    try:
        meaning_values = Construction.contemporary_meaning.unique()
    except (ValueError, TypeError):
        meaning_values = MEANING_VALUES
    try:
        synt_functions_anchor = Construction.synt_function_of_anchor.type.enums
    except (ValueError, TypeError):
        synt_functions_anchor = SYNT_FUNCTIONS_ANCHOR

    query_args = request.args
    print(*query_args.items(), sep='\n')
    logger.debug(f"{query_args}")

    # a GET request with
    #   - no parameters or unfilled parameters
    #   - or a `no-search` flag (usually after linking from construction page)
    if (request.method != 'POST'
        and (not (request.args and any(val for key, val in query_args.items()))
             or query_args.get('no-search') == '1')
    ):
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

    with current_app.engine.connect() as conn:
        results = conn.execute(stmt).mappings().all()

    for row in results:
        print(type(row))
        print(row)
        # print(row._fields)
        # for field in row:
        #     print(vars(field))
        # print(row._asdict())
    row_id2data = group_rows_by_construction(results)

    print(row_id2data)
    print("formula" in query_args, query_args, sep="\n")

    return render_template(
        'search.html',
        title='Поиск: результаты',
        year=datetime.now().year,
        meaning_values=meaning_values,
        synt_functions_anchor=synt_functions_anchor,
        form_input=request.form,
        results=row_id2data,
        n_param_results=len(results),
        query=query_args
    )


@bp.route('/simple-search/')
def simple_search():
    return render_template(
        'search_simple.html',
        # '/errors/404.html',
        # message="Page under construction"
    ), 404
