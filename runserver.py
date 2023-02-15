# from sqlalchemy.orm import aliased
# from sqlalchemy import text, select

from app import create_app, db_session

app = create_app()


# flask shell
@app.shell_context_processor
def make_shell_context():
    from sqlalchemy.orm import aliased
    from sqlalchemy import (
        text,
        select,
        or_,
        and_
    )

    from app.models import Construction, Change, Constraint, GeneralInfo

    return {'Construction': Construction, 'Change': Change,
            'Constraint': Constraint, 'GeneralInfo': GeneralInfo,
            'session': db_session, 'aliased': aliased, 'text': text,
            'select': select}
