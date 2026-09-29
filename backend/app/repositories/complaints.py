from typing import cast
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Category, ComplaintStatus, Priority
from app.models import Complaint


class ComplaintRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, complaint: Complaint) -> Complaint:
        self._session.add(complaint)
        await self._session.commit()
        await self._session.refresh(complaint)
        return complaint

    async def get(self, complaint_id: UUID) -> Complaint | None:
        return await self._session.get(Complaint, complaint_id)

    async def list(
        self,
        *,
        category: Category | None,
        priority: Priority | None,
        status: ComplaintStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Complaint], int]:
        statement: Select[Complaint] = select(Complaint).order_by(Complaint.created_at.desc())
        filters = [
            criterion
            for criterion in (
                Complaint.category == category if category else None,
                Complaint.priority == priority if priority else None,
                Complaint.status == status if status else None,
            )
            if criterion is not None
        ]
        if filters:
            statement = statement.where(*filters)
        items = cast(
            list[Complaint],
            list(
                (
                    await self._session.scalars(
                        statement.offset((page - 1) * page_size).limit(page_size)
                    )
                ).all()
            ),
        )
        total = await self._session.scalar(select(func.count()).select_from(statement.subquery()))
        return items, total or 0

    async def transition_status(
        self,
        complaint_id: UUID,
        *,
        current: ComplaintStatus,
        target: ComplaintStatus,
    ) -> Complaint | None:
        """Atomically update only when the row remains in its observed state."""
        result = await self._session.execute(
            update(Complaint)
            .where(Complaint.id == complaint_id, Complaint.status == current)
            .values(status=target)
            .returning(Complaint)
        )
        complaint = result.scalar_one_or_none()
        if complaint is None:
            await self._session.rollback()
            return None
        await self._session.commit()
        await self._session.refresh(complaint)
        return complaint

    async def statistics(self) -> dict[str, object]:
        """Return compact dashboard aggregates without exposing reporter details."""
        total = await self._session.scalar(select(func.count()).select_from(Complaint))
        by_status_rows = (
            await self._session.execute(
                select(Complaint.status, func.count()).group_by(Complaint.status)
            )
        ).all()
        by_category_rows = (
            await self._session.execute(
                select(Complaint.category, func.count()).group_by(Complaint.category)
            )
        ).all()
        return {
            "total": total or 0,
            "by_status": {str(key): value for key, value in by_status_rows},
            "by_category": {str(key): value for key, value in by_category_rows},
        }

    async def exists_with_text_and_location(self, text: str, location: str) -> bool:
        existing = await self._session.scalar(
            select(Complaint.id)
            .where(Complaint.text == text, Complaint.location == location)
            .limit(1)
        )
        return existing is not None
