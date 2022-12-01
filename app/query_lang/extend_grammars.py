from sqlalchemy import select

from app.database import db_session
from app.models import Construction, GeneralInfo, Change, Constraint


def get_values(fieldname, session):
    for orm in (Construction, GeneralInfo, Change, Constraint):
        if fieldname in vars(orm):
            col = getattr(orm, fieldname)
            if hasattr(col.type, "enums"):
                values = col.type.enums
            else:
                values = session.scalars(select(col).distinct()).all()
    return values


def format_values2lexical_rule(
    rule_name, values,
    RULE_ASSIGN_SYMB=':', QUOTE='"', JOINER='|', add_newlines=True
):
    if add_newlines:
        joiner = ('\n' + ' ' * (len(rule_name) + len(RULE_ASSIGN_SYMB) + 2)
                  + JOINER + ' ')
    else:
        joiner = ' ' + JOINER + ' '

    Q = QUOTE

    return (f"{rule_name} {RULE_ASSIGN_SYMB} "
            f"{joiner.join(Q + val + Q for val in values)}\n\n")


def append_to_file(filename, text, encoding='utf-8'):
    with open(filename, 'a', encoding=encoding) as f:
        f.write(text)


def append2grammar_values_of(fieldnames, grammar_filename, session, **rule_format):
    for fieldname in fieldnames:
        # TODO: do a global check so no values are prefixes?
        values = get_values(fieldname, session)
        formatted_rule = format_values2lexical_rule(fieldname, values,
                                                    **rule_format)
        append_to_file(grammar_filename, formatted_rule)
        print(values, formatted_rule, sep='\n')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Display distinct values of a database column')

    parser.add_argument('columns', type=str, metavar='C', nargs='+',
                        help='names of columns')

    args = parser.parse_args()

    peg_format = dict(RULE_ASSIGN_SYMB='<-', JOINER='/', QUOTE='`')

    append2grammar_values_of(args.columns, './app/query_lang/logic_query.peg', db_session,
                             **peg_format)
