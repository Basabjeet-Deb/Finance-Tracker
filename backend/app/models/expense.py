"""Expense and Budget models"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="expenses")


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monthly_budget = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # Format: YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")


class CPIData(Base):
    __tablename__ = "cpi_data"
    
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, unique=True, nullable=False)  # Format: YYYY-MM
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FuelData(Base):
    __tablename__ = "fuel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    petrol_price = Column(Float, nullable=False)
    diesel_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
