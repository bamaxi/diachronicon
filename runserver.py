from app import create_app
from config import TestConfig

# app = create_app()
app = create_app(test_config_obj=TestConfig)
print("about to run (runserver)")
app.run("0.0.0.0", 5000)


# flask shell
@app.shell_context_processor
def make_shell_context():
    from sqlalchemy import (
        text,
        select,
        func,
        or_,
        and_
    )
    from sqlalchemy.orm import aliased

    from app.models import (
        Construction,
        Change,
        Constraint,
        GeneralInfo,
        ConstructionVariant,
        FormulaElement
    )

    db_session = app.db_session
    engine = app.engine

    return {
        'Construction': Construction, 'Change': Change,
        'Constraint': Constraint, 'GeneralInfo': GeneralInfo,
        'ConstructionVariant': ConstructionVariant,
        'FormulaElement': FormulaElement,
        'session': db_session, 'engine': engine,
        'aliased': aliased, 'text': text,
        'select': select, 'func': func
    }
