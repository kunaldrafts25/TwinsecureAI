"""
Custom database types and type adapters.
This module provides custom database types and type adapters for SQLAlchemy.
"""

import json

from sqlalchemy.dialects.postgresql import ARRAY as PostgresARRAY
from sqlalchemy.dialects.postgresql import INET as PostgresINET
from sqlalchemy.dialects.postgresql import JSONB as PostgresJSONB
from sqlalchemy.types import JSON, String, Text, TypeDecorator


class JSONB(TypeDecorator):
    """
    Platform-independent JSONB type.

    Uses PostgreSQL's JSONB type when available, otherwise falls back to JSON.
    This allows the same models to work with both PostgreSQL and SQLite.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresJSONB())
        else:
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

    Uses PostgreSQL's INET type when available, otherwise falls back to String.
    This allows the same models to work with both PostgreSQL and SQLite.
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresINET())
        else:
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

    Uses PostgreSQL's ARRAY type when available, otherwise falls back to JSON stored as Text.
    This allows the same models to work with both PostgreSQL and SQLite.
    """

    impl = Text
    cache_ok = True

    def __init__(self, item_type):
        super(ARRAY, self).__init__()
        self.item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresARRAY(self.item_type))
        else:
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
