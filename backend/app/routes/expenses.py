"""
Expense Management Routes
CRUD operations for expenses and budgets
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.db.database import get_db
from app.models import User, Expense, Budget
from app.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    BudgetCreate, BudgetResponse,
    DashboardResponse, CategoryBreakdown
)
from app.routes.user import get_current_user

router = APIRouter(tags=["expenses"])


# ==================== Expense Routes ====================

@router.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for current user"""
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).order_by(Expense.date.desc()).offset(skip).limit(limit).all()
    return expenses


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    new_expense = Expense(
        user_id=current_user.id,
        amount=expense_data.amount,
        category=expense_data.category,
        date=expense_data.date,
        note=expense_data.note
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update fields
    if expense_data.amount is not None:
        expense.amount = expense_data.amount
    if expense_data.category is not None:
        expense.category = expense_data.category
    if expense_data.date is not None:
        expense.date = expense_data.date
    if expense_data.note is not None:
        expense.note = expense_data.note
    
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return None


# ==================== Budget Routes ====================

@router.post("/budget", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update budget for a month"""
    # Check if budget exists for this month
    existing_budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == budget_data.month
    ).first()
    
    if existing_budget:
        existing_budget.monthly_budget = budget_data.monthly_budget
        db.commit()
        db.refresh(existing_budget)
        return existing_budget
    else:
        new_budget = Budget(
            user_id=current_user.id,
            monthly_budget=budget_data.monthly_budget,
            month=budget_data.month
        )
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        return new_budget


@router.get("/budget/{month}", response_model=BudgetResponse)
def get_budget(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget for a specific month"""
    budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == month
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found for this month")
    
    return budget


# ==================== Dashboard Route ====================

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data with spending analytics"""
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    last_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    
    # Monthly total
    monthly_total = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y-%m', Expense.date) == current_month
    ).scalar() or 0
    
    # Category breakdown
    category_data = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y-%m', Expense.date) == current_month
    ).group_by(Expense.category).all()
    
    category_breakdown = [
        CategoryBreakdown(
            category=cat.category,
            amount=cat.total,
            percentage=(cat.total / monthly_total * 100) if monthly_total > 0 else 0
        )
        for cat in category_data
    ]
    
    # Daily spending
    daily_data = db.query(
        Expense.date,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y-%m', Expense.date) == current_month
    ).group_by(Expense.date).order_by(Expense.date).all()
    
    daily_spending = [
        {"date": str(day.date), "amount": day.total}
        for day in daily_data
    ]
    
    # Current vs last month
    last_month_total = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y-%m', Expense.date) == last_month
    ).scalar() or 0
    
    change_pct = 0
    if last_month_total > 0:
        change_pct = ((monthly_total - last_month_total) / last_month_total) * 100
    
    current_vs_last_month = {
        "current_month": monthly_total,
        "last_month": last_month_total,
        "change_percentage": change_pct
    }
    
    # Budget status
    budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == current_month
    ).first()
    
    budget_status = None
    if budget:
        used_pct = (monthly_total / budget.monthly_budget * 100) if budget.monthly_budget > 0 else 0
        budget_status = {
            "monthly_budget": budget.monthly_budget,
            "spent": monthly_total,
            "remaining": budget.monthly_budget - monthly_total,
            "percentage_used": used_pct,
            "status": "exceeded" if used_pct > 100 else "warning" if used_pct > 80 else "good"
        }
    
    return DashboardResponse(
        monthly_total=monthly_total,
        category_breakdown=category_breakdown,
        daily_spending=daily_spending,
        current_vs_last_month=current_vs_last_month,
        budget_status=budget_status
    )
