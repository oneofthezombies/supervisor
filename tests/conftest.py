import pytest
from httpx import AsyncClient

from app.main import app
from app import database


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    database.Base.metadata.create_all(database.engine)
    yield
    database.Base.metadata.drop_all(database.engine)
