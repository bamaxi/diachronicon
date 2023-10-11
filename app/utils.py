import typing as T

from sqlalchemy import (
    select,
)
from app.models import (
    DBModel
)
import app.database


def read_lines(path, mode='r', encoding='utf-8'):
    with open(path, mode, encoding=encoding) as f:
        return [line.strip() for line in f.read().split('\n')]
    

def filter_ban_na(item: T.Any):
    return item is not None


def apply_filter(
    data: T.List[T.Any], filter: T.Optional[T.Callable[[T.Any], bool]]=None
) -> T.List[T.Any]:
    if filter:
        data = [item for item in data if filter(item)]
    return data


def find_unique(
    model: DBModel, field: str, filter: T.Optional[T.Callable[[T.Any], bool]]=filter_ban_na,
    engine=None, cache: T.Dict[T.Tuple[DBModel, str], T.List[T.Any]]={}
) -> T.List[str]:
    if (model, field) in cache:
        return apply_filter(cache[(model, field)], filter)

    if engine is None:
        engine = app.database.engine

    col = getattr(model, field)
    stmt = select(col.distinct()).order_by(col)

    with engine.connect() as conn:
        results = conn.execute(stmt).scalars().all()
    
    cache[(model, field)] = results
    print(type(results), results)
    return apply_filter(results, filter)