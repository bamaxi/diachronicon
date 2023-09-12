import typing as T
from typing import Any

from markupsafe import (
    escape,
    Markup
)

from flask import render_template, abort, request, redirect
from wtforms.widgets import html_params as widgets_html_params, Option, Select
from wtforms import (
    Form,
    Field,
    Label
)
import wtforms

from jinja2 import Environment, select_autoescape
env = Environment(
    autoescape=select_autoescape()
)


INDENT = " " * 2
ATTRS_SEP = " "


class SupportsStr(T.Protocol):
    def __str__(self) -> str: ...

class Widget(T.Protocol):
    def __str__(self) -> str: ...
    def __html__(self) -> str: ...
    def __call__(self, *args: Any, **kwds: Any) -> str: ...


def html_to_file(html, filename="search_form.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)


class DataList:
    """datalist widget for html rendering"""
    option_attrs2required = {"label": False, "value": True, "selected": False}

    def __init__(
        self, id: str, literal_options: T.List[T.Union[int, str]] = None,
        with_attr_options: T.List[T.Dict[str, T.Union[str, int]]] = None,
    ):
        self.id = id
        self.with_atrr_options = []
        self.literal_options = []

        if with_attr_options is not None:
            for opt in with_attr_options:
                assert opt.get("value"), f"`value` required for options, found: {opt}"

            self.with_atrr_options = with_attr_options
            self.are_options_attr = True
        elif literal_options is not None:
            self.literal_options = literal_options
            self.are_options_attr = False
        else:
            raise ValueError(f"one of `literal_options` or `with_atrr_options`"
                             f"must be provided")

    def __str__(self):
        return self()

    def __html__(self):
        return self()

    def __call__(self, base_indent="", **kwargs):
        option_htmls = []

        if self.are_options_attr:
            for opt in self.with_atrr_options:
                atrrs_str = widgets_html_params(**opt)
                option_htmls.append(f"<option {atrrs_str}></option>")
        else:
            for opt in self.literal_options:
                option_htmls.append(f'<option value="{opt}"></option>')

        # opening recieves indent in parent `str.join()`
        datalist_opening = f'<datalist id="{self.id}">'
        options_text = join_newline_indent(
            option_htmls, first_with_newline=False, indent_symb=base_indent+INDENT
        )
        datalist_closing = f'{base_indent}</datalist>'

        return Markup("\n".join([datalist_opening, options_text, datalist_closing]))


# def make_fieldset(cls: T.Type['Fieldset']) -> Fieldset:
#     ...


# class Fieldset:
#     """fieldset widget for html rendering"""

#     def __init__(
#         self, name: str, legend: str, items: T.List[str],
#         kwargs: T.Dict[str, T.Any]
#     ) -> None:
#         contents = []
#         if legend:
#             legend_html = f"<legend>{legend}</legend>"
#             contents.append(legend_html)
        
#         attrs_str = widgets_html_params(kwargs)
        
#         fieldset_opening = f'<fieldset{(" " + attrs_str) if attrs_str else ""}>'

#         fieldset_closing = "<fieldset>"

    

def join_newline_indent(
    items: T.List[str], first_with_newline=False, first_with_indent=True,
    last_with_indent=True, indent_symb: str=INDENT, newline_symb: str="\n"
):
    if not items:
        return ""
    
    first_item, *items_except_first = items
    if not first_with_newline:
        first_item_str = f"{indent_symb}{first_item}"
        items_except_first_str = f"{newline_symb}{indent_symb}".join([""] + items_except_first)
        return "".join([first_item_str, items_except_first_str])
    
    return f"{newline_symb}{indent_symb}".join([""] + items)


def add_indent(item: T.Union[str, Markup, Field, Widget], indent="") -> str:
    if isinstance(item, (str, Markup)):
        return f"{indent}{item}"
    else:
        return item(base_indent=indent)


def format_attrs_simple(attrs: T.Dict[str, SupportsStr], attrs_sep: str=ATTRS_SEP):
    return attrs_sep.join([f'{key}="{value}"' for key, value in attrs.items()])


def convert_underscore(s: str, to: str="-"):
    return s.replace("_", "-")


def format_attrs_partial_order(
    attrs: T.Dict[str, SupportsStr],
    order: T.Iterable[str]=["type", "class", "id", "name", "list", "value"],
    attrs_sep: str=ATTRS_SEP,
):
    """Format using `order` for attrs specified there and alphabetical order for others"""
    # consistent with `wtforms.widgets.html_params` as of `3.0`
    attrs = {(convert_underscore(key) if key[:5] in ("aria-", "data-") else key): val
             for key, val in attrs.items()}
    
    preordered_attrs: T.Dict[str, SupportsStr] = {}

    for key in order:
        if key in attrs:
            preordered_attrs[key] = attrs.pop(key)
    
    # if other_attrs:
    #     return f"{format_attrs_simple(preordered_attrs)} {widgets_html_params(**other_attrs)}"
    # return f"{format_attrs_simple(preordered_attrs)}"
    return f"{format_attrs_simple(preordered_attrs)} {widgets_html_params(**attrs)}"


def make_default_attrs(widget: Widget, field: wtforms.Field, **kwargs) -> T.Dict[str, T.Any]:
    attrs = {}
    for maybe_widget_attr in ("input_type", "input_class"):
        if hasattr(widget, maybe_widget_attr):
            attrs[maybe_widget_attr.removeprefix("input_")] = getattr(widget, maybe_widget_attr)
    
    for maybe_field_attr in ("name", "id"):
        if hasattr(field, maybe_field_attr):
            attrs[maybe_field_attr] = getattr(field, maybe_field_attr)
    
    if field.render_kw:
        attrs.update(field.render_kw)
    attrs.update(kwargs)

    return attrs


def make_bootstrap_errors_div(field):
    error_div_opening = '<div class="error feedback-invalid">'
    error_div_closing = '</div>'
    if field.errors:
        errors = join_newline_indent([f"<li>{error}</li>" for error in field.errors])
        error_div = "\n".join([error_div_opening, errors, error_div_closing])
    else:
        error_div = error_div_opening + error_div_closing
    
    return error_div


def make_sign_options_for_param(param: str):
        # _options = [
        #     {"label": Markup("{param} это (&leqq;, &geqq; или &equals;)".format(param=param)),
        #      "value": "", "selected": True},
        #     {"label": Markup("Максимум (&leqq;)"), "value": "le"},
        #     {"label": Markup("Минимум (&geqq;)"), "value": "ge"},
        #     {"label": Markup("Ровно (&equals;)"), "value": "eq"}
        # ]
        _options = [
            ("", Markup("{param} это (&leqq;, &geqq; или &equals;)".format(param=param))),
            ("le", Markup("Максимум (&leqq;)")),
            ("ge", Markup("Минимум (&geqq;)")),
            ("eq", Markup("Ровно (&equals;)"))
        ]
        selected = ""
        return _options, selected


def render_option(value, label, selected, **kwargs):
    if value is True:
        # Handle the special case of a 'True' value.
        value = str(value)

    options = dict(kwargs, value=value)
    if selected:
        options["selected"] = True
    return Markup(f"<option {format_attrs_partial_order(options)}>{label}</option>")


class BootstrapSelectWidget:
    select_template = "<select {select_attrs}></select>"
    input_class = "form-select"

    def __str__(self) -> str: return self.__call__()
    def __html__(self) -> str: return self.__call__()

    def __call__(self, field: wtforms.SelectField, base_indent="", **kwargs) -> Markup:
        # attrs = {"class": self.input_class, "name": field.name, "aria-label": field.label.text}
        # if field.render_kw:
        #     attrs.update(field.render_kw)
        kwargs["aria-label"] = field.label.text
        attrs = make_default_attrs(self, field, **kwargs)

        selected = getattr(field, "data") or kwargs.get("selected")
        options_html = join_newline_indent(
            [f"{base_indent}{render_option(value, Markup(label), value==selected)}"
             for value, label, _ in field.iter_choices()]
        )
        
        select_opening = f"<select {format_attrs_partial_order(attrs)}>"
        select_closing = "</select>"
        return Markup("\n".join([select_opening, options_html, select_closing]))


class BootstrapCheckWidget:
    outer_div_class = "form-check"

    input_template = "<input {input_attrs}></input>"
    
    input_type = "checkbox"
    input_class = "form-check-input"

    def __str__(self) -> str: return self.__call__()
    def __html__(self) -> str: return self.__call__()
    
    def __call__(self, field: wtforms.BooleanField, base_indent="", **kwargs) -> Markup:
        # attrs = {"class": self.input_class, "name": field.name, "id": field.id,
        #          "type": self.input_type}
        # if field.render_kw:
        #     attrs.update(field.render_kw)
        attrs = make_default_attrs(self, field, **kwargs)
        input_ = self.input_template.format(input_attrs=format_attrs_partial_order(attrs))

        outer_div_attrs = format_attrs_partial_order({"class": self.outer_div_class})
        outer_div_opening = f"<div {outer_div_attrs}>"

        label = field.label(**{"class": "form-check-label"})

        error_div = make_bootstrap_errors_div(field)
        outer_div_closing = "</div>"

        return Markup("\n".join([outer_div_opening, input_, label, error_div, outer_div_closing]))


class BootstrapStringWidget:
    outer_div_class = "form-field-text"

    input_type = "text"
    input_class = "form-control"
    aria_describedby = "{id}-help"
    name = "{prefix}-{id}"

    def __init__(self, use_placeholder=True) -> None:
        self.use_placeholder = use_placeholder

    def __str__(self) -> str: return self.__call__()
    def __html__(self) -> str: return self.__call__()

    def __call__(
        self, field: Field, label_extra_text=None,
        # prefix="c",
        cur_value=None,
        div_extra_contents: T.Optional[T.List[T.Union[str, Markup, Field, Widget]]] = None,
        **kwargs
    ) -> Markup:
        # print(f"in widget. `div_extra_contents`: {div_extra_contents}\n"
        #       f"`extra_attrs` {extra_attrs}")

        div_contents = []

        aria_describedby = self.aria_describedby.format(id=field.id)
        # input_attrs = {
        #     "type": self.input_type, "class": self.input_class,
        #     "id": field.id,
        #     "aria_describedby": aria_describedby,
        #     # "name": self.name.format(prefix=field._prefix, id=field.id),
        #     "name": field.name,
        #     **kwargs
        # }
        input_attrs = make_default_attrs(self, field, **kwargs)
        input_attrs["aria-describedby"] = aria_describedby

        if self.use_placeholder:
            input_attrs["placeholder"] = field.name

        value = field.data or cur_value
        if value:
            input_attrs["value"] = value

        input_ = f"<input {format_attrs_partial_order(input_attrs)}>"

        # label with optional extra
        label_text = field.label.text
        if label_extra_text:
            label_text += label_extra_text
        label = Label(field_id=field.id, text=label_text).__html__()

        help_div_attrs_str = format_attrs_partial_order(
            {"class": "form-text", "id": aria_describedby})
        help_div = (f"<div {help_div_attrs_str}>{field.description}</div>")
        
        error_div = make_bootstrap_errors_div(field)

        outer_div_attrs = format_attrs_partial_order({"class": self.outer_div_class})
        outer_div_opening = f"<div {outer_div_attrs}>"

        div_contents = [outer_div_opening, input_, label, help_div]
        if div_extra_contents:
            # TODO: that's a bad call...
            div_contents += [add_indent(item, INDENT) for item in div_extra_contents]
        div_contents += [error_div, "</div>"]

        return Markup(f"\n{INDENT}".join(div_contents[:-1]) + f"\n{div_contents[-1]}")
    

class BoostrapSelectField(wtforms.SelectField):
    widget = BootstrapSelectWidget()

class BootstrapBooleanField(wtforms.BooleanField):
    widget = BootstrapCheckWidget()

class BootstrapStringField(wtforms.StringField):
    widget = BootstrapStringWidget()

class BootstrapIntegerField(wtforms.IntegerField):
    widget = BootstrapStringWidget(use_placeholder=False)


def render_datalist():
    datalist = DataList("order-options", with_attr_options= [
        {"value": 1, "label": "первый", "selected": True},
        {"value": -2, "label": "предпоследний"},
        {"value": -1, "label": "последний"},
    ])

    print(datalist)

    print(env.from_string("{{ datalist() }}",
                          globals={"datalist": datalist}))
    

def render_text():
    # field = wtforms.StringField(
    #     label="Формула", description="тестовое описание", name="formula",
    #     id="formula-1-", widget=BootstrapStringWidget
    # )

    class MyForm(wtforms.Form):
        formula = wtforms.StringField(
            label="Формула", description="тестовое описание", name="formula",
            id="formula-1", widget=BootstrapStringWidget()
        )

    # print(field(cur_value="np*"))
    form = MyForm()

    print(form.formula())


def render_fieldset():
    class MyForm(wtforms.Form):
        # general
        constructionId = BootstrapStringField(
            label="id", description="id конструкции",
            name="id", _prefix="c-",
            id="constructionId"
        )
        formula = BootstrapStringField(
            label="Формула", description="формула конструкции в последний период",
            name="formula", _prefix="c-",
            id="formula-1"
        )

        _meaning_datalist_id = "meaning_values"
        _meaning_datalist = DataList(
            id=_meaning_datalist_id,
            literal_options=["maximizer", "minimizer", "other"])
        meaning = BootstrapStringField(
            label="Значение", render_kw=dict(
                label_extra_text = Markup('<span class="symbol symbol-form symbol-logic"></span>'),
                div_extra_contents = [_meaning_datalist],
                list = _meaning_datalist_id,
            ), description="значение конструкциии в последний период",
            name="meaning", _prefix="c-",
            id="meaning"
        )

        constraint_type = BoostrapSelectField(
            label="Тип ограничения",
            choices=[("", "Выберите"), ("synt", "Синтаксическое"), ("sem", "Семантическое"),
                     ("", "Любое")]
        )

    form = MyForm()
    print(form.constructionId())
    print(form.formula())
    print(form.meaning())
    print(form.constraint_type())


def render_multifields():
    class ChangeForm(wtforms.Form):
        formula = BootstrapStringField(
            label="Формула", description="формула конструкции в этот период",
            name="stage", _prefix="ch-",
            id="stage"
        )
        period_duration = BootstrapStringField(
            label="Длительность периода",
            id="duration"
        )

    # class Changes(wtforms.Form):
    #     changes = wtforms.FieldList(wtforms.FormField(ChangeForm), min_entries=3)

    class ConstructionForm(wtforms.Form):
        # changes = wtforms.FormField(Changes)
        changes = wtforms.FieldList(wtforms.FormField(ChangeForm), min_entries=3)
        formula = BootstrapStringField(
            label="Формула", description="формула конструкции в последний период",
            name="formula", _prefix="c-",
            id="formula"
        )

    class MultiConstructionForm(wtforms.Form):
        constructions = wtforms.FieldList(wtforms.FormField(ConstructionForm), min_entries=2)


    # myform = Changes()
    # print(myform.changes())
    # print(myform.formula())

    myform = MultiConstructionForm()
    # print(myform.constructions())

    # print(render_template())

def test_boolean():
    class ConstructionAndGeneralForm(Form):
        constructionId = BootstrapStringField(
            label="id конструкции", name="constructionId",
        )
        formula = BootstrapStringField(
            label="Формула", name="formula",
        )

        _meaning_datalist_id = "meaning_values"
        # _meaning_values = safe_get(Construction.contemporary_meaning.unique) or MEANING_VALUES
        # _meaning_values = ["вау",  "вцщк 2"]
        _meaning_values = []
        _meaning_datalist = DataList(
                id=_meaning_datalist_id,
                literal_options=_meaning_values)
        meaning = BootstrapStringField(
            label="Значение", name="meaning",
            render_kw=dict(
                # label_extra_text = Markup('<span class="symbol symbol-form symbol-logic"></span>'),
                div_extra_contents = [_meaning_datalist],
                list = _meaning_datalist_id,
            ), description="значение конструкциии в последний период",   
        )

        in_rus_constructicon = BootstrapBooleanField(
            label="Есть в конструктиконе", name="in_rus_constructicon"
        )

        _num_changes_sign_options, selected = make_sign_options_for_param("Количество")
        num_changes_sign = BoostrapSelectField(
            _num_changes_sign_options[0][1], name="num_changes_sign", 
            choices=_num_changes_sign_options,
            render_kw=dict(selected=selected))
        num_changes = BootstrapStringField(
            label="Количество изменений", name="num_changes",
        )

    form = ConstructionAndGeneralForm()
    print(form.constructionId())
    print(form.formula())
    print(form.meaning())
    print(form.in_rus_constructicon())
    print(form.num_changes_sign())


def test_anchor():
    class AnchorForm(Form):
        _synt_functions_datalist_id = "synt_function_of_anchor_values"
        # _synt_functions_anchor = safe_get(
        #     lambda: Construction.synt_function_of_anchor.type.enums) or SYNT_FUNCTIONS_ANCHOR
        _synt_functions_anchor = ["фф", "алфт"]
        _synt_functions_datalist = DataList(
            id=_synt_functions_datalist_id,
            literal_options=_synt_functions_anchor)
        synt_functions_of_anchor = BootstrapStringField(
            label="Синт. функция якоря", name="synt_function_of_anchor",
            render_kw=dict(div_extra_contents = [_synt_functions_datalist],
                        list=_synt_functions_datalist_id)
        )

        anchor_schema = BootstrapStringField(label="Схема якоря", name="anchor_schema")
        anchor_ru = BootstrapStringField(label="Якорь (рус.)", name="anchor_ru")

    form = AnchorForm()
    print(form.synt_functions_of_anchor())
    print(form.anchor_schema())
    print(form.anchor_ru())

# render_datalist()
# render_text()
# render_fieldset()
# render_multifields()
# test_boolean()
test_anchor()
