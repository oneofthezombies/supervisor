from typing import cast
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.common import database_url

engine = create_async_engine(database_url(), echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as sess:
        sess = cast(AsyncSession, sess)
        try:
            yield sess
        finally:
            await sess.close()
