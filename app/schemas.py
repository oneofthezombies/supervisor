from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.common import RoleEnum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class User(BaseModel):
    id: int
    username: str
    role: RoleEnum
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode: True


class UserCreate(BaseModel):
    username: str
    password: str


class UserSecret(BaseModel):
    id: int
    user_id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode: True


class Reservation(BaseModel):
    id: int
    user_id: int
    start_at: datetime
    end_at: datetime
    applicant_count: int
    is_confirmed: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        orm_mode: True


class ReservationCreate(BaseModel):
    start_at: datetime
    end_at: datetime
    applicant_count: int


class ReservationUpdate(BaseModel):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    applicant_count: Optional[int] = None
    is_confirmed: Optional[bool] = None


class ReservationPublic(BaseModel):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    applicant_count: Optional[int] = None
