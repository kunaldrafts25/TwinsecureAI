"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

# Make CRUD functions easily importable
from .alert import get_count_by_severity, get_count_by_status, get_multi
from .crud_alert import alert
from .crud_report import report
from .crud_user import user
