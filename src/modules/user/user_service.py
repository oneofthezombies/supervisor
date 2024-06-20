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

from src import models
from src.modules.db import db_service
from src.schemas import User, UserCreate

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


class UserService:
    def __init__(self, db_service: db_service.Dep):
        self.db_service = db_service

    async def get_db_user_by_username(self, username: str) -> Optional[models.User]:
        """
        NOTICE: 민감정보(해시된 비밀번호)를 포함한 객체를 반환합니다.
        해시된 비밀번호가 필요한 것이 아니라면 `.get_user_by_username(username)`을 사용해주세요.
        """
        result = await self.db_service.execute(
            select(models.User).filter(models.User.username == username)
        )
        user = result.scalars().first()
        if not user:
            return user

        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        user = await self.get_db_user_by_username(username)
        if not user:
            return user

        return self.filter_db_user(user)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db_service.execute(
            select(models.User).filter(models.User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return user

        return self.filter_db_user(user)

    async def create_user(self, dto: UserCreate) -> User:
        hashed_password = password_context.hash(dto.password)
        user = models.User(
            username=dto.username,
            hashed_password=hashed_password,
        )
        self.db_service.add(user)
        await self.db_service.commit()
        await self.db_service.refresh(user)
        return self.filter_db_user(user)

    async def create_user_if_not_exist_by_username(self, dto: UserCreate) -> User:
        user = await self.get_user_by_username(username=dto.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        return await self.create_user(dto)

    def filter_db_user(self, user: models.User) -> User:
        return User(id=user.id, username=user.username, role=user.role)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_context.verify(password, hashed_password)


Dep = Annotated[UserService, Depends(UserService)]
