"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

"""
Enum definitions for database models.
"""

import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"


class UserStatus(str, enum.Enum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
