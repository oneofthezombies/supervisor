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

from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from passlib.context import CryptContext

from src import models, schemas
from src.database import DBDep

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


class UserService:
    def __init__(self, db: DBDep):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[models.User]:
        result = await self.db.execute(
            select(models.User).filter(models.User.username == username)
        )
        return result.scalars().first()

    async def create_user(self, dto: schemas.UserCreate) -> models.User:
        hashed_password = password_context.hash(dto.password)
        user = models.User(
            username=dto.username,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, username: str, password: str):
        user: models.User | None = await self.get_user_by_username(self.db, username)
        if not user:
            return user
        if not password_context.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return user


UserServiceDep = Annotated[UserService, Depends(UserService)]
