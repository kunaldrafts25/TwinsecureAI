import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, DateTime, func, Enum, JSON, ForeignKey, Text, Integer, Index, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.types import JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from app.db.base import Base
from app.core.password import get_password_hash
from app.core.enums import UserRole, UserStatus

class User(Base):
    """
    Enhanced database model for users with advanced features.
    """
    __tablename__ = "users"
    __table_args__ = (
        # Add indexes for common queries
        # Create a composite unique index on email and role
        Index('ix_users_email_role', 'email', 'role', unique=True),
        {'postgresql_partition_by': 'LIST (role)'}  # Partition by role for better performance
    )

    # Primary key and basic info
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Email can't be unique by itself in a partitioned table - must include the partitioning column
    # The unique constraint is created as a composite index on (email, role)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True, nullable=True)

    # Enhanced user attributes
    # role is part of the primary key because it's used for partitioning
    role = Column(Enum(UserRole), primary_key=True, nullable=False, default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    department = Column(String, nullable=True)
    title = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Security and access control
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login_attempt = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    mfa_enabled = Column(Boolean(), default=False)
    mfa_secret = Column(String, nullable=True)

    # Preferences and settings
    preferences = Column(JSONB, default={})
    notification_settings = Column(JSONB, default={
        "email": True,
        "slack": False,
        "discord": False
    })

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    reports = relationship("Report", back_populates="creator", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="assigned_to", foreign_keys="[Alert.assigned_to_id]", cascade="all, delete-orphan", overlaps="assigned_alerts")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    # Validators
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        return email.lower()

    @validates('role')
    def validate_role(self, key, role):
        """Validate role assignment"""
        if self.is_superuser and role != UserRole.ADMIN:
            raise ValueError("Superuser must have admin role")
        return role

    # Hybrid properties
    @hybrid_property
    def is_locked(self) -> bool:
        """Check if user account is locked due to failed login attempts"""
        if self.failed_login_attempts >= 5:
            if self.last_login_attempt:
                lockout_time = datetime.now(timezone.utc) - self.last_login_attempt
                return lockout_time.total_seconds() < 1800  # 30 minutes lockout
        return False

    @hybrid_property
    def needs_password_change(self) -> bool:
        """Check if user needs to change password"""
        if not self.password_changed_at:
            return True
        password_age = datetime.now(timezone.utc) - self.password_changed_at
        return password_age.days >= 90  # 90 days password policy

    # Methods
    def set_password(self, password: str) -> None:
        """Set user password with hashing"""
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

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        return permission in self.preferences.get('permissions', [])

    def to_dict(self) -> dict:
        """Convert user object to dictionary"""
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'status': self.status.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"

class APIKey(Base):
    """
    Model for API keys associated with users.
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "user_role"],
            ["users.id", "users.role"],
        ),
    )

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

class AuditLog(Base):
    """
    Model for user activity audit logging.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "user_role"],
            ["users.id", "users.role"],
        ),
    )

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"