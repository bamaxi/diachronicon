from typing import Literal, Union

import logging
from datetime import datetime

from sqlalchemy import (
    select,
    or_,
    and_
)
from sqlalchemy.orm import aliased

from numpy import array
import pandas as pd

import plotly
import plotly_express as px
import plotly.graph_objects as go

from flask import current_app
from flask import render_template, abort, request, redirect

from . import bp
from app.models import (
    Construction,
    Change,
    GeneralInfo,
    Constraint,
    FormulaElement
)

from config import Config


# from app.utils import pretty_log
# from ..testing.profiling import profiled

logger = logging.getLogger()

CHANGE_COLUMNS = [str(col).removeprefix('change.')
                  for col in Change.__table__.columns]

pd_na = pd.NA


COLORS = {
    'synt': "#636efa",
    'sem':  "#EF553B"
}


class NoDate:
    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False


NO_DATE = NoDate()


def new_plot_single_const_changes(
        data: dict[str, [dict[str, list[datetime]]]],
        no_last_date_option: Literal['current' or 'largest'] = 'largest'
):
    assert 1 <= len(data) <= 2 and ('synt' in data or 'sem' in data)

    # make a filler to be used instead of unmarked last-attested dates
    if no_last_date_option == 'largest':
        LAST_DATE = max(_date for level in data
                        for _date in data[level]['last_attested'])
    elif no_last_date_option == 'current':
        LAST_DATE = datetime(datetime.now().year, 1, 1)
    else:
        raise ValueError

    for level, level_data in data.items():
        last_dates = level_data['last_attested']
        first_dates = level_data['first_attested']

        corrected_last_dates = []

        for i, last_date_ in enumerate(last_dates):
            if last_date_ is NO_DATE and first_dates[i] is NO_DATE:
                # remove first_date and don't add last_date
                first_dates.pop(i)
                continue
            elif last_date_ is NO_DATE:
                last_date_ = LAST_DATE

            corrected_last_dates.append(last_date_)

        data[level]['last_attested'] = corrected_last_dates

    print(LAST_DATE, data, last_dates, corrected_last_dates, sep='\n')

    fig = go.Figure(
        layout={
            'barmode': 'overlay',
            'legend': {'title': {'text': 'level'}, 'tracegroupgap': 0},
            'margin': {'t': 60},
            # 'template': '...',
            'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'type': 'date', 'title': {'text': 'year'}},
            'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], }  # 'title': {'text': 'construction_id'}}
        }
    )

    for i, (level, level_data) in enumerate(data.items()):
        first_dates = level_data['first_attested']

        x = []
        for j, last_date_ in enumerate(level_data['last_attested']):
            first_date_ = first_dates[j]
            if last_date_ is NO_DATE and first_date_ is NO_DATE:
                continue

            x.append((last_date_ - first_date_).total_seconds() * 1000)

        fig.add_bar(**{
            'alignmentgroup': 'True',
            'base': array(first_dates, dtype=object),
            # 'customdata': level,
            'hovertemplate': (
                'level=%{name}<br>first_attested=%{base}<br>'
                'last_attested=%{x}<br>construction_id=%{y}'
                '<extra></extra>'
            ),
            'legendgroup': level,
            'marker': {'color': COLORS[level], 'opacity': 0.6},
            'name': level,
            'offset': 0.0 - i * 0.05,
            'width': 0.05,
            'offsetgroup': level,
            'orientation': 'h',
            'showlegend': True,
            'textposition': 'auto',
            'x': array(x),
            'xaxis': 'x',
            'y': array([1, 1, 1, 1], dtype='int64'),
            'yaxis': 'y'
        })

    graphJSON = str(fig.to_json())

    return graphJSON


def plot_single_const_changes(
        df: pd.DataFrame,
        no_last_date_option: Literal['current' or 'largest'] = 'largest'
):
    fig = go.Figure(
        layout={
            'barmode': 'overlay',
            'legend': {'title': {'text': 'level'}, 'tracegroupgap': 0},
            'margin': {'t': 60},
            # 'template': '...',
            'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'type': 'date', 'title': {'text': 'year'}},
            'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0], }#'title': {'text': 'construction_id'}}
        }
    )

    fig.add_bar(**{
        'alignmentgroup': 'True',
        'base': array(['1850', '1831', '1857', '1873'], dtype=object),
        'hovertemplate': ('level=%{name}<br>first_attested=%{base}<br>'
                          'last_attested=%{x}<br>construction_id=%{y}'
                          '<extra></extra>'),
        'legendgroup': 'synt',
        'marker': {'color': '#636efa', 'opacity': 0.6},
        'name': 'synt',
        'offset': 0.0,
        'width': 0.1,
        'offsetgroup': 'synt',
        'orientation': 'h',
        'showlegend': True,
        'textposition': 'auto',
        'x': array([1.1360736e+12, 4.8282048e+12, 3.1553280e+11, 4.4810496e+12]),
        'xaxis': 'x',
        'y': array([1, 1, 1, 1], dtype='int64'),
        'yaxis': 'y'
    })

    fig.add_bar(**{
        'alignmentgroup': 'True',
        'base': array(['1850', '1831'], dtype=object),
        'hovertemplate': ('level=%{name}<br>first_attested=%{base}<br>'
                          'last_attested=%{x}<br>construction_id=%{y}'
                          '<extra></extra>'),
        'legendgroup': 'sem',
        'marker': {'color': '#EF553B', 'opacity': 0.6},
        'name': 'sem',
        'offset': -0.1,
        'width': 0.1,
        'offsetgroup': 'sem',
        'orientation': 'h',
        'showlegend': True,
        'textposition': 'auto',
        'x': array([1.1360736e+12, 3.1561920e+11]),
        'xaxis': 'x',
        'y': array([1, 1], dtype='int64'),
        'yaxis': 'y'
    })

    # fig = px.timeline(
    #     df, x_start="first_attested", x_end="last_attested",
    #     y="construction_id", color='level',
    #     opacity=.6,
    #                   # , hover_name="hoverName"
    #                   # # , color_discrete_sequence=px.colors.qualitative.Prism
    #                   # , opacity=.6
    #                   # , template='plotly_white'
    #                   # , color='level'
    #                   # , hover_data=['first_attested', 'last_attested']
    # )

    # print(vars(fig))
    # print(fig.data)

    # print(list(fig.data))
    # for obj in fig.data:
    #     # stage, level = obj.hovertext[0].split("|")
    #     # print(stage, level)
    #     print(obj)
    #     level = obj.name
    #     if (level == 'synt'):
    #         obj.width = 0.1
    #         obj.offset = 0.0
    #     elif (level == 'sem'):
    #         obj.width = 0.1
    #         obj.offset = -0.1
    #     print(obj)
    #     print(obj.hovertemplate)
    #
    # fig.add_bar(**{
    #     'alignmentgroup': 'True',
    #     'base': array([1850, 1831], dtype=object),
    #     'hovertemplate': ('<b>%{hovertext}</b><br>'),
    #     'hovertext': array(['3|sem', '0|sem'], dtype=object),
    #     'legendgroup': 'sem2',
    #     'marker': {'color': '#EF553B', 'opacity': 0.6},
    #     'name': 'sem2',
    #     'offsetgroup': 'sem2',
    #     'orientation': 'h',
    #     'showlegend': True,
    #     'textposition': 'auto',
    #     'x': array([1860, 2015]),
    #     'xaxis': 'x',
    #     'y': array([3, 3], dtype=object),
    #     'yaxis': 'y'
    # })

    # data = [dict(Task="Job A", Start='2007', Finish='2010'),
    #         dict(Task="Job A", Start='2008', Finish='2010'),
    #         dict(Task="Job B", Start='2004', Finish='2010'),
    #         dict(Task="Job C", Start='2009', Finish='2010')]
    #
    # df = pd.DataFrame(data)
    #
    # df['JobNum'] = ""
    # df.loc[0, 'JobNum'] = 1
    # for idx in range(1, df.shape[0]):
    #     if df.loc[idx - 1, 'Task'] == df.loc[idx, 'Task']:
    #         df.loc[idx, 'JobNum'] = df.loc[idx - 1, 'JobNum'] + 1
    #     else:
    #         df.loc[idx, 'JobNum'] = 1
    #
    # df['hoverName'] = df.apply(lambda x: x['Task'] + "|" + str(x['JobNum']), axis=1)
    #
    # print(df.info())
    # print(df['Start'])
    # print(df['Finish'])

    # fig = px.timeline(df
    #                   , x_start="Start"
    #                   , x_end="Finish"
    #                   , y="Task"
    #                   , hover_name="hoverName"
    #                   # , color_discrete_sequence=px.colors.qualitative.Prism
    #                   , opacity=.7
    #                   , template='plotly_white'
    #                   , color='JobNum'
    #                   , hover_data=['Start', 'Finish']
    #                   )
    #
    # for obj in fig.data:
    #     Task, JobNum = obj.hovertext[0].split("|")
    #     if (int(JobNum) == 1):
    #         obj.width = 0.1
    #         obj.offset = 0.05
    #     elif (int(JobNum) == 2):
    #         obj.width = 0.1
    #         obj.offset = -0.05

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = str(fig.to_json())

    return graphJSON


def parse_year(year: Union[str, int, None], left_bias=0.0):
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
        graphJSON = new_plot_single_const_changes(changes_data)
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

    # return render_template(
    #     'index.html',
    #     title='Главная',
    #     year=datetime.now().year,
    #     res_id=res.id,
    #     construction=res,
    #     graphJSON=graphJSON
    # )

MAPPING = {
    'c': Construction,
    'constraint': Constraint,
    # '': Change,
    # '': GeneralInfo,
}

html_name2table_name = {
    'meaning': 'contemporary_meaning'
}


def make_basic_formula_query(stmt, model, value):
    return stmt.where(getattr(model, 'formula').like(f"%{value}%"))


def make_byelem_formula_query(stmt, model, value):
    elements = value.split(' ')
    print(elements)

    element_tables = [aliased(FormulaElement) for i in range(len(elements))]

    # params = {}

    stmt = stmt.where(getattr(model, 'id') == element_tables[0].construction_id)

    for i, element_value in enumerate(elements):
        cur_elem_table = element_tables[i]

        # TODO: asterisk instead of element
        if i != 0:
            stmt = stmt.where(
                cur_elem_table.construction_id == element_tables[0].construction_id,
                cur_elem_table.order == element_tables[i - 1].order + 1,
                # or_(cur_elem_table.order == element_tables[i-1].order + 1,
                #     and_(cur_elem_table.is_optional,
                #          cur_elem_table.order == element_tables[i-1].order + 2)
                # )
            )

        # params[f'gloss{i}'] = value  # or text(value)
        corrected_val = element_value.replace('*', '%')
        stmt = stmt.where(getattr(cur_elem_table, 'value').ilike(corrected_val))

    return stmt


def make_formula_query(stmt, model, value):
    if '*' in value:
        return make_byelem_formula_query(stmt, model, value)
    return make_basic_formula_query(stmt, model, value)


param2query_maker = {
    # 'formula': make_formula_query,
    'formula': make_formula_query,
    'element': make_basic_formula_query
}

# TODO: опционально пропускать при поиске по элементам те, что в скобках

def build_query(items, parts_sep='-', ready_only=False):
    """
    Collects html params into database query
    :param items:
    :param parts_sep:
    :param ready_only:
    :return:
    """
    # stmt = None
    # if ready_only:
    #     stmt = select()

    items_by_model = {}

    for key, value in items:
        if not value:
            continue

        logger.debug(key, value)
        key_model_part, key_param_part = key.split(parts_sep, maxsplit=1)
        # new
        key_param_part = html_name2table_name.get(key_param_part) or key_param_part

        # there could be multiple constraints or changes coded
        #   in html as `constraint-3-element` for example
        if parts_sep not in key_param_part:
            items_by_model.setdefault(MAPPING[key_model_part], {}
                                      )[key_param_part] = value
            continue

        i, key_param = key_param_part.split(parts_sep, maxsplit=1)
        model_list = items_by_model.setdefault(MAPPING[key_model_part], [])

        i = int(i)
        if len(model_list) < i:
            model_list.append({key_param: value})
        else:
            model_list[i][key_param] = value

    if ready_only:
        items_by_model[Construction]['status'] = 'ready'

    print(items_by_model)
    if not items_by_model:
        return

    # make the query itself
    stmt = select(*[model for model in items_by_model])
    for model, params_values in items_by_model.items():
        if not isinstance(params_values, list):
            for param, val in params_values.items():
                print(model, param, val)
                if param in param2query_maker:
                    stmt = param2query_maker[param](stmt, model, val)
                else:
                    # a simple equality testing
                    stmt = stmt.where(getattr(model, param) == val)
        else:
            # code for aliases? How should multiple constraints or multiple
            #   changes be connected?
            pass

    print(stmt)

    return stmt


@bp.route('/search/', methods=['GET', 'POST'])
def search():
    meaning_values = current_app.db_session.execute(
        select(Construction.contemporary_meaning)
    ).scalars().all()

    synt_functions_anchor = Construction.synt_function_of_anchor.type.enums

    query_args = list(request.args.items())
    print(*query_args, sep='\n')
    logger.debug(f"{query_args}")

    # a GET request with no parameters or unfilled parameters
    if (request.method != 'POST'
        and not (request.args and any(val for key, val in query_args))
    ):
        logger.debug(f"no query, returning clear form")

        return render_template(
            'search.html',
            title='Поиск',
            year=datetime.now().year,
            meaning_values=meaning_values,
            synt_functions_anchor=synt_functions_anchor,
        )

    # if request.method == 'POST' or request.method == 'GET' and request.args:
    print(f'in conditional')
    # print(*vars(request).items(), sep='\n')
    # print(*query_args, sep='\n')

    print(request.form)
    print(request.data)

    # logger.debug(f"{request.args}")

    stmt = build_query(query_args)

    results = current_app.db_session.execute(stmt)

    # print(results, results.scalars().all())

    return render_template(
        'search.html',
        title='Поиск: результаты',
        year=datetime.now().year,
        meaning_values=meaning_values,
        synt_functions_anchor=synt_functions_anchor,
        form_input=request.form,
        results=results.scalars().all(),
        query=request.args
    )


@bp.route('/simple-search/')
def simple_search():
    return render_template(
        '/errors/404.html',
        message="Page under construction"
    ), 404
