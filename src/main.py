from src.common import ignore_passlib_warning

ignore_passlib_warning()

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.db import db_common
from src.modules.auth import auth_router
from src.modules.user import user_router
from src.modules.reservation import reservation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_common.engine.begin() as conn:
        await conn.run_sync(db_common.Base.metadata.create_all)
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(reservation_router.router)
