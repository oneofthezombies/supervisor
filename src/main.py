# import os

# if os.environ.get("DEBUG"):
#     from dotenv import load_dotenv

#     load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.auth import auth_router
from src.modules.user import user_router
from src.modules.db import db_common


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_common.engine.begin() as conn:
        await conn.run_sync(db_common.Base.metadata.create_all)
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router.router)
app.include_router(user_router.router)
