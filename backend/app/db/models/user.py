"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

User model definition with authentication and profile information.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from app.core.enums import UserRole, UserStatus
from app.core.password import get_password_hash
from app.db.base import Base
from app.db.types import JSONB


class User(Base):
    """User model with authentication and profile information"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER, index=True)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    department = Column(String, nullable=True)
    title = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    # Security
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login_attempt = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    
    # Settings
    preferences = Column(JSONB, default={})
    notification_settings = Column(
        JSONB, 
        default={"email": True, "slack": False, "discord": False}
    )
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    reports = relationship("Report", back_populates="creator", foreign_keys="[Report.created_by_id]")
    alerts = relationship("Alert", back_populates="assigned_to", foreign_keys="[Alert.assigned_to_id]")
    created_twins = relationship("DigitalTwin", back_populates="creator", foreign_keys="[DigitalTwin.created_by_id]")
    
    # Validators
    @validates("email")
    def validate_email(self, key, email):
        """Validate and normalize email"""
        if not email or "@" not in email:
            raise ValueError("Invalid email format")
        return email.lower()
    
    # Hybrid properties
    @hybrid_property
    def is_locked(self) -> bool:
        """Check if account is locked due to failed login attempts"""
        if self.failed_login_attempts >= 5:
            if self.last_login_attempt:
                lockout_time = datetime.now(timezone.utc) - self.last_login_attempt
                return lockout_time.total_seconds() < 1800  # 30 minutes lockout
        return False
    
    @hybrid_property
    def needs_password_change(self) -> bool:
        """Check if password needs to be changed (90 day policy)"""
        if not self.password_changed_at:
            return True
        password_age = datetime.now(timezone.utc) - self.password_changed_at
        return password_age.days >= 90
    
    # Methods
    def set_password(self, password: str) -> None:
        """Hash and set user password"""
        self.hashed_password = get_password_hash(password)
        self.password_changed_at = datetime.now(timezone.utc)
        self.failed_login_attempts = 0
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        self.last_login_attempt = datetime.now(timezone.utc)
    
    def reset_failed_login(self) -> None:
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.last_login_attempt = None
    
    def __repr__(self):
        return f"<User {self.email}>"
