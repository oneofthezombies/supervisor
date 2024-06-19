from fastapi import APIRouter, Depends, HTTPException, status

from src import schemas
from src.services.user import UserService

router = APIRouter()


@router.post("/users", response_model=schemas.User)
async def create_user(
    dto: schemas.UserCreate, user_service: UserService = Depends(UserService.get)
):
    user = await user_service.get_user_by_username(username=dto.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return await user_service.create_user(dto)
