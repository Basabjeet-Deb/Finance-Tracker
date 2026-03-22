"""User model - Supabase Auth compatible"""
from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    # Core fields - id syncs with Supabase Auth user id
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Financial profile fields
    income = Column(Float, nullable=True)  # Monthly income
    dependents = Column(Integer, default=0, nullable=False)  # Number of dependents
    medical_risk = Column(String(20), default='low', nullable=False)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    analysis_history = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")
