"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

API endpoints for Digital Twin management.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_user
from app.db import crud
from app.db.models import DigitalTwin, NetworkTopology, User
from app.db.session import get_db
from app.schemas.digital_twin import (
    DigitalTwin as DigitalTwinSchema,
    DigitalTwinCreate,
    DigitalTwinUpdate,
    NetworkTopology as NetworkTopologySchema,
    NetworkTopologyCreate,
    TwinEngagement,
    TwinEngagementCreate,
)

router = APIRouter()


@router.get("/", response_model=list[DigitalTwinSchema])
async def list_digital_twins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None),
    is_honeypot: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """List all digital twins with optional filtering."""
    logger.info(f"User {current_user.email} listing digital twins")
    
    twins = await crud.digital_twin.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        is_honeypot=is_honeypot,
    )
    
    return twins


@router.get("/{twin_id}", response_model=DigitalTwinSchema)
async def get_digital_twin(
    twin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a specific digital twin by ID."""
    logger.info(f"User {current_user.email} fetching digital twin {twin_id}")
    
    twin = await crud.digital_twin.get(db=db, twin_id=twin_id)
    
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital twin not found"
        )
    
    return twin


@router.post("/", response_model=DigitalTwinSchema, status_code=status.HTTP_201_CREATED)
async def create_digital_twin(
    twin_in: DigitalTwinCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new digital twin."""
    logger.info(f"User {current_user.email} creating digital twin: {twin_in.name}")
    
    twin = await crud.digital_twin.create(
        db=db,
        obj_in=twin_in,
        created_by_id=current_user.id
    )
    
    logger.info(f"Digital twin created: {twin.id}")
    return twin


@router.patch("/{twin_id}", response_model=DigitalTwinSchema)
async def update_digital_twin(
    twin_id: UUID,
    twin_in: DigitalTwinUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update an existing digital twin."""
    logger.info(f"User {current_user.email} updating digital twin {twin_id}")
    
    twin = await crud.digital_twin.get(db=db, twin_id=twin_id)
    
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital twin not found"
        )
    
    updated_twin = await crud.digital_twin.update(
        db=db,
        db_obj=twin,
        obj_in=twin_in
    )
    
    return updated_twin


@router.delete("/{twin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_digital_twin(
    twin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete a digital twin."""
    logger.info(f"User {current_user.email} deleting digital twin {twin_id}")
    
    twin = await crud.digital_twin.delete(db=db, twin_id=twin_id)
    
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital twin not found"
        )


@router.get("/{twin_id}/topology", response_model=list[NetworkTopologySchema])
async def get_twin_topology(
    twin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get network topology connections for a digital twin."""
    logger.info(f"User {current_user.email} fetching topology for twin {twin_id}")
    
    connections = await crud.network_topology.get_by_twin(db=db, twin_id=twin_id)
    return connections


@router.post("/topology", response_model=NetworkTopologySchema, status_code=status.HTTP_201_CREATED)
async def create_topology_connection(
    topology_in: NetworkTopologyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a network topology connection between twins."""
    logger.info(f"User {current_user.email} creating topology connection")
    
    connection = await crud.network_topology.create(db=db, obj_in=topology_in)
    return connection


@router.get("/{twin_id}/engagements", response_model=list[TwinEngagement])
async def get_twin_engagements(
    twin_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get engagement history for a digital twin."""
    logger.info(f"User {current_user.email} fetching engagements for twin {twin_id}")
    
    engagements = await crud.twin_engagement.get_by_twin(
        db=db,
        twin_id=twin_id,
        limit=limit
    )
    
    return engagements


@router.post("/{twin_id}/engagements", response_model=TwinEngagement, status_code=status.HTTP_201_CREATED)
async def create_twin_engagement(
    twin_id: UUID,
    engagement_in: TwinEngagementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new engagement record for a digital twin."""
    logger.info(f"User {current_user.email} creating engagement for twin {twin_id}")
    
    engagement_data = engagement_in.model_dump()
    engagement_data["twin_id"] = twin_id
    
    engagement = await crud.twin_engagement.create(
        db=db,
        obj_in=TwinEngagementCreate(**engagement_data)
    )
    
    twin = await crud.digital_twin.get(db=db, twin_id=twin_id)
    if twin:
        twin.engagement_count += 1
        twin.last_engagement = datetime.now(timezone.utc)
        db.add(twin)
        await db.commit()
    
    return engagement


@router.get("/network/topology", response_model=dict[str, Any])
async def get_network_topology(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Get network topology mapping of all digital twins and their connections.
    Creates a visual representation of the digital twin network.
    """
    logger.info(f"User {current_user.email} fetching network topology")
    
    twins_stmt = select(DigitalTwin).where(DigitalTwin.status == 'active')
    twins_result = await db.execute(twins_stmt)
    twins = twins_result.scalars().all()
    
    topology_stmt = select(NetworkTopology)
    topology_result = await db.execute(topology_stmt)
    connections = topology_result.scalars().all()
    
    nodes = []
    for twin in twins:
        node = {
            "id": str(twin.id),
            "label": twin.name or f"Twin {twin.id}",
            "type": "honeypot" if twin.is_honeypot else "production",
            "ip_address": str(twin.ip_address) if twin.ip_address else None,
            "status": twin.status,
            "engagement_count": twin.engagement_count,
            "last_engagement": twin.last_engagement.isoformat() if twin.last_engagement else None,
        }
        nodes.append(node)
    
    edges = []
    for conn in connections:
        edge = {
            "source": str(conn.source_twin_id),
            "target": str(conn.destination_twin_id),
            "protocol": conn.protocol,
            "port": conn.port,
            "connection_type": conn.connection_type,
        }
        edges.append(edge)
    
    total_twins = len(nodes)
    total_connections = len(edges)
    honeypots = sum(1 for n in nodes if n["type"] == "honeypot")
    production = total_twins - honeypots
    
    max_possible_connections = total_twins * (total_twins - 1) / 2
    network_density = (
        total_connections / max_possible_connections
        if max_possible_connections > 0
        else 0
    )
    
    return {
        "nodes": nodes,
        "edges": edges,
        "metrics": {
            "total_twins": total_twins,
            "total_connections": total_connections,
            "honeypots": honeypots,
            "production": production,
            "network_density": network_density,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/network/map/{twin_id}", response_model=dict[str, Any])
async def get_twin_network_map(
    twin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Get network map for a specific digital twin showing its connections and neighbors."""
    logger.info(f"User {current_user.email} fetching network map for twin {twin_id}")
    
    twin = await crud.digital_twin.get(db=db, twin_id=twin_id)
    
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital twin not found"
        )
    
    connections_stmt = select(NetworkTopology).where(
        (NetworkTopology.source_twin_id == twin_id) |
        (NetworkTopology.destination_twin_id == twin_id)
    )
    connections_result = await db.execute(connections_stmt)
    connections = connections_result.scalars().all()
    
    connected_twin_ids = set()
    for conn in connections:
        if conn.source_twin_id == twin_id:
            connected_twin_ids.add(conn.destination_twin_id)
        else:
            connected_twin_ids.add(conn.source_twin_id)
    
    connected_twins = []
    if connected_twin_ids:
        twins_stmt = select(DigitalTwin).where(DigitalTwin.id.in_(connected_twin_ids))
        twins_result = await db.execute(twins_stmt)
        connected_twins_list = twins_result.scalars().all()
        
        for ct in connected_twins_list:
            connected_twins.append({
                "id": str(ct.id),
                "name": ct.name,
                "ip_address": str(ct.ip_address) if ct.ip_address else None,
                "type": "honeypot" if ct.is_honeypot else "production",
            })
    
    return {
        "twin": {
            "id": str(twin.id),
            "name": twin.name,
            "ip_address": str(twin.ip_address) if twin.ip_address else None,
            "type": "honeypot" if twin.is_honeypot else "production",
            "status": twin.status,
        },
        "connections": [
            {
                "id": str(conn.id),
                "source": str(conn.source_twin_id),
                "target": str(conn.destination_twin_id),
                "protocol": conn.protocol,
                "port": conn.port,
                "connection_type": conn.connection_type,
            }
            for conn in connections
        ],
        "connected_twins": connected_twins,
        "metrics": {
            "total_connections": len(connections),
            "connected_twins_count": len(connected_twins),
        },
    }
