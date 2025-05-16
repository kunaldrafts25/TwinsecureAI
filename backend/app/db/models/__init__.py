# Make models easily importable from the db.models package
# Import Base from base.py to ensure it's recognized
from app.db.base import Base

from .alert import Alert
from .report import Report
from .user import User
