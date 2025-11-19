"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Pydantic schemas for Digital Twin operations.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DigitalTwinBase(BaseModel):
    """Base schema for Digital Twin."""
    
    name: str = Field(..., description="Name of the digital twin")
    description: str | None = None
    twin_type: str = Field(..., description="Type of digital twin")
    ip_address: str | None = None
    hostname: str | None = None
    network_segment: str | None = None
    exposed_ports: list[int] | None = None
    services: list[str] | None = None
    is_honeypot: bool = False
    honeypot_type: str | None = None
    vulnerability_level: str | None = None
    configuration: dict[str, Any] | None = None


class DigitalTwinCreate(DigitalTwinBase):
    """Schema for creating a digital twin."""
    pass


class DigitalTwinUpdate(BaseModel):
    """Schema for updating a digital twin."""
    
    name: str | None = None
    description: str | None = None
    status: str | None = None
    ip_address: str | None = None
    metrics: dict[str, Any] | None = None
    configuration: dict[str, Any] | None = None


class DigitalTwin(DigitalTwinBase):
    """Schema for Digital Twin response."""
    
    id: UUID
    status: str
    engagement_count: int = 0
    total_attacks_detected: int = 0
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class NetworkTopologyCreate(BaseModel):
    """Schema for creating network topology connection."""
    
    source_twin_id: UUID
    destination_twin_id: UUID
    connection_type: str | None = None
    protocol: str | None = None
    ports: list[int] | None = None


class NetworkTopology(BaseModel):
    """Schema for network topology response."""
    
    id: UUID
    source_twin_id: UUID
    destination_twin_id: UUID
    connection_type: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TwinEngagementCreate(BaseModel):
    """Schema for creating twin engagement."""
    
    twin_id: UUID
    attacker_ip: str
    engagement_type: str
    severity: str
    attack_vector: str | None = None
    payload: dict[str, Any] | None = None


class TwinEngagement(BaseModel):
    """Schema for twin engagement response."""
    
    id: UUID
    twin_id: UUID
    attacker_ip: str
    engagement_type: str
    severity: str
    started_at: datetime
    ended_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

