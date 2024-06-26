from datetime import datetime, timezone
from typing import Optional

from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from passlib.context import CryptContext

from app import models
from app.common import Role, utcnow
from app.modules.db import db_service
from app.schemas import User, UserCreate, UserSecret

password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


class UserService:
    def __init__(self, db_service: db_service.Dep):
        self.db_service = db_service

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db_service.execute(
            select(models.User).where(
                models.User.username == username,
                models.User.deleted_at == None,
            )
        )
        user = result.scalars().first()
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db_service.execute(
            select(models.User).where(
                models.User.id == user_id,
                models.User.deleted_at == None,
            )
        )
        user = result.scalars().first()
        return user

    async def create_basic_user(self, dto: UserCreate) -> User:
        return await self._create_user(dto, Role.basic)

    async def create_admin_user(self, dto: UserCreate) -> User:
        return await self._create_user(dto, Role.admin)

    async def create_basic_user_if_not_exist_by_username(self, dto: UserCreate) -> User:
        user: User | None = await self.get_user_by_username(username=dto.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        return await self.create_basic_user(dto)

    async def get_user_secret_by_user_id(self, user_id: int) -> UserSecret:
        result = await self.db_service.execute(
            select(models.UserSecret).where(
                models.UserSecret.user_id == user_id,
                models.UserSecret.deleted_at == None,
            )
        )
        user_secret = result.scalars().first()
        return user_secret

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return password_context.verify(password, hashed_password)

    async def _create_user(self, dto: UserCreate, role: Role) -> User:
        hashed_password = password_context.hash(dto.password)
        user = models.User(
            username=dto.username,
            role=role,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        self.db_service.add(user)
        await self.db_service.flush()

        user_secret = models.UserSecret(
            user_id=user.id,
            hashed_password=hashed_password,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        self.db_service.add(user_secret)
        await self.db_service.commit()
        await self.db_service.refresh(user)
        return user


Dep = Annotated[UserService, Depends(UserService)]
