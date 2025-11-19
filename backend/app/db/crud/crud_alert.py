"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

CRUD operations for Alert model.
"""

from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Alert
from app.schemas import AlertCreate, AlertQueryFilters, AlertUpdate


class CRUDAlert:
    """CRUD operations for Alert model"""
    
    async def get(
        self,
        db: AsyncSession,
        alert_id: UUID | str
    ) -> Alert | None:
        """Get a single alert by ID"""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        filters: AlertQueryFilters
    ) -> list[Alert]:
        """Get multiple alerts with filtering and pagination"""
        stmt = select(Alert)
        
        # Apply filters
        if filters.ip_address:
            stmt = stmt.where(Alert.source_ip == filters.ip_address)
        
        if filters.start_time:
            stmt = stmt.where(Alert.triggered_at >= filters.start_time)
        
        if filters.end_time:
            stmt = stmt.where(Alert.triggered_at <= filters.end_time)
        
        if filters.severity:
            stmt = stmt.where(Alert.severity == filters.severity)
        
        if filters.status:
            stmt = stmt.where(Alert.status == filters.status)
        
        if filters.alert_type:
            stmt = stmt.where(Alert.alert_type == filters.alert_type)
        
        if filters.min_abuse_score is not None:
            stmt = stmt.where(Alert.abuse_score >= filters.min_abuse_score)
        
        if filters.max_abuse_score is not None:
            stmt = stmt.where(Alert.abuse_score <= filters.max_abuse_score)
        
        if filters.country:
            stmt = stmt.where(Alert.ip_info.op("->>")("country") == filters.country)
        
        # Sort by newest first
        stmt = stmt.order_by(desc(Alert.triggered_at))
        
        # Apply pagination
        stmt = stmt.offset(filters.offset).limit(filters.limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AlertCreate
    ) -> Alert:
        """Create a new alert"""
        obj_in_data = obj_in.model_dump()
        db_obj = Alert(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Alert,
        obj_in: AlertUpdate | dict
    ) -> Alert:
        """Update an existing alert"""
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
        self,
        db: AsyncSession,
        *,
        alert_id: UUID | str
    ) -> Alert | None:
        """Delete an alert by ID"""
        db_obj = await self.get(db, alert_id=alert_id)
        
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        
        return None
    
    async def get_count_by_severity(self, db: AsyncSession) -> dict[str, int]:
        """Get count of alerts grouped by severity"""
        stmt = select(
            Alert.severity,
            func.count(Alert.id).label("count")
        ).group_by(Alert.severity)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        
        for severity, count in rows:
            if severity:
                severity_str = severity.value if hasattr(severity, "value") else str(severity)
                severity_lower = severity_str.lower()
                if severity_lower in counts:
                    counts[severity_lower] = count
        
        return counts
    
    async def get_count_by_status(self, db: AsyncSession) -> dict[str, int]:
        """Get count of alerts grouped by status"""
        stmt = select(
            Alert.status,
            func.count(Alert.id).label("count")
        ).group_by(Alert.status)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        counts = {}
        for status, count in rows:
            if status:
                status_str = status.value if hasattr(status, "value") else str(status)
                counts[status_str.lower()] = count
        
        return counts


# Instantiate the CRUD class
alert = CRUDAlert()
