import pytest

from config import TestConfig
from app import create_app
from app.models import Construction
from app.database import engine
from app.utils import find_unique

@pytest.fixture
def app():
    return create_app(test_config_obj=TestConfig)


@pytest.fixture
def page_loader(app):
    app.app_context()
    return app.test_client().get


@pytest.fixture
def construction_page_loader(page_loader):
    return lambda id: page_loader("/construction/{id}/".format(id=id))


def ids():
    return find_unique(Construction, "id")


@pytest.mark.parametrize('construction_id', ids())
def test_construction_page_loads(construction_id, construction_page_loader):
    response = construction_page_loader(construction_id)
    assert 200 <= response.status_code < 400