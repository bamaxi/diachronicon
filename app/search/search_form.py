import typing as T

from markupsafe import (
    escape,
    Markup
)

from flask import render_template, abort, request, redirect
from wtforms.widgets import html_params as widgets_html_params
from wtforms import (
    Form,
    Field
)

from jinja2 import Environment, select_autoescape
env = Environment(
    autoescape=select_autoescape()
)


def html_to_file(html, filename="search_form.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)


class DataList:
    """datalist widget for html rendering"""
    option_attrs2required = {"label": False, "value": True, "selected": False}

    def __init__(
        self, name: str, literal_options: T.List[T.Union[int, str]] = None,
        with_attr_options: T.List[T.Dict[str, T.Union[str, int]]] = None,
    ):
        self.name = name
        self.with_atrr_options = []
        self.literal_options = []

        if with_attr_options:
            for opt in with_attr_options:
                assert opt.get("value"), f"`value` required for options, found: {opt}"

            self.with_atrr_options = with_attr_options
            self.are_options_attr = True
        elif literal_options:
            self.literal_options = literal_options
            self.are_options_attr = False
        else:
            raise ValueError(f"one of `literal_options` or `with_atrr_options`"
                             f"must be provided")

    def __str__(self):
        return self()

    def __html__(self):
        return self()

    def __call__(self, **kwargs):
        option_htmls = []

        if self.are_options_attr:
            for opt in self.with_atrr_options:
                atrrs_str = widgets_html_params(**opt)
                option_htmls.append(f"<option {atrrs_str}></option>")
        else:
            for opt in self.literal_options:
                option_htmls.append(f'<option value="{opt}"></option>')

        return Markup("\n".join(option_htmls))


def render():
    datalist = DataList("order-options", with_attr_options= [
        {"value": 1, "label": "первый", "selected": True},
        {"value": -2, "label": "предпоследний"},
        {"value": -1, "label": "последний"},
    ])

    print(datalist)

    print(env.from_string("{{ datalist() }}",
                          globals={"datalist": datalist}))


render()
