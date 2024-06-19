from contextlib import asynccontextmanager

import asyncio

from fastapi import FastAPI

from src.routers import users
from src.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


app = FastAPI(lifespan=lifespan)


app.include_router(users.router)
