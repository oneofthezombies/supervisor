from typing import cast

from asyncpg import InvalidCachedStatementError
from fastapi import Depends
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NotSupportedError

from app.database import SessionLocal


async def get_db_service():
    async with SessionLocal() as sess:
        sess = cast(AsyncSession, sess)
        try:
            yield sess
        except NotSupportedError as e:
            if isinstance(e.orig, InvalidCachedStatementError):
                await sess.rollback()
                async with SessionLocal() as new_session:
                    yield new_session
            else:
                raise
        finally:
            await sess.close()


Dep = Annotated[AsyncSession, Depends(get_db_service)]
