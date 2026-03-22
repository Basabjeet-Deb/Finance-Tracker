"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List
from uuid import UUID


# ==================== User Schemas ====================
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ==================== Expense Schemas ====================
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: date
    note: Optional[str] = None


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[date] = None
    note: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    category: str
    date: date
    note: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== Budget Schemas ====================
class BudgetCreate(BaseModel):
    monthly_budget: float
    month: str


class BudgetResponse(BaseModel):
    id: UUID
    user_id: UUID
    monthly_budget: float
    month: str
    
    class Config:
        from_attributes = True


# ==================== Dashboard Schemas ====================
class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float


class DashboardResponse(BaseModel):
    monthly_total: float
    category_breakdown: List[CategoryBreakdown]
    daily_spending: List[dict]
    current_vs_last_month: dict
    budget_status: Optional[dict] = None


# ==================== Insight Schemas ====================
class InsightResponse(BaseModel):
    insights: List[str]


# ==================== External Data Schemas ====================
class CPIDataResponse(BaseModel):
    month: str
    value: float
    
    class Config:
        from_attributes = True


class FuelDataResponse(BaseModel):
    date: date
    petrol_price: float
    diesel_price: float
    
    class Config:
        from_attributes = True
