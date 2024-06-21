from typing import cast

from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal


async def get_db_service():
    async with SessionLocal() as sess:
        sess = cast(AsyncSession, sess)
        try:
            yield sess
        finally:
            await sess.close()


Dep = Annotated[AsyncSession, Depends(get_db_service)]
