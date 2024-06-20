from fastapi import Depends
from typing_extensions import Annotated
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)


basic_scheme = HTTPBasic()

BasicDep = Annotated[HTTPBasicCredentials, Depends(HTTPBasicCredentials)]

FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# NOTICE: src/modules/auth_router.py 내 router, create_token의 URL 규약이 맞아야 함
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]
