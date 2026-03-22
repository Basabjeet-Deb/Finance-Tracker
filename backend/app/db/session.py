"""
Database session management
Re-exports get_db() from database.py for clean imports
"""
from app.db.database import get_db

__all__ = ['get_db']
