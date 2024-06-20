from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status

from app.modules.auth.auth_common import TokenDep
from app.schemas import User
from app.common import RoleEnum
from app.modules.auth import auth_service


async def get_current_user(token: TokenDep, auth_service: auth_service.Dep) -> User:
    user = await auth_service.parse_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_admin_user(user: CurrentUserDep) -> User:
    if user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid permission"
        )

    return user


CurrentAdminUserDep = Annotated[User, Depends(get_current_admin_user)]
