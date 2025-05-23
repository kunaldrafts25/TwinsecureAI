"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# SQLAlchemy recommends using a naming convention for constraints
# See: [https://alembic.sqlalchemy.org/en/latest/naming.html](https://alembic.sqlalchemy.org/en/latest/naming.html)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create a metadata object with the naming convention
metadata = MetaData(naming_convention=convention)

# Create a base class for declarative class definitions
# All database models will inherit from this class.
# The metadata object is passed here.
Base = declarative_base(metadata=metadata)

# You can also define a BaseQuery class here if needed for custom query methods,
# though it's less common with the async session pattern.
