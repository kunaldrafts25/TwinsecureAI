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
