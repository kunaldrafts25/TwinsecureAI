from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Report
from app.schemas import ReportCreate, ReportQueryFilters, ReportUpdate


class CRUDReport:
    """CRUD operations for Report model."""

    async def get(
        self, db: AsyncSession, report_id: Union[UUID, str]
    ) -> Optional[Report]:
        """Get a single report by ID."""
        stmt = select(Report).where(Report.id == report_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filename(
        self, db: AsyncSession, filename: str
    ) -> Optional[Report]:
        """Get a single report by filename."""
        stmt = select(Report).where(Report.filename == filename)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, filters: ReportQueryFilters
    ) -> List[Report]:
        """Get multiple reports with filtering and pagination."""
        stmt = select(Report)

        # Apply filters
        if filters.start_time:
            stmt = stmt.where(Report.generated_at >= filters.start_time)
        if filters.end_time:
            stmt = stmt.where(Report.generated_at <= filters.end_time)

        # Apply sorting (default: newest first)
        stmt = stmt.order_by(desc(Report.generated_at))

        # Apply pagination
        stmt = stmt.offset(filters.offset).limit(filters.limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: ReportCreate) -> Report:
        """Create a new report."""
        obj_in_data = obj_in.model_dump()
        db_obj = Report(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Report, obj_in: Union[ReportUpdate, dict]
    ) -> Report:
        """Update an existing report (limited fields)."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self, db: AsyncSession, *, report_id: Union[UUID, str]
    ) -> Optional[Report]:
        """Delete a report by ID."""
        db_obj = await self.get(db, report_id=report_id)
        if db_obj:
            # Consider deleting the actual file from storage (e.g., S3) as well
            # file_location = db_obj.file_location
            # await delete_file_from_storage(file_location) # Placeholder
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        return None


# Instantiate the CRUD class
report = CRUDReport()
