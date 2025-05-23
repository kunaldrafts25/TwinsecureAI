"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

# Make models easily importable from the db.models package
# Import Base from base.py to ensure it's recognized
from app.db.base import Base

from .alert import Alert
from .report import Report
from .user import User
