"""
Unified Analysis API
Single endpoint for complete financial analysis
Orchestrates all engines through financial_engine
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import logging

from app.db.database import get_db
from app.models import User, Expense
from app.routes.user import get_current_user
from app.services.financial_engine import analyze_finances

logger = logging.getLogger(__name__)

router = APIRouter(tags=["unified-analysis"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UserProfileInput(BaseModel):
    """User financial profile input"""
    monthly_income: float = Field(..., gt=0, description="Monthly income in ₹")
    emi_amount: float = Field(default=0, ge=0, description="Monthly EMI payment")
    medical_risk: str = Field(default="low", pattern="^(low|medium|high)$")
    family_dependency: int = Field(default=0, ge=0, le=10)
    has_emergency_fund: bool = Field(default=False)


class ExpenseInput(BaseModel):
    """Expense input"""
    category: str
    amount: float = Field(..., gt=0)
    note: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """Complete analysis request"""
    user_profile: UserProfileInput
    expenses: Optional[List[ExpenseInput]] = None
    use_current_month: bool = Field(
        default=True,
        description="If true, fetch expenses from database for current month"
    )


class AnalyzeResponse(BaseModel):
    """Structured analysis response - UI-friendly"""
    
    # Risk assessment
    risk_level: str  # low, medium, high, critical
    risk_score: int  # 0-100
    
    # Inflation context
    inflation: Dict  # {pressure, value, status}
    
    # Spending breakdown
    allocation: Dict  # {fixed, essential, lifestyle, savings} as percentages
    amounts: Dict  # Actual ₹ amounts
    spending_status: Dict  # {fixed: "normal", essential: "high", ...}
    
    # Issues detected
    violations: List[Dict]  # Structured violations
    money_leaks: List[Dict]  # Categories overspending
    
    # Actionable output
    recommendations: List[str]  # Top 5 specific actions
    priority_actions: List[str]  # Top 3 urgent actions
    
    # Cost optimization
    optimization_opportunities: List[Dict]  # Max 2 targeted savings
    
    # Targets
    adjusted_thresholds: Dict  # Inflation-adjusted targets
    
    # Metrics
    survival_months: float
    total_monthly_spending: float
    
    # Metadata
    analysis_date: str
    data_quality: str  # "complete", "partial", "estimated"


# ============================================================================
# MAIN ENDPOINT
# ============================================================================

@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_financial_health(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UNIFIED FINANCIAL ANALYSIS ENDPOINT
    
    Single source of truth for all financial analysis
    Orchestrates: rule_engine, inflation_engine, optimizer, deals_service
    
    Flow:
    1. Validate input
    2. Fetch/use expenses
    3. Call financial_engine.analyze_finances()
    4. Format response for UI
    
    Returns:
    - Structured, actionable insights
    - UI-friendly format
    - Complete financial picture
    """
    try:
        logger.info(f"[Analyze] Starting analysis for user {current_user.id}")
        
        # Step 1: Get expenses
        if request.use_current_month:
            # Fetch from database
            now = datetime.now()
            current_month = now.strftime("%Y-%m")
            
            expenses_db = db.query(Expense).filter(
                Expense.user_id == current_user.id,
                func.to_char(Expense.date, 'YYYY-MM') == current_month
            ).all()
            
            expense_list = [
                {
                    "category": exp.category,
                    "amount": exp.amount,
                    "note": exp.note or ""
                }
                for exp in expenses_db
            ]
            
            logger.info(f"[Analyze] Fetched {len(expense_list)} expenses from database")
        else:
            # Use provided expenses
            expense_list = [
                {
                    "category": exp.category,
                    "amount": exp.amount,
                    "note": exp.note or ""
                }
                for exp in (request.expenses or [])
            ]
            
            logger.info(f"[Analyze] Using {len(expense_list)} provided expenses")
        
        # Step 2: Run unified financial analysis
        logger.info("[Analyze] Calling financial_engine.analyze_finances()")
        
        decision = analyze_finances(
            monthly_income=request.user_profile.monthly_income,
            expenses=expense_list,
            db=db,
            emi_amount=request.user_profile.emi_amount,
            medical_risk=request.user_profile.medical_risk,
            family_dependency=request.user_profile.family_dependency,
            has_emergency_fund=request.user_profile.has_emergency_fund
        )
        
        logger.info(f"[Analyze] Analysis complete - Risk: {decision.risk_level}, Score: {decision.risk_score}")
        
        # Step 3: Calculate spending status for UI
        spending_status = {
            "fixed": "high" if decision.percentages["fixed"] > 50 else "normal",
            "essential": "high" if decision.percentages["essential"] > decision.adjusted_thresholds["essential"] else "normal",
            "lifestyle": "high" if decision.percentages["lifestyle"] > decision.adjusted_thresholds["lifestyle"] else "normal",
            "savings": "low" if decision.percentages.get("savings", 0) < decision.adjusted_thresholds["savings"] else "good"
        }
        
        # Step 4: Calculate total spending
        total_spending = sum(decision.amounts.values()) - decision.amounts.get("savings", 0)
        
        # Step 5: Determine data quality
        data_quality = "complete" if len(expense_list) > 0 else "estimated"
        if len(expense_list) > 0 and len(expense_list) < 5:
            data_quality = "partial"
        
        # Step 6: Format response
        response = AnalyzeResponse(
            risk_level=decision.risk_level,
            risk_score=decision.risk_score,
            inflation=decision.inflation,
            allocation=decision.percentages,
            amounts=decision.amounts,
            spending_status=spending_status,
            violations=decision.violations,
            money_leaks=decision.money_leaks,
            recommendations=decision.recommendations,
            priority_actions=decision.priority_actions,
            optimization_opportunities=decision.optimization_opportunities,
            adjusted_thresholds=decision.adjusted_thresholds,
            survival_months=decision.survival_months,
            total_monthly_spending=round(total_spending, 2),
            analysis_date=datetime.now().isoformat(),
            data_quality=data_quality
        )
        
        logger.info("[Analyze] Response formatted successfully")
        
        return response
    
    except Exception as e:
        logger.error(f"[Analyze] Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@router.get("/api/analyze/quick")
async def quick_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick financial health check
    
    Uses user profile from database + current month expenses
    Faster than full analysis - good for dashboard
    """
    try:
        # Get user income from profile or use default
        monthly_income = current_user.income or 50000
        
        # Get current month expenses
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            func.to_char(Expense.date, 'YYYY-MM') == current_month
        ).all()
        
        expense_list = [
            {"category": exp.category, "amount": exp.amount, "note": exp.note or ""}
            for exp in expenses
        ]
        
        # Run analysis
        decision = analyze_finances(
            monthly_income=monthly_income,
            expenses=expense_list,
            db=db,
            medical_risk=current_user.medical_risk or "low",
            family_dependency=current_user.dependents or 0
        )
        
        # Return simplified response
        return {
            "risk_level": decision.risk_level,
            "risk_score": decision.risk_score,
            "savings_rate": decision.percentages.get("savings", 0),
            "survival_months": decision.survival_months,
            "top_actions": decision.priority_actions,
            "inflation_pressure": decision.inflation["pressure"],
            "total_spending": sum(decision.amounts.values()) - decision.amounts.get("savings", 0)
        }
    
    except Exception as e:
        logger.error(f"[Quick Analysis] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analyze/status")
async def analysis_status():
    """
    Check if analysis system is operational
    """
    try:
        # Test imports
        from app.services.financial_engine import FinancialDecisionEngine
        from app.services.rule_engine import RuleEngine
        from app.services.inflation_engine import adjust_budget_thresholds
        from app.services.optimizer import OptimizationEngine
        from app.services.deals_service import CostOptimizationService
        
        return {
            "status": "operational",
            "engines": {
                "financial_engine": "active",
                "rule_engine": "active",
                "inflation_engine": "active",
                "optimizer": "active",
                "cost_optimization": "active"
            },
            "version": "3.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
