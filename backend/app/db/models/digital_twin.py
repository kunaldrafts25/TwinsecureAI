"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Digital Twin models for network topology and honeypot management.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import ARRAY, JSONB


class DigitalTwinType(str, enum.Enum):
    """Types of digital twins"""
    
    SERVER = "server"
    NETWORK = "network"
    APPLICATION = "application"
    DATABASE = "database"
    CONTAINER = "container"
    IOT_DEVICE = "iot_device"
    CUSTOM = "custom"


class DigitalTwinStatus(str, enum.Enum):
    """Status of digital twin"""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPLOYING = "deploying"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class HoneypotType(str, enum.Enum):
    """Types of honeypots"""
    
    LOW_INTERACTION = "low_interaction"
    MEDIUM_INTERACTION = "medium_interaction"
    HIGH_INTERACTION = "high_interaction"
    PRODUCTION = "production"


class DigitalTwin(Base):
    """Digital Twin model representing a virtual replica of a network asset"""
    
    __tablename__ = "digital_twins"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    twin_type = Column(Enum(DigitalTwinType), nullable=False, index=True)
    status = Column(Enum(DigitalTwinStatus), default=DigitalTwinStatus.INACTIVE, index=True)
    
    # Network configuration
    ip_address = Column(INET, nullable=True, index=True)
    ip_addresses = Column(ARRAY(INET), nullable=True)
    mac_address = Column(String(17), nullable=True)
    hostname = Column(String(255), nullable=True, index=True)
    domain = Column(String(255), nullable=True)
    
    # Network topology
    network_segment = Column(String(100), nullable=True)
    vlan_id = Column(Integer, nullable=True)
    subnet = Column(String(18), nullable=True)
    gateway = Column(INET, nullable=True)
    dns_servers = Column(ARRAY(INET), nullable=True)
    
    # Services and ports
    exposed_ports = Column(ARRAY(Integer), nullable=True)
    services = Column(ARRAY(String), nullable=True)
    protocols = Column(ARRAY(String), nullable=True)
    
    # Operating system and software
    os_type = Column(String(50), nullable=True)
    os_version = Column(String(100), nullable=True)
    software_stack = Column(JSONB, nullable=True)
    
    # Honeypot configuration
    is_honeypot = Column(Boolean, default=False, index=True)
    honeypot_type = Column(Enum(HoneypotType), nullable=True)
    vulnerability_level = Column(String(20), nullable=True)
    deception_techniques = Column(ARRAY(String), nullable=True)
    
    # Configuration and metadata
    configuration = Column(JSONB, nullable=True)
    config_metadata = Column("metadata", JSONB, nullable=True)  # "metadata" is reserved in SQLAlchemy, use config_metadata as attribute name
    tags = Column(ARRAY(String), nullable=True)
    
    # Self-referential relationship
    parent_twin_id = Column(UUID(as_uuid=True), ForeignKey("digital_twins.id"), nullable=True)
    parent_twin = relationship("DigitalTwin", remote_side=[id], back_populates="child_twins")
    child_twins = relationship("DigitalTwin", back_populates="parent_twin")
    
    # Metrics and monitoring
    metrics = Column(JSONB, nullable=True)
    last_metrics_update = Column(DateTime(timezone=True), nullable=True)
    
    # Engagement tracking
    engagement_count = Column(Integer, default=0)
    last_engagement = Column(DateTime(timezone=True), nullable=True)
    total_attacks_detected = Column(Integer, default=0)
    total_alerts_generated = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # Created by
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="created_twins")
    
    # Relationships
    outgoing_connections = relationship("NetworkTopology", foreign_keys="[NetworkTopology.source_twin_id]", back_populates="source_twin")
    incoming_connections = relationship("NetworkTopology", foreign_keys="[NetworkTopology.destination_twin_id]", back_populates="destination_twin")
    engagements = relationship("TwinEngagement", back_populates="twin", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DigitalTwin {self.name} ({self.twin_type.value})>"


class NetworkTopology(Base):
    """Network topology model for mapping relationships between digital twins"""
    
    __tablename__ = "network_topology"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source and destination twins
    source_twin_id = Column(UUID(as_uuid=True), ForeignKey("digital_twins.id"), nullable=False, index=True)
    destination_twin_id = Column(UUID(as_uuid=True), ForeignKey("digital_twins.id"), nullable=False, index=True)
    
    # Connection details
    connection_type = Column(String(50), nullable=True)
    protocol = Column(String(20), nullable=True)
    ports = Column(ARRAY(Integer), nullable=True)
    bandwidth = Column(Integer, nullable=True)
    latency = Column(Integer, nullable=True)
    
    # Metadata
    config_metadata = Column("metadata", JSONB, nullable=True)  # "metadata" is reserved in SQLAlchemy, use config_metadata as attribute name
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    source_twin = relationship("DigitalTwin", foreign_keys=[source_twin_id], back_populates="outgoing_connections")
    destination_twin = relationship("DigitalTwin", foreign_keys=[destination_twin_id], back_populates="incoming_connections")
    
    def __repr__(self):
        return f"<NetworkTopology {self.source_twin_id} -> {self.destination_twin_id}>"


class TwinEngagement(Base):
    """Tracks engagements (attacks/interactions) with digital twins"""
    
    __tablename__ = "twin_engagements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Twin reference
    twin_id = Column(UUID(as_uuid=True), ForeignKey("digital_twins.id"), nullable=False, index=True)
    twin = relationship("DigitalTwin", back_populates="engagements")
    
    # Attacker information
    attacker_ip = Column(INET, nullable=False, index=True)
    attacker_country = Column(String(2), nullable=True)
    attacker_asn = Column(String(20), nullable=True)
    
    # Engagement details
    engagement_type = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Attack details
    attack_vector = Column(String(100), nullable=True)
    payload = Column(JSONB, nullable=True)
    response_actions = Column(ARRAY(String), nullable=True)
    
    # Alert reference
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True)
    alert = relationship("Alert")
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TwinEngagement {self.id} on Twin {self.twin_id}>"
