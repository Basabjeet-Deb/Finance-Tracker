"""
Financial Analysis Routes
Uses the unified financial decision engine and saves analysis history
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.db.database import get_db
from app.models import User, Expense, AnalysisHistory
from app.routes.user import get_current_user
from app.services.financial_engine import analyze_finances
from app.services.deals_service import DealsService
from app.services.rbi_service import RBIService
from app.services.fuel_service import FuelService

router = APIRouter(tags=["analysis"])


@router.get("/financial-analysis")
def get_financial_analysis(
    monthly_income: float = None,
    emi_amount: float = 0,
    medical_risk: str = "low",
    family_dependency: int = 0,
    has_emergency_fund: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive financial analysis using unified decision engine
    
    Returns actionable insights with specific ₹ amounts
    Saves analysis to history for tracking
    """
    try:
        # Use user's income from profile if not provided
        if monthly_income is None:
            monthly_income = current_user.income or 50000
        
        # Use user's profile data
        medical_risk = current_user.medical_risk or medical_risk
        family_dependency = current_user.dependents or family_dependency
        
        # Get user's expenses for current month
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            func.to_char(Expense.date, 'YYYY-MM') == current_month
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
        
        # Run unified financial decision engine
        decision = analyze_finances(
            monthly_income=monthly_income,
            expenses=expense_list,
            db=db,
            emi_amount=emi_amount,
            medical_risk=medical_risk,
            family_dependency=family_dependency,
            has_emergency_fund=has_emergency_fund
        )
        
        # Save analysis to history
        try:
            analysis_record = AnalysisHistory(
                user_id=current_user.id,
                score=decision.risk_score,
                risk_level=decision.risk_level,
                savings_rate=decision.percentages.get("savings", 0),
                inflation_data=decision.inflation,
                percentages=decision.percentages,
                money_leaks=[
                    {
                        "category": leak.get("category"),
                        "amount": leak.get("amount"),
                        "percentage": leak.get("percentage"),
                        "reason": leak.get("reason"),
                        "message": leak.get("message")
                    }
                    for leak in decision.money_leaks
                ],
                recommendations=decision.recommendations
            )
            db.add(analysis_record)
            db.commit()
        except Exception as e:
            print(f"Could not save analysis history: {e}")
            # Continue even if history save fails
        
        # Fetch external market data (non-blocking, use cached/fallback)
        deals = []
        emi_impact = {"current_repo_rate": None, "projected_emi_increase": 0, "alert_message": ""}
        fuel_impact = {"current_avg_petrol_price": None, "metro_prices": {}, "insight": ""}
        
        # Skip external API calls for faster response
        # These can be loaded separately if needed
        
        # Format response
        return {
            "risk_level": decision.risk_level,
            "risk_score": decision.risk_score,
            "savings_rate": decision.percentages.get("savings", 0),
            
            # Inflation context
            "inflation": {
                "pressure": decision.inflation["pressure"],
                "value": decision.inflation["value"],
                "status": decision.inflation["status"]
            },
            
            # Spending breakdown
            "spending_summary": {
                "fixed_obligations": {
                    "percentage": decision.percentages["fixed"],
                    "amount": decision.amounts["fixed"],
                    "status": "high" if decision.percentages["fixed"] > 50 else "normal"
                },
                "essentials": {
                    "percentage": decision.percentages["essential"],
                    "amount": decision.amounts["essential"],
                    "status": "high" if decision.percentages["essential"] > decision.adjusted_thresholds["essential"] else "normal"
                },
                "lifestyle": {
                    "percentage": decision.percentages["lifestyle"],
                    "amount": decision.amounts["lifestyle"],
                    "status": "high" if decision.percentages["lifestyle"] > decision.adjusted_thresholds["lifestyle"] else "normal"
                },
                "savings": {
                    "percentage": decision.percentages.get("savings", 0),
                    "amount": decision.amounts.get("savings", 0),
                    "status": "low" if decision.percentages.get("savings", 0) < decision.adjusted_thresholds["savings"] else "good"
                }
            },
            
            # Issues (structured)
            "impacted_categories": decision.money_leaks,
            "violations": decision.violations,
            
            # Actions
            "recommendations": decision.recommendations,
            "priority_actions": decision.priority_actions,
            "insights": [v["message"] for v in decision.violations] + [
                leak.get("message", f"{leak['category']} spending is {leak['percentage']:.1f}% of income")
                for leak in decision.money_leaks[:3]
            ],
            
            # Cost optimization opportunities (NEW)
            "optimization_opportunities": decision.optimization_opportunities,
            
            # Targets
            "adjusted_thresholds": decision.adjusted_thresholds,
            
            # Survival metric
            "survival_months": decision.survival_months,
            
            # External data (deprecated - kept for backward compatibility)
            "deals": [],  # Deprecated: use optimization_opportunities instead
            "emi_impact": emi_impact,
            "fuel_impact": fuel_impact
        }
    
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
    """Quick financial health summary using decision engine"""
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
    
    # Use user's income or default
    monthly_income = current_user.income or 50000
    
    decision = analyze_finances(
        monthly_income=monthly_income,
        expenses=expense_list,
        db=db,
        medical_risk=current_user.medical_risk or "low",
        family_dependency=current_user.dependents or 0
    )
    
    return {
        "monthly_income": monthly_income,
        "risk_level": decision.risk_level,
        "risk_score": decision.risk_score,
        "savings_rate": decision.percentages.get("savings", 0),
        "survival_months": decision.survival_months,
        "top_actions": decision.priority_actions
    }


@router.get("/analysis-history")
def get_analysis_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's financial analysis history
    Shows how financial health has changed over time
    """
    history = db.query(AnalysisHistory).filter(
        AnalysisHistory.user_id == current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).limit(limit).all()
    
    return {
        "count": len(history),
        "history": [
            {
                "id": str(record.id),
                "score": record.score,
                "risk_level": record.risk_level,
                "savings_rate": record.savings_rate,
                "created_at": record.created_at.isoformat(),
                "inflation": record.inflation_data,
                "percentages": record.percentages
            }
            for record in history
        ]
    }

