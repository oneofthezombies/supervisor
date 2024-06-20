from pydantic import BaseModel

from src.common import RoleEnum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserBase(BaseModel):
    username: str
    role: RoleEnum


class UserCreate(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode: True
