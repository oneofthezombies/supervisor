from fastapi import APIRouter

from src.modules.auth.auth_common import FormDep
from src.schemas import User, UserCreate
from src.modules.user import user_service
from src.modules.permission.permission_deps import CurrentUserDep

router = APIRouter(prefix="/users")


@router.post("/", response_model=User)
async def create_user(form_data: FormDep, user_service: user_service.Dep):
    return await user_service.create_user_if_not_exist_by_username(
        UserCreate(username=form_data.username, password=form_data.password)
    )


@router.get("/me", response_model=User)
async def read_me(current_user: CurrentUserDep):
    return current_user
