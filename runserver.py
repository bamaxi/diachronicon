from sqlalchemy.orm import aliased
from sqlalchemy import text, select

from app import create_app, db_session
from app.models import Construction, Change, Constraint, GeneralInfo

app = create_app()


# flask shell
@app.shell_context_processor
def make_shell_context():
    return {'Construction': Construction, 'Change': Change,
            'Constraint': Constraint, 'GeneralInfo': GeneralInfo,
            'session': db_session, 'aliased': aliased, 'text': text,
            'select': select}
