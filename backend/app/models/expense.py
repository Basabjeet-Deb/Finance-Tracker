"""Expense, Budget, CPI, Fuel, and Analysis History models - Supabase compatible"""
from sqlalchemy import Column, String, Float, Date, ForeignKey, DateTime, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core expense fields
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)  # New field
    type = Column(String(20), nullable=True, index=True)  # fixed, essential, lifestyle, savings
    
    # Additional fields
    date = Column(Date, nullable=False, index=True)
    note = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_user_type', 'user_id', 'type'),
    )


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_budget = Column(Float, nullable=False)
    month = Column(String(7), nullable=False, index=True)  # Format: YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    
    # Composite unique constraint
    __table_args__ = (
        Index('idx_user_month', 'user_id', 'month', unique=True),
    )


class CPIData(Base):
    __tablename__ = "cpi_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    month = Column(String(7), unique=True, nullable=False, index=True)  # Format: YYYY-MM
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FuelData(Base):
    __tablename__ = "fuel_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    petrol_price = Column(Float, nullable=False)
    diesel_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisHistory(Base):
    """Store financial analysis results for tracking over time"""
    __tablename__ = "analysis_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Analysis results
    score = Column(Integer, nullable=False)  # Risk score 0-100
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    savings_rate = Column(Float, nullable=False)  # Percentage
    
    # Detailed breakdown (stored as JSON)
    inflation_data = Column(JSON, nullable=True)
    percentages = Column(JSON, nullable=True)
    money_leaks = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="analysis_history")
    
    # Index for querying user's history
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )
