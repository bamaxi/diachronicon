import typing as T
from typing import Tuple, List, Dict, Union, Type, Optional

from datetime import datetime
import logging

from flask import current_app
from flask import render_template, abort, request, redirect
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    selectinload,
    joinedload,
    Session
)

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
    ConstructionChangesPlot,
    ConstructionSequentialChangesPlot,
)


logger = logging.getLogger(f"diachronicon.{__name__}")
# logger.setLevel(logging.ERROR)
# logger.handlers.clear()
logger.addHandler(logging.StreamHandler())
# logger.addHandler(logging.NullHandler())


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


def prepare_graph_data(changes, skip_empty=True):
    """Update dates and

    :param changes:
    :return:
    """
    changes_data = {}
    print("changes:", changes)

    for change in changes:
        level_data = changes_data.setdefault(change.level, {})
        presence = {}

        for field in ('first_attested', 'last_attested'):
            year = parse_year(getattr(change, field))
            value = datetime(year, 1, 1) if year else NO_DATE

            # level_data = changes_data.setdefault(change.level, {})
            presence[field] = value != NO_DATE
            level_data.setdefault(field, []).append(value)

        if skip_empty and not any(present for present in presence.values()):
            for field in ('first_attested', 'last_attested'):
                level_data[field].pop()

    return changes_data


# def is_dict_empty(d: T.Dict[str, T.Any]) -> bool:
#     res = True
#     for key, val in d.items():
#         if isinstance(val, dict):
#             _res = is_dict_empty(val)
#             res |= _res
#         elif isinstance(val, dict):
#             for item in val:
                


@bp.route('/item/<int:index>/')
@bp.route('/construction/<int:index>/')
def construction(index: int):
    print(index, type(index))
    index = int(index)

    stmt = select(Construction, Change).join(Change).options(
        # joinedload(Construction.changes),
        # joinedload(Construction.general_info)
        selectinload("*"),
        selectinload(Change.previous_changes),
        selectinload(Change.next_changes),
    ).where(
            Construction.id == index
    )
    # .options(
    #     joinedload(Change.previous_changes),
    # )
    # stmt = select(Construction).where(Construction.id == index).options(
    #     joinedload("*")
    # )
    # logger.debug(f"built query: {stmt}")
    print(f"built query: {stmt}")

    with Session(current_app.engine) as session:
        # results = conn.execute(stmt).mappings().all()
        res_ = session.execute(stmt).scalars()

        # session = current_app.db_session
        # res_ = session.execute(stmt)

        logger.debug(f"found res: {res_}")
        print(res_)

        construction = res_.first() or abort(404)
        # construction = construction[0]
        print(type(construction), construction)
        # print(vars(construction))
        # print(construction.Construction)

        # logger.debug(construction)
        print(construction)

    title = (getattr(getattr(construction, "general_info", object), "name", None)
             or construction.formula)
    context = dict(
        title=f"Конструкция '{title}'",
        year=datetime.now().year,
        res_id=construction.id,
        construction=construction,  
        graphJSON=None,
        networkJSON=None
    )

    # title = f"Конструкция '{construction.general_info.name}'"
    # print(title)

    # res_id = construction.id
    # print(res_id)

    # context = dict(
    #     title=title,
    #     year=datetime.now().year,
    #     res_id=res_id,
    #     construction=construction,
        # graphJSON=None,
        # networkJSON=None,
    # )
    # context = dict(graphJSON=None, networkJSON=None)

    print("preparing changes")
    try:
        print("preparing changes")
        changes_data = prepare_graph_data(construction.changes)
        

        logger.debug(f"{changes_data}")
        print(changes_data)

        if changes_data:
            graph = ConstructionChangesPlot.from_elements(changes_data)
            print(graph.bars)

            graphJSON = str(graph.to_plotly_json())
            context.update(dict(graphJSON=graphJSON))
            # graphJSON = new_plot_single_const_changes(changes_data)
            # graphJSON = super_new_plot_single_const_changes(changes_data)

        if construction.changes:
            network = ConstructionSequentialChangesPlot.from_elements(construction.changes)

    except Exception as e:
        print(f"exception at preparation: {e}")

    print(f"about to render `{index}`")

    construction.set_changes_one_based()
    print(construction.changes, construction.changes[0], construction.changes[0].next_changes,
          construction.changes[-1], construction.changes[-1].previous_changes,
          sep="\n"
    )

    page = render_template('construction.html',  **context)
    return page
