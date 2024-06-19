from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.common import RoleEnum
from src import database, models
from services.user import UserService


security = HTTPBasic()


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    user_service: UserService = Depends(UserService.get),
):
    user = await user_service.authenticate_user(
        credentials.username, credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
