from typing import (
    Type,
    Dict,
    Union
)
import argparse

from openpyxl import load_workbook

from ..models import (
    Construction,
    GeneralInfo,
    Change,
    Constraint,
    FormulaElement
)


SHEET_TO_CLASS = {
    'construction': Construction,
    'general_info': GeneralInfo,
    'changes': Change,
    'constraints': Constraint,
}

COLUMNS_CORRECTION = {
    'general_info': {
            'construction_name': 'name',
    },
    'construction': {
        'construction_id': 'id',
        'in_Russian_Constructicon': 'in_rus_constructicon',
        'number_in_Russian_Constructicon': 'rus_constructicon_id',
    },
    'constraints': {
        # 'constraint_id': 'id',
        'syntactic_constraints': 'syntactic',
        'semantic_constraints': 'semantic',
    }
}


# TODO: special processing for NP (=NP-nom) ?
def parse_formula(
        formula: str,
        el_variants_sep='/',
        # model_class=FormulaElement
) -> list[dict]:
    data = []

    for i, element in enumerate(formula.split(' ')):
        self_result_elements = []

        has_brackets = any(br in element for br in ('(', ')'))
        if has_brackets:
            element = element.strip('()')

        has_variants = el_variants_sep in element
        if has_variants:
            actual_elements = element.split(el_variants_sep)
            first_element_data = {
                'value': actual_elements[0], 'order': i,
                'is_optional': has_brackets, 'has_variants': has_variants
            }
            self_result_elements.append(first_element_data)
            self_result_elements.extend([
                {'value': variant_el, 'order': i, 'is_optional': has_brackets}
                for variant_el in actual_elements[1:]
            ])
        else:
            self_result_elements = [
                {'value': element, 'order': i, 'is_optional': has_brackets}
            ]

        # TODO: special parsing / saving of nom nps (simply `n` / `np`)

        # element_data = {'value': element, 'order': i, 'is_optional': has_brackets}
        # element_obj = model_class(**element_data)
        # element_objs = [model_class(**el_data) for el_data in self_result_elements]

        # data.append(element_obj)

        # data.extend(element_objs)
        data.extend(self_result_elements)

    return data


def fix_construction_id(construction_id: str):
    if isinstance(construction_id, int):
        return construction_id

    construction_id = construction_id.replace('.', '0')
    if '(' in construction_id and ')' in construction_id:
        num = construction_id[:construction_id.index('(')]
        group = construction_id[construction_id.index('(')+1:construction_id.index(')')]
        return int(group+num)
    else:
        print(construction_id)
        raise ValueError


def fix_values(
        phrase_dict: Dict[str, Union[str, int, None]],
        model_class: Type[Union[Construction, GeneralInfo, Change, Constraint]]
):
    if model_class is Construction:
        phrase_dict['id'] = fix_construction_id(phrase_dict['id'])
    elif 'construction_id' in phrase_dict:
        phrase_dict['construction_id'] = fix_construction_id(phrase_dict['construction_id'])

    return phrase_dict


def parse(filename: str, verbose=False):
    wb = load_workbook(filename)

    # parse.idscorrection = {}

    data = []
    for sheet in wb.worksheets:
        model_class = SHEET_TO_CLASS.get(sheet.title)
        if model_class is None:
            continue

        rows_iter = sheet.iter_rows()

        title_row = next(rows_iter)
        title_row_values = [cell.value.replace(' ', '_')
                            for cell in title_row if cell.value]
        title_row_values = [COLUMNS_CORRECTION.get(sheet.title, {}).get(value, value)
                            for value in title_row_values]

        for row in rows_iter:
            cell_values = [cell.value.strip() if isinstance(cell.value, str) else cell.value
                           for cell in row]
            if not any(cell_values):
                continue

            phrase_dict = dict(zip(title_row_values, cell_values))
            fix_values(phrase_dict, model_class)

            values = model_class(**phrase_dict)

            if model_class is Construction:
                formula_elements = parse_formula(phrase_dict['formula'])
                formula_elements_vals = [FormulaElement(**el_data)
                                         for el_data in formula_elements]
                if verbose:
                    print(FormulaElement, formula_elements_vals)

                values.formula_elements.extend(formula_elements_vals)

            if verbose:
                print(model_class, phrase_dict)

            data.append(values)

    if verbose:
        for item in data:
            print(item, end='\n\n')

    return data


if __name__ == "__main__":
    from ..database_utils import init_db, make_database

    parser = argparse.ArgumentParser(
        description='Append data from a suitable .xlsx (.README) to'
                    'an (existing) database that is configured for this app')

    parser.add_argument('file', metavar='F', type=str,
                        help='an existing database file path')
    parser.add_argument('--database-url', type=str, default=None,
                        help='an optional sqlalchemy uri to use a different database')
    # parser.add_argument('--database-name', type=str, default=None,
    #                     help='an optional name for the database with same scheme')
    parser.add_argument('-i', '--init', action='store_true',
                        help='whether to initialize user database')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='whether to print values as they are processed')
    args = parser.parse_args()

    if args.database_url is None:
        from ..database import engine, db_session, Base
    else:
        engine, db_session, Base = make_database(args.database_url)

    if args.init:
        init_db(Base, engine)

    data = parse(args.file, verbose=args.verbose)

    db_session.add_all(data)
    db_session.commit()

    print(f"Commit made!")
