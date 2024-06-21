from fastapi import APIRouter, status

from app.modules.auth import auth_common, auth_service
from app.schemas import Token


router = APIRouter(prefix="/auth")


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=Token)
async def create_token(
    form_data: auth_common.FormDep,
    auth_service: auth_service.Dep,
):
    return await auth_service.create_token(form_data)


@router.post("/refresh", status_code=status.HTTP_201_CREATED, response_model=Token)
async def refresh_token(refresh_token: str, auth_service: auth_service.Dep):
    return await auth_service.refresh_token(refresh_token)
