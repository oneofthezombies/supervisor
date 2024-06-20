from typing import cast

from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.db import db_common


async def get():
    async with db_common.SessionLocal() as sess:
        sess = cast(AsyncSession, sess)
        try:
            yield sess
        finally:
            await sess.close()


Dep = Annotated[AsyncSession, Depends(get)]
