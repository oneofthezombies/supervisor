###############################
# ignore passlib warning begin
import bcrypt


class About:
    pass


if not hasattr(bcrypt, "__about__"):
    about = About()
    setattr(about, "__version__", "1.0.0")
    setattr(bcrypt, "__about__", about)
# ignore passlib warning end
###############################

from typing import Optional

from typing_extensions import Annotated
from fastapi import Depends
from sqlalchemy.future import select
from passlib.context import CryptContext

from src import models, schemas
from src.modules.db import db_service

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


class UserService:
    def __init__(self, db_service: db_service.Dep):
        self.db_service = db_service

    async def get_user_by_username(self, username: str) -> Optional[models.User]:
        result = await self.db_service.execute(
            select(models.User).filter(models.User.username == username)
        )
        return result.scalars().first()

    async def create_user(self, dto: schemas.UserCreate) -> models.User:
        hashed_password = password_context.hash(dto.password)
        user = models.User(
            username=dto.username,
            hashed_password=hashed_password,
        )
        self.db_service.add(user)
        await self.db_service.commit()
        await self.db_service.refresh(user)
        return user

    async def verify_password(self, password: str, user: models.User) -> bool:
        return password_context.verify(password, user.hashed_password)


Dep = Annotated[UserService, Depends(UserService)]
