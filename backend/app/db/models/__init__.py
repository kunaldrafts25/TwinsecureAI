# Make models easily importable from the db.models package
from .user import User
from .alert import Alert
from .report import Report

# Import Base from base.py to ensure it's recognized
from app.db.base import Base
