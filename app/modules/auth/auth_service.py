from datetime import datetime, timedelta, timezone
import os
from typing import Optional

from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, OAuth2PasswordRequestForm
import jwt

from app.common import utcnow
from app.schemas import Token, User
from app.modules.user import user_service


AUTH_JWT_SECRET_KEY = os.environ["AUTH_JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    def __init__(self, user_service: user_service.Dep):
        self.user_service = user_service

    async def create_token(self, form_data: OAuth2PasswordRequestForm) -> Token:
        user = await self.user_service.get_user_by_username(
            form_data.username,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username",
                headers={"WWW-Authenticate": "Basic"},
            )

        user_secret = await self.user_service.get_user_secret_by_user_id(user.id)
        if not self.user_service.verify_password(
            form_data.password,
            user_secret.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password",
                headers={"WWW-Authenticate": "Basic"},
            )

        now_at = utcnow()
        access_token_expires_at = now_at + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = jwt.encode(
            {"sub": user.id, "exp": access_token_expires_at},
            AUTH_JWT_SECRET_KEY,
            JWT_ALGORITHM,
        )

        refresh_token_expires_at = now_at + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = jwt.encode(
            {"sub": user.id, "exp": refresh_token_expires_at},
            AUTH_JWT_SECRET_KEY,
            JWT_ALGORITHM,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_token(self, refresh_token: str) -> Token:
        user = await self.parse_user_from_token(refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        access_token = self._create_access_token(
            utcnow(),
            user.id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def parse_user_from_token(self, token) -> Optional[User]:
        user_id = self._parse_user_id_from_token(token)
        if user_id is None:
            return None

        return await self.user_service.get_user_by_id(user_id)

    def _parse_user_id_from_token(self, token: str) -> Optional[int]:
        payload: Optional[dict] = None
        try:
            payload = jwt.decode(
                token,
                AUTH_JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )
        except jwt.PyJWTError as e:
            print(e)
            return None

        if not payload:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        if not isinstance(user_id, int):
            return None

        return user_id

    def _create_access_token(self, now_at: datetime, user_id: int) -> str:
        access_token_expires_at = now_at + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = jwt.encode(
            {"sub": user_id, "exp": access_token_expires_at},
            AUTH_JWT_SECRET_KEY,
            JWT_ALGORITHM,
        )

        return access_token


Dep = Annotated[AuthService, Depends(AuthService)]
