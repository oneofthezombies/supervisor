from typing import Optional

# ignore passlib warning begin
import bcrypt


class About:
    pass


if not hasattr(bcrypt, "__about__"):
    about = About()
    setattr(about, "__version__", "1.0.0")
    setattr(bcrypt, "__about__", about)
# ignore passlib warning end


from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

from src import database, models, schemas

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


class UserService:
    async def get(db: AsyncSession = Depends(database.get_db)):
        return UserService(db)

    def __init__(self, db: AsyncSession):
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
