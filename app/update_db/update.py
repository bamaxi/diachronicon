import argparse
import logging
from typing import (
    Type, Tuple, List, Dict, Union, Callable, Iterator,
    Literal, Any)

from openpyxl import load_workbook

from ..models import (
    Construction,
    ConstructionVariant,
    GeneralInfo,
    Change,
    Constraint,
    FormulaElement
)


logging.basicConfig(handlers=(logging.StreamHandler(),))
print(__name__)
logger = logging.getLogger(__name__)


ORIG_SHEET_NAME2DB_TABLE_NAME = {
    "cnstruct": "construction",
    "gen_inf": "general_info",
    "ch": "changes",
    "cnstraint": "constraints",
}


SHEET_TO_CLASS = {
    "construction": Construction,
    "general_info": GeneralInfo,
    "changes": Change,
    "constraints": Constraint,
}

COLUMNS_CORRECTION = {
    "general_info": {
        "construction_name": "name",
    },
    "construction": {
        "construction_id": "id",
        "in_Russian_Constructicon": "in_rus_constructicon",
        "number_in_Russian_Constructicon": "rus_constructicon_id",
        "constructicon_morphosyntags": "morphosyntags",
        "constructicon_semantags": "semantags",
    },
    "constraints": {
        # "constraint_id": "id",
        "syntactic_constraints": "syntactic",
        "semantic_constraints": "semantic",
    },
    "changes": {
        "change_id": "id",
        "part_of_construction_changed": "stage",
        "first_entry": "first_attested",
        "last_entry": "last_attested",
    }
}


class EOF(object):
    ...


def read_until(
    formula_it: Iterator, finish_at_predicate: Callable[[str], bool]
) -> Tuple[str, Union[str, EOF]]:
    res = []
    while True:
        next_ = next(formula_it, EOF)
        if finish_at_predicate(next_):
            return "".join(res), next_
        res.append(next_)


def tokenize_formula(
    formula: str, elems_sep: str = " ",
    span_start: str = "(", span_end: str = ")",
    are_span_symbs_optionality_symb=True,
) -> List[Dict]:
    """Tokenizes formula into word or span"""
    SPECIAL = [elems_sep, span_start, span_end, EOF]

    parts = cur_part = []
    queue = [parts]

    formula_it = iter(formula)
    symbol = ""

    while True:
        symbol, prev = next(formula_it, EOF), symbol

        # print("after read", symbol, prev, cur_part, parts, queue, sep="\n  ")

        if symbol not in SPECIAL:
            cur_element, special = read_until(formula_it, lambda symbol: symbol in SPECIAL)

            cur_part.append({"val": symbol + cur_element})
            symbol, prev = special, symbol

        if symbol == span_start:
            cur_part = []
            queue.append(cur_part)
        elif symbol == span_end:
            # print("span_end before append", symbol, prev, cur_part, parts, queue, sep="\n  ")
            # parts.append({"type": "maybe_span", "parts": queue.pop()})
            cur_result = {"type": "maybe_span", "val": queue.pop()}
            cur_part = queue[-1]
            cur_part.append(cur_result)
            # print("span_end after append and cur_part", symbol, prev, cur_part, parts, queue, sep="\n  ")
        elif symbol is EOF:
            # print("EOF", symbol, prev, cur_part, parts, queue, sep="\n  ")
            break

    return parts


def flatten_span(
    span_token_values: List[Dict[str, Any]], depth=1, order=0
) -> List[Dict[str, str]]:
    flattened_token_list = []

    if len(span_token_values) == 1:
        tok_desc = {"value": span_token_values[0]["val"], "is_optional": True}
        if depth > 1:
            tok_desc["depth"] = depth - 1
        return [tok_desc]
    
    for tok in span_token_values:
        if tok.get("type") == "maybe_span":
            flattened_token_list.extend(flatten_span(tok["val"], depth=depth + 1))
        else:
            flattened_token_list.append({"value": tok["val"], "depth": depth,
                                         "is_optional": False})

    return flattened_token_list


def parse_formula(
    formula: str, el_variants_sep="/",
) -> List[Dict]:
    elements = []
    order = 0

    tokens = tokenize_formula(formula)
    for token in tokens:
        if token.get("type") == "maybe_span":
            span_elements = flatten_span(token["val"])

            for _order, span_element in enumerate(span_elements, order):
                span_element["order"] = _order
            order = _order + 1

            elements.extend(span_elements)
        else:
            elements.append({"value": token["val"], "order": order})
            order += 1

    return elements


# TODO: special processing for NP (=NP-nom) ?
def parse_formula_old(
        formula: str,
        el_variants_sep="/",
) -> List[Dict]:
    data = []

    # TODO: improve tokenization to take spans into account
    for i, element in enumerate(formula.split(" ")):
        self_result_elements = []

        has_brackets = any(br in element for br in ("(", ")"))
        if has_brackets:
            element = element.strip("()")

        has_variants = el_variants_sep in element
        if has_variants:
            actual_elements = element.split(el_variants_sep)
            first_element_data = {
                "value": actual_elements[0], "order": i,
                "is_optional": has_brackets, "has_variants": has_variants
            }
            self_result_elements.append(first_element_data)
            self_result_elements.extend([
                {"value": variant_el, "order": i, "is_optional": has_brackets}
                for variant_el in actual_elements[1:]
            ])
        else:
            self_result_elements = [
                {"value": element, "order": i, "is_optional": has_brackets}]

        # TODO: special parsing / saving of nom nps (simply `n` / `np`)

        data.extend(self_result_elements)

    return data


def fix_construction_id(construction_id: str):
    if isinstance(construction_id, int):
        return construction_id

    construction_id = construction_id.replace(".", "0")
    construction_id = construction_id.replace("?", "9")
    if "(" in construction_id and ")" in construction_id:
        num = construction_id[:construction_id.index("(")]
        group = construction_id[construction_id.index("(")+1:construction_id.index(")")]
        return int(group+num)
    else:
        print(construction_id)
        raise ValueError


def fix_values(
        phrase_dict: Dict[str, Union[str, int, None]],
        model_class: Type[Union[Construction, GeneralInfo, Change, Constraint]]
):
    if model_class is Construction:
        phrase_dict["id"] = fix_construction_id(phrase_dict["id"])
    elif "construction_id" in phrase_dict:
        phrase_dict["construction_id"] = fix_construction_id(phrase_dict["construction_id"])

    return phrase_dict


def get_formula_element_variants(variation_val: str) -> Dict[str, List[str]]:
    elem2variants = {}

    for single_variation_desc in variation_val.split("\n"):
        if not (":" in single_variation_desc and "," in single_variation_desc):
            continue
        if (":" in single_variation_desc) ^ ("," in single_variation_desc):
            # there may be error in markup
            continue

        described_formula_el, el_variants_str = single_variation_desc.split(":")
        el_variants = [el_var.strip() for el_var in el_variants_str.split(",")]

        elem2variants[described_formula_el] = el_variants

    return elem2variants


def process_construction(
    phrase_dict: Dict[str, Union[str, int]], constr: Construction,
    formula_parser: Callable[[str], List[Dict[str, str]]] = parse_formula,
    verbose=False
) -> None:
    """Parse and add to construction object variants and their formula elements

    :param phrase_dict:
    :param constr:
    :param formula_parser:
    :param verbose:
    :return:
    """

    formula_elements = formula_parser(phrase_dict["formula"])
    formula_elements_vals = [FormulaElement(**el_data)
                             for el_data in formula_elements]
    if verbose:
        print(FormulaElement, formula_elements_vals)

    constr.formula_elements.extend(formula_elements_vals)

    main_constr = ConstructionVariant(is_main=True)
    main_constr.formula_elements.extend(formula_elements_vals)
    construction_variants_vals = [main_constr]

    construction_variants = [
        var for var in (phrase_dict["variation"] or "").split("\n")
        if var and not any(symb in var for symb in ":,")
    ]
    print(construction_variants)

    for variant in construction_variants:
        constr_variant = ConstructionVariant(formula=variant)
        variant_formula_elements = formula_parser(variant)
        variant_formula_elements_vals = [FormulaElement(**el_data)
                                         for el_data in variant_formula_elements]
        constr_variant.formula_elements.extend(variant_formula_elements_vals)
        construction_variants_vals.append(constr_variant)

    if verbose:
        print(ConstructionVariant, construction_variants_vals)

    constr.variants.extend(construction_variants_vals)


extra_processing = {
    Construction: process_construction
}


def parse(filename: str, use_old_sheet_names=True, verbose=False):
    wb = load_workbook(filename)

    # parse.idscorrection = {}

    data = []
    for sheet in wb.worksheets:
        if not use_old_sheet_names:
            corrected_sheet_name = ORIG_SHEET_NAME2DB_TABLE_NAME.get(sheet.title)
        else:
            corrected_sheet_name = sheet.title
        model_class = SHEET_TO_CLASS.get(corrected_sheet_name)
        if model_class is None:
            continue

        rows_iter = sheet.iter_rows()

        # TODO: formula versus value
        title_row = next(rows_iter)
        title_row_values = [cell.value.replace(" ", "_")
                            for cell in title_row if cell.value]
        title_row_values = [
            COLUMNS_CORRECTION.get(corrected_sheet_name, {}).get(value, value)
            for value in title_row_values
        ]
        print("title is", sheet.title, model_class, corrected_sheet_name,
              COLUMNS_CORRECTION.get(corrected_sheet_name, {}).get("change_id"),
              title_row_values)

        for row in rows_iter:
            cell_values = [cell.value.strip() if isinstance(cell.value, str) else cell.value
                           for cell in row]
            if not any(cell_values):
                continue

            phrase_dict = dict(zip(title_row_values, cell_values))
            fix_values(phrase_dict, model_class)

            if verbose:
                print(model_class, phrase_dict)

            values = model_class(**phrase_dict)

            if model_class in extra_processing:
                extra_processing[model_class](phrase_dict, values, verbose=verbose)

            data.append(values)

    if verbose:
        for item in data:
            print(item, end="\n\n")

    return data


if __name__ == "__main__":
    from ..database_utils import init_db, make_database

    parser = argparse.ArgumentParser(
        description="Append data from a suitable .xlsx (.README) to"
                    "an (existing) database that is configured for this app")

    parser.add_argument("file", metavar="F", type=str,
                        help="an existing database file path")
    parser.add_argument("--database-url", type=str, default=None,
                        help="an optional sqlalchemy uri to use a different database")
    # parser.add_argument("--database-name", type=str, default=None,
    #                     help="an optional name for the database with same scheme")
    parser.add_argument("-i", "--init", action="store_true",
                        help="whether to initialize user database")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="whether to print values as they are processed")
    parser.add_argument("-q", "--sql-quiet", action="store_true",
                        help="whether to silence SQL console logging")
    args = parser.parse_args()

    kwargs = (dict(sqlalchemy_echo=False, sqlalchemy_echo_pool=False)
              if args.sql_quiet else {})

    if args.database_url is None:
        from ..database import engine, db_session, Base
    else:
        engine, db_session, Base = make_database(args.database_url, **kwargs)

    if args.init:
        init_db(Base, engine)

    data = parse(args.file, verbose=args.verbose)

    # db_session.add_all(data)
    for piece in data:
        db_session.add(piece)
        db_session.commit()

    # db_session.commit()

    print(f"Commit made!")
