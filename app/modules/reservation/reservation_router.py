from datetime import datetime
from typing import List
from fastapi import APIRouter, status

from app.modules.reservation import reservation_service
from app.modules.auth.auth_deps import CurrentUserDep
from app.schemas import Reservation, ReservationCreate, ReservationUpdate

router = APIRouter(prefix="/reservations")


@router.get("", response_model=List[Reservation])
async def read_reservations(
    _: CurrentUserDep,
    reservation_service: reservation_service.Dep,
):
    return await reservation_service.read_reservations()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Reservation)
async def create_reservation(
    dto: ReservationCreate,
    _: CurrentUserDep,
    reservation_service: reservation_service.Dep,
):
    return await reservation_service.create_reservation(dto)


@router.patch("/{reservation_id}", response_model=Reservation)
async def update_reservation(
    reservation_id: int,
    dto: ReservationUpdate,
    _: CurrentUserDep,
    reservation_service: reservation_service.Dep,
):
    return await reservation_service.update_reservation(reservation_id, dto)


@router.delete("/{reservation_id}", response_model=Reservation)
async def delete_reservation(
    reservation_id: int,
    _: CurrentUserDep,
    reservation_service: reservation_service.Dep,
):
    return await reservation_service.delete_reservation(
        reservation_id,
    )


@router.get("/publics")
async def read_public_reservations(
    start_at: datetime,
    end_at: datetime,
    _: CurrentUserDep,
    reservation_service: reservation_service.Dep,
):
    return await reservation_service.read_publics(start_at, end_at)
