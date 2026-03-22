"""
Financial Analysis Routes
Rule-based financial engine and insights
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

from app.db.database import get_db
from app.models import User, Expense, Budget
from app.schemas import InsightResponse
from app.routes.user import get_current_user
from app.services.rule_engine import (
    FinancialProfile, CategorizationEngine, ConstraintBuilder, RuleEngine
)
from app.services.cpi_service import get_latest_cpi, get_all_cpi_with_inflation
from app.services.inflation_engine import (
    get_inflation_pressure,
    adjust_budget_thresholds,
    get_inflation_adjusted_analysis
)
from app.services.deals_service import DealsService
from app.services.rbi_service import RBIService
from app.services.fuel_service import FuelService

router = APIRouter(tags=["analysis"])


@router.get("/financial-analysis")
def get_financial_analysis(
    monthly_income: float,
    emi_amount: float = 0,
    medical_risk: str = "low",
    family_dependency: int = 0,
    has_emergency_fund: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive financial analysis using rule-based optimization engine
    with inflation-adjusted decision making
    """
    try:
        # Get user's expenses for current month
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            func.strftime('%Y-%m', Expense.date) == current_month
        ).all()
        
        # Convert to dict format
        expense_list = [
            {
                "category": exp.category,
                "amount": exp.amount,
                "note": exp.note or ""
            }
            for exp in expenses
        ]
        
        # Categorize expenses
        spending = CategorizationEngine.aggregate_spending(expense_list)
        
        # Convert SpendingData to dict for calculations
        spending_dict = {
            "fixed": spending.fixed,
            "essential": spending.essential,
            "lifestyle": spending.lifestyle,
            "savings": spending.savings,
            "unexpected": spending.unexpected
        }
        
        # Calculate current allocation
        current_allocation = RuleEngine.calculate_allocation(spending_dict, monthly_income)
        
        # Get inflation-adjusted analysis
        inflation_analysis = get_inflation_adjusted_analysis(
            db,
            expense_list,
            monthly_income,
            current_allocation
        )
        
        # Use inflation-adjusted thresholds
        adjusted_thresholds = inflation_analysis["adjusted_thresholds"]
        
        # Convert SpendingData to flat dict for external services
        flat_spending_dict = {}
        for cat_dict in [spending.fixed, spending.essential, spending.lifestyle, spending.savings, spending.unexpected]:
            flat_spending_dict.update(cat_dict)
        
        # Fetch external metrics with error handling
        try:
            deals = DealsService.get_deals_for_user(flat_spending_dict)
        except Exception as e:
            print(f"Deals service error: {e}")
            deals = []
            
        try:
            emi_impact = RBIService.calculate_emi_impact(emi_amount)
        except Exception as e:
            print(f"RBI service error: {e}")
            emi_impact = {"current_repo_rate": None, "projected_emi_increase": 0, "alert_message": "Error fetching RBI data"}
            
        try:
            fuel_impact = FuelService.calculate_fuel_impact(flat_spending_dict.get("Transport", 0))
        except Exception as e:
            print(f"Fuel service error: {e}")
            fuel_impact = {"current_avg_petrol_price": None, "metro_prices": {}, "insight": "Error fetching fuel data"}

        # Combine insights
        combined_insights = {
            "risk_level": inflation_analysis["risk_level"],
            "risk_score": inflation_analysis["risk_score"],
            "savings_rate": round(current_allocation.get("savings", 0), 1),
            "inflation": inflation_analysis["inflation"],
            "adjusted_thresholds": adjusted_thresholds,
            "impacted_categories": inflation_analysis["impacted_categories"],
            "spending_summary": {
                "fixed_obligations": {
                    "percentage": round(current_allocation.get("fixed", 0), 1),
                    "amount": round((current_allocation.get("fixed", 0) / 100) * monthly_income, 2),
                    "status": "high" if current_allocation.get("fixed", 0) > 50 else "normal"
                },
                "essentials": {
                    "percentage": round(current_allocation.get("essential", 0), 1),
                    "amount": round((current_allocation.get("essential", 0) / 100) * monthly_income, 2),
                    "status": "high" if current_allocation.get("essential", 0) > adjusted_thresholds["essential"] else "normal"
                },
                "lifestyle": {
                    "percentage": round(current_allocation.get("lifestyle", 0), 1),
                    "amount": round((current_allocation.get("lifestyle", 0) / 100) * monthly_income, 2),
                    "status": "high" if current_allocation.get("lifestyle", 0) > adjusted_thresholds["lifestyle"] else "normal"
                },
                "savings": {
                    "percentage": round(current_allocation.get("savings", 0), 1),
                    "amount": round((current_allocation.get("savings", 0) / 100) * monthly_income, 2),
                    "status": "low" if current_allocation.get("savings", 0) < adjusted_thresholds["savings"] else "good"
                }
            },
            "insights": inflation_analysis["insights"],
            "recommendations": inflation_analysis["recommendations"],
            "deals": deals,
            "emi_impact": emi_impact,
            "fuel_impact": fuel_impact
        }
        
        return combined_insights
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in financial_analysis: {str(e)}")
        print(error_trace)
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/financial-health")
def get_financial_health_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick financial health summary"""
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == current_month
    ).first()
    
    monthly_income = budget.monthly_budget * 1.5 if budget else 50000
    
    expenses = db.query(Expense).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y-%m', Expense.date) == current_month
    ).all()
    
    expense_list = [
        {"category": exp.category, "amount": exp.amount, "note": exp.note or ""}
        for exp in expenses
    ]
    
    spending = CategorizationEngine.aggregate_spending(expense_list)
    spending_dict = {
        "fixed": spending.fixed,
        "essential": spending.essential,
        "lifestyle": spending.lifestyle,
        "savings": spending.savings,
        "unexpected": spending.unexpected
    }
    
    current_allocation = RuleEngine.calculate_allocation(spending_dict, monthly_income)
    
    return {
        "monthly_income": monthly_income,
        "current_allocation": current_allocation,
        "total_expenses": sum(sum(cat.values()) for cat in spending_dict.values())
    }


@router.get("/insights", response_model=InsightResponse)
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get basic insights (legacy endpoint)"""
    return InsightResponse(insights=["Analysis available via /financial-analysis endpoint"])
