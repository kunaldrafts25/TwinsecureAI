"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

import json  # Import json for casting
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import String as SQLString  # Import cast and String for JSON filtering
from sqlalchemy import (
    asc,
    cast,
    desc,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Alert
from app.schemas import AlertCreate, AlertQueryFilters, AlertUpdate


class CRUDAlert:
    """CRUD operations for Alert model."""

    async def get(
        self, db: AsyncSession, alert_id: Union[UUID, str]
    ) -> Optional[Alert]:
        """Get a single alert by ID."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, filters: AlertQueryFilters
    ) -> List[Alert]:
        """Get multiple alerts with filtering and pagination."""
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
            # Filter by country within the JSON ip_info field
            # Note: This requires the country to be stored consistently, e.g., ip_info['country']
            # This filter might be slow on large datasets without specific JSON indexing in PG.
            # Use ->> to get JSON field as text
            stmt = stmt.where(Alert.ip_info.op("->>")("country") == filters.country)
            # For case-insensitive matching:
            # from sqlalchemy import func as sqlfunc
            # stmt = stmt.where(sqlfunc.lower(Alert.ip_info.op('->>')('country')) == filters.country.lower())

        # Apply sorting (default: newest first)
        stmt = stmt.order_by(desc(Alert.triggered_at))

        # Apply pagination
        stmt = stmt.offset(filters.offset).limit(filters.limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: AlertCreate) -> Alert:
        """Create a new alert."""
        # Convert Pydantic model to dictionary
        obj_in_data = obj_in.model_dump()
        db_obj = Alert(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Alert, obj_in: Union[AlertUpdate, dict]
    ) -> Alert:
        """Update an existing alert."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):  # Check if the field exists on the model
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self, db: AsyncSession, *, alert_id: Union[UUID, str]
    ) -> Optional[Alert]:
        """Delete an alert by ID."""
        db_obj = await self.get(db, alert_id=alert_id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        return None


# Instantiate the CRUD class
alert = CRUDAlert()
