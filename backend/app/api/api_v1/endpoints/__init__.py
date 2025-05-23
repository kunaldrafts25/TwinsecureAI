"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

# app/api/api_v1/endpoints/__init__.py

from .alerts import router as alerts
from .auth import router as auth
from .dashboard import router as dashboard
from .honeypot import router as honeypot
from .reports import router as reports
from .system import router as system
from .users import users

# List all modules in __all__ for better imports
__all__ = ["auth", "users", "alerts", "reports", "honeypot", "system", "dashboard"]
