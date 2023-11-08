import typing as T
from datetime import datetime

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
import wtforms
import wtforms.validators
from flask import current_app
from flask import render_template, abort, request, redirect, url_for
from flask_wtf import FlaskForm

from app.models import (
    Construction,
    Change,
    GeneralInfo,
    Constraint,
    FormulaElement,
    ConstructionVariant,
    DBModel,
    Model2Field2Val
)
import app.database

from app.main import bp
from app.search.search_form import (
    make_sign_options_for_param,
    make_options_from_values,
    DataList,
    BootstrapBooleanField,
    BoostrapSelectField,
    BootstrapStringField,
    BootstrapIntegerField,
)
from app.search.query_sqlalchemy import (
    default_sqlquery,
    SQLQuery,
)
from app.utils import (
    find_unique
)




class SimpleSearchForm(FlaskForm):
    _construction_values = find_unique(Construction, "formula")
    _construction_options, _selected = make_options_from_values(
        _construction_values, "конструкцию")
    formula = BoostrapSelectField(
        _construction_options[0][1], name="formula", 
        choices=_construction_options,
        render_kw=dict(selected=_selected))


# @bp.route('/simple-search/')
def simple_search():
    # try:
    #     with current_app.engine.connect() as conn:
    #         all_formulas = conn.execute(select(Construction.formula)).scalars().all()
    # except:
    #     all_formulas = []
    simple_form = SimpleSearchForm()

    if simple_form.is_submitted():
        print(f'FORM SUBMITTED')

        queried_formula = simple_form.data["formula"]
        stmt = select(Construction).where(Construction.formula == queried_formula)
        with current_app.engine.connect() as conn:
            results = conn.execute(stmt).mappings().all()

        return render_template(
            'search_simple.html',
            # '/errors/404.html',
            # message="Page under construction"
            _form=simple_form,
            results=results,
            # items=all_formulas,
        )

    return render_template(
            'search_simple.html',
            _form=simple_form,
        )


@bp.route('/')
@bp.route('/index/')
@bp.route('/main/')
def main():
    simple_form = SimpleSearchForm()

    if simple_form.is_submitted():
        print(f'FORM SUBMITTED')

        queried_formula = simple_form.data["formula"]
        stmt = select(Construction).where(Construction.formula == queried_formula)
        with current_app.engine.connect() as conn:
            results = conn.execute(stmt).mappings().all()

        return render_template(
            'main.html', title='Главная',
            _form=simple_form,
            results=results,
        )
    
    return render_template(
        'main.html', title='Главная',
        _form=simple_form,
    )


@bp.route('/simple-form', methods=["POST"])
def receive_simple():
    simple_form = SimpleSearchForm()
    print("in receive")
    print(simple_form.is_submitted(), simple_form.validate_on_submit())

    queried_formula = simple_form.data["formula"]
    stmt = select(Construction).where(Construction.formula == queried_formula)
    print(stmt)
    with current_app.engine.connect() as conn:
        results = conn.execute(stmt).mappings().all()

    print(results)

    return render_template(
        'main.html', title='Главная (результаты)',
        _form=simple_form,
        results=results,
        query=simple_form,
    )


@bp.route("/about")
def about():
    return render_template(
        '/errors/404.html',
        message="Page under construction"
    )   

