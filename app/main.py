import os

print("db host:", os.environ["DB_HOST"])

from app.common import ignore_passlib_warning

ignore_passlib_warning()

from fastapi import FastAPI

from app.modules.auth import auth_router
from app.modules.user import user_router
from app.modules.reservation import reservation_router


app = FastAPI()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(reservation_router.router)
