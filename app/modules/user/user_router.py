from fastapi import APIRouter, status

from app.modules.auth.auth_common import FormDep
from app.schemas import User, UserCreate
from app.modules.user import user_service
from app.modules.auth.auth_deps import CurrentUserDep

router = APIRouter(prefix="/users")


@router.get("/me", response_model=User)
async def read_user_me(current_user: CurrentUserDep):
    return current_user


@router.post("", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_basic_user(form_data: FormDep, user_service: user_service.Dep):
    return await user_service.create_basic_user_if_not_exist_by_username(
        UserCreate(username=form_data.username, password=form_data.password)
    )
