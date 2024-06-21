import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.modules.user.user_service import UserService
from app.schemas import UserCreate


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    # DB 삭제
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.drop_all)

    # DB 생성
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)

    # 어드민 계정 생성
    async with AsyncSession(database.engine) as sess:
        username = os.environ["ADMIN_USERNAME"]
        user = await UserService(sess).create_admin_user(
            UserCreate(
                username=username,
                password=os.environ["ADMIN_PASSWORD"],
            )
        )

    yield


@pytest.fixture(scope="module")
def shared():
    data = {}
    return data
