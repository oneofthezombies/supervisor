from fastapi import APIRouter, HTTPException, status

from src import schemas
from src.services.user import UserServiceDep

router = APIRouter()


@router.post("/users/login")
async def login_user():
    """
    Basic 인증
    """


@router.post("/users/logout")
async def logout_user():
    """
    토큰 인증
    """


@router.post("/users", response_model=schemas.User)
async def create_user(dto: schemas.UserCreate, user_service: UserServiceDep):
    user = await user_service.get_user_by_username(username=dto.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    return await user_service.create_user(dto)
