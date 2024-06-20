from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, select
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status

from src import models
from src.common import RoleEnum
from src.modules.db import db_service
from src.modules.permission.permission_deps import CurrentUserDep
from src.schemas import (
    Reservation,
    ReservationPublic,
    ReservationCreate,
    ReservationUpdate,
)


class ReservationService:
    def __init__(
        self,
        db_service: db_service.Dep,
        current_user: CurrentUserDep,
    ):
        self.db_service = db_service
        self.current_user = current_user

    async def read_reservations(self) -> List[Reservation]:
        async with self.db_service.begin():
            query = select(models.Reservation)
            if self.current_user.role == RoleEnum.basic:
                query = query.where(models.Reservation.user_id == self.current_user.id)

            result = await self.db_service.execute(query)
            reservations = result.scalars().all()
            return reservations

    async def create_reservation(self, dto: ReservationCreate) -> Reservation:
        self._validate_start_at_and_end_at(dto.start_at, dto.end_at)
        async with self.db_service.begin():
            result = await self.db_service.execute(
                select(func.sum(models.Reservation.applicant_count)).where(
                    models.Reservation.start_at <= dto.start_at,
                    models.Reservation.end_at >= dto.end_at,
                    models.Reservation.is_confirmed == True,
                    models.Reservation.deleted_at == None,
                )
            )
            total_applicant_count = (result.scalar() or 0) + dto.applicant_count
            if total_applicant_count > 50000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum applicant count exceeded",
                )

            reservation = models.Reservation(
                user_id=self.current_user.id,
                start_at=dto.start_at,
                end_at=dto.end_at,
                applicant_count=dto.applicant_count,
            )
            self.db_service.add(reservation)
            await self.db_service.commit()
            await self.db_service.refresh(reservation)
            return reservation

    async def update_reservation(
        self, reservation_id: int, dto: ReservationUpdate
    ) -> Reservation:
        async with self.db_service.begin():
            reservation = await self._get_reservation(reservation_id)

            if self.current_user.role == RoleEnum.basic:
                if reservation.id != self.current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You cannot update another user's reservation",
                    )

                if reservation.is_confirmed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Reservations that are confirmed cannot be update",
                    )

                if dto.is_confirmed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have permission to confirm the reservation",
                    )

            for key, value in vars(dto).items():
                if value is not None:
                    setattr(reservation, key, value)

            await self.db_service.commit()
            await self.db_service.refresh(reservation)
            return reservation

    async def delete_reservation(self, reservation_id: int) -> Reservation:
        async with self.db_service.begin():
            reservation = await self._get_reservation(reservation_id)

            if self.current_user.role == RoleEnum.basic:
                if reservation.id != self.current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You cannot delete another user's reservation",
                    )

                if reservation.is_confirmed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Reservations that are confirmed cannot be delete",
                    )

            if reservation.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reservation has already been deleted",
                )

            reservation.deleted_at = datetime.now(timezone.utc)
            await self.db_service.commit()
            await self.db_service.refresh(reservation)
            return reservation

    async def read_publics(
        self, start_at: datetime, end_at: datetime
    ) -> List[ReservationPublic]:
        self._validate_start_at_and_end_at(start_at, end_at)
        async with self.db_service.begin():
            result = await self.db_service.execute(
                select(
                    models.Reservation.start_at,
                    models.Reservation.end_at,
                    models.Reservation.applicant_count,
                ).where(
                    models.Reservation.start_at < end_at,
                    models.Reservation.end_at > start_at,
                    models.Reservation.is_confirmed == True,
                    models.Reservation.deleted_at == None,
                )
            )
            rows = result.all()
            return [
                ReservationPublic(
                    start_at=row.start_at,
                    end_at=row.end_at,
                    applicant_count=row.applicant_count,
                )
                for row in rows
            ]

    async def _get_reservation(self, reservation_id: int) -> Reservation:
        result = await self.db_service.execute(
            select(models.Reservation).where(
                models.Reservation.id == reservation_id,
                models.Reservation.deleted_at == None,
            )
        )
        reservation = result.scalars().first()
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )

        return reservation

    async def _validate_start_at_and_end_at(self, start_at: datetime, end_at: datetime):
        if start_at < datetime.now(timezone.utc) + timedelta(days=3):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservations can be made up to 3 days in advance",
            )

        if start_at >= end_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time cannot be later than end time",
            )


Dep = Annotated[ReservationService, Depends(ReservationService)]
