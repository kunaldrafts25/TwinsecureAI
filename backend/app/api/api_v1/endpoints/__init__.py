# app/api/api_v1/endpoints/__init__.py

from .auth import router as auth
from .users import users
from .alerts import router as alerts
from .system import router as system
from .honeypot import router as honeypot
from .reports import router as reports
from .dashboard import router as dashboard


# List all modules in __all__ for better imports
__all__ = ["auth", "users", "alerts", "reports", "honeypot", "system", "dashboard"]