# app/api/api_v1/endpoints/__init__.py

from .auth import router as auth # Example import
from .users import users # <-- Make sure this line exists and is correct
from .alerts import router as alerts # Example import
# ... import other routers ...
from .system import router as system # Example import
from .honeypot import router as honeypot # Example import
from .reports import router as reports # Example import


# You might also list them in __all__ if you use that pattern
# __all__ = ["auth", "users", "alerts", "reports", "honeypot", "system"]