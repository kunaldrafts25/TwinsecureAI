"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

CRUD operations for Digital Twin, Network Topology, and Twin Engagement models.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DigitalTwin, NetworkTopology, TwinEngagement
from app.schemas.digital_twin import (
    DigitalTwinCreate,
    DigitalTwinUpdate,
    NetworkTopologyCreate,
    TwinEngagementCreate,
)


class CRUDDigitalTwin:
    """CRUD operations for Digital Twin"""
    
    async def get(
        self,
        db: AsyncSession,
        twin_id: UUID
    ) -> DigitalTwin | None:
        """Get a digital twin by ID"""
        stmt = select(DigitalTwin).where(DigitalTwin.id == twin_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        is_honeypot: bool | None = None,
    ) -> list[DigitalTwin]:
        """Get multiple digital twins with optional filtering"""
        stmt = select(DigitalTwin)
        
        if status:
            stmt = stmt.where(DigitalTwin.status == status)
        
        if is_honeypot is not None:
            stmt = stmt.where(DigitalTwin.is_honeypot == is_honeypot)
        
        stmt = stmt.offset(skip).limit(limit).order_by(DigitalTwin.created_at.desc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: DigitalTwinCreate,
        created_by_id: UUID | None = None
    ) -> DigitalTwin:
        """Create a new digital twin"""
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        
        if created_by_id:
            obj_in_data["created_by_id"] = created_by_id
        
        db_obj = DigitalTwin(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: DigitalTwin,
        obj_in: DigitalTwinUpdate
    ) -> DigitalTwin:
        """Update an existing digital twin"""
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
        twin_id: UUID
    ) -> DigitalTwin | None:
        """Delete a digital twin"""
        db_obj = await self.get(db, twin_id=twin_id)
        
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        
        return None


class CRUDNetworkTopology:
    """CRUD operations for Network Topology"""
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: NetworkTopologyCreate
    ) -> NetworkTopology:
        """Create a network topology connection"""
        obj_in_data = obj_in.model_dump()
        db_obj = NetworkTopology(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_twin(
        self,
        db: AsyncSession,
        twin_id: UUID
    ) -> list[NetworkTopology]:
        """Get all connections for a digital twin"""
        stmt = select(NetworkTopology).where(
            (NetworkTopology.source_twin_id == twin_id)
            | (NetworkTopology.destination_twin_id == twin_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class CRUDTwinEngagement:
    """CRUD operations for Twin Engagements"""
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TwinEngagementCreate
    ) -> TwinEngagement:
        """Create a new twin engagement record"""
        obj_in_data = obj_in.model_dump()
        db_obj = TwinEngagement(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_twin(
        self,
        db: AsyncSession,
        twin_id: UUID,
        limit: int = 100
    ) -> list[TwinEngagement]:
        """Get engagements for a digital twin"""
        stmt = (
            select(TwinEngagement)
            .where(TwinEngagement.twin_id == twin_id)
            .order_by(TwinEngagement.started_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Instantiate CRUD classes
digital_twin = CRUDDigitalTwin()
network_topology = CRUDNetworkTopology()
twin_engagement = CRUDTwinEngagement()









