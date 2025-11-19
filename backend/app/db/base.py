"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

SQLAlchemy base class for declarative ORM models.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# SQLAlchemy naming convention for constraints
# This ensures consistent, readable constraint names in the database
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Base class for all ORM models
# All database models inherit from this
Base = declarative_base(metadata=metadata)
