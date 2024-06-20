from fastapi import APIRouter

from src.modules.auth import auth_common, auth_service
from src.schemas import Token


router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token)
async def create_token(
    form_data: auth_common.FormDep,
    auth_service: auth_service.Dep,
):
    return await auth_service.create_token(form_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, auth_service: auth_service.Dep):
    return await auth_service.refresh_token(refresh_token)
