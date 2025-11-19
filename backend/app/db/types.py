"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Custom database types for cross-database compatibility.
"""

import json

from sqlalchemy.dialects.postgresql import ARRAY as PostgresARRAY
from sqlalchemy.dialects.postgresql import INET as PostgresINET
from sqlalchemy.dialects.postgresql import JSONB as PostgresJSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import JSON, String, Text, TypeDecorator


class JSONB(TypeDecorator):
    """
    Platform-independent JSONB type.
    
    Uses PostgreSQL's JSONB when available, otherwise falls back to JSON.
    This allows the same models to work with both PostgreSQL and SQLite.
    """
    
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresJSONB())
        return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value
    
    def process_result_value(self, value, dialect):
        return value


class INET(TypeDecorator):
    """
    Platform-independent INET type.
    
    Uses PostgreSQL's INET when available, otherwise falls back to String.
    This allows storing IP addresses across different databases.
    """
    
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresINET())
        return dialect.type_descriptor(String(50))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)
    
    def process_result_value(self, value, dialect):
        return value


class ARRAY(TypeDecorator):
    """
    Platform-independent ARRAY type.
    
    Uses PostgreSQL's ARRAY when available, otherwise falls back to JSON stored as Text.
    This allows using arrays across different databases.
    """
    
    impl = Text
    cache_ok = True
    
    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type
    
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresARRAY(self.item_type))
        return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.loads(value)


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.
    
    Uses PostgreSQL's UUID when available, otherwise falls back to String(36).
    This allows using UUIDs across different databases.
    """
    
    impl = String
    cache_ok = True
    
    def __init__(self, as_uuid=False):
        super().__init__(36)
        self.as_uuid = as_uuid
    
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresUUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # For SQLite, convert UUID to string
        if hasattr(value, 'hex'):
            return str(value)
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and self.as_uuid:
            return value
        # For SQLite, we get strings, convert to UUID if needed
        if self.as_uuid and isinstance(value, str):
            import uuid
            return uuid.UUID(value)
        return value
