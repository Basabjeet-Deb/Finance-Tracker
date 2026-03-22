"""
Inflation Decision Engine
Transforms CPI data into actionable financial logic for budget optimization
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
import logging

from app.services.cpi_service import get_latest_cpi, get_all_cpi_with_inflation

logger = logging.getLogger(__name__)


# Category sensitivity to inflation
SENSITIVITY = {
    "food": "high",
    "transport": "high", 
    "healthcare": "high",
    "rent": "medium",
    "utilities": "medium",
    "lifestyle": "low",
    "entertainment": "low",
    "shopping": "low"
}


def get_inflation_pressure(db: Session) -> Dict:
    """
    Calculate inflation pressure score from CPI data
    
    Returns:
        {
            "pressure": "low | medium | high",
            "value": float,  # YoY inflation %
            "score": int     # 0-100 normalized
        }
    """
    try:
        # Get CPI data with inflation metrics
        cpi_data = get_all_cpi_with_inflation(db, limit=2)
        
        if not cpi_data or len(cpi_data) < 1:
            logger.warning("No CPI data available")
            return {
                "pressure": "medium",
                "value": 5.0,
                "score": 50,
                "status": "estimated"
            }
        
        # Get latest inflation
        latest = cpi_data[-1]
        yoy_inflation = latest.get("year_over_year_inflation")
        
        if yoy_inflation is None:
            logger.warning("No YoY inflation data available")
            return {
                "pressure": "medium",
                "value": 5.0,
                "score": 50,
                "status": "estimated"
            }
        
        # Determine pressure level
        if yoy_inflation < 3:
            pressure = "low"
        elif yoy_inflation <= 6:
            pressure = "medium"
        else:
            pressure = "high"
        
        # Normalize to 0-100 score
        # Cap at 15% for normalization (15% = 100 score)
        score = min(int((yoy_inflation / 15.0) * 100), 100)
        
        return {
            "pressure": pressure,
            "value": round(yoy_inflation, 2),
            "score": score,
            "status": "actual",
            "date": latest.get("date")
        }
        
    except Exception as e:
        logger.error(f"Error calculating inflation pressure: {e}")
        return {
            "pressure": "medium",
            "value": 5.0,
            "score": 50,
            "status": "error"
        }


def adjust_budget_thresholds(inflation: Dict) -> Dict[str, float]:
    """
    Dynamically adjust budget thresholds based on inflation pressure
    
    Args:
        inflation: Dict from get_inflation_pressure()
    
    Returns:
        {
            "fixed": float,      # % of income
            "essential": float,  # % of income
            "lifestyle": float,  # % of income
            "savings": float     # % of income
        }
    """
    # Base thresholds
    thresholds = {
        "fixed": 50.0,
        "essential": 30.0,
        "lifestyle": 20.0,
        "savings": 20.0
    }
    
    pressure = inflation.get("pressure", "medium")
    inflation_value = inflation.get("value", 5.0)
    
    # High inflation adjustments
    if pressure == "high":
        thresholds["essential"] += 5.0  # Allow more for essentials
        thresholds["lifestyle"] = max(10.0, thresholds["lifestyle"] - 5.0)  # Reduce lifestyle
        thresholds["savings"] = max(10.0, thresholds["savings"] - 5.0)  # Reduce savings target
        
        # Extra adjustment for very high inflation (>8%)
        if inflation_value > 8:
            thresholds["essential"] += 3.0
            thresholds["lifestyle"] = max(8.0, thresholds["lifestyle"] - 3.0)
    
    # Medium inflation adjustments
    elif pressure == "medium":
        thresholds["essential"] += 2.0
        thresholds["lifestyle"] = max(15.0, thresholds["lifestyle"] - 2.0)
    
    # Low inflation - encourage savings
    else:
        thresholds["savings"] += 5.0
        thresholds["lifestyle"] = max(15.0, thresholds["lifestyle"] - 2.0)
    
    # Ensure no negative values
    for key in thresholds:
        thresholds[key] = max(0.0, thresholds[key])
    
    return thresholds


def get_inflation_impact_categories(
    expenses: List[Dict],
    inflation: Dict
) -> List[Dict]:
    """
    Identify categories most affected by inflation
    
    Args:
        expenses: List of expense dicts with 'category' and 'amount'
        inflation: Dict from get_inflation_pressure()
    
    Returns:
        List of categories with impact assessment
    """
    pressure = inflation.get("pressure", "medium")
    inflation_value = inflation.get("value", 5.0)
    
    # Aggregate expenses by category
    category_totals = {}
    for expense in expenses:
        category = expense.get("category", "Other").lower()
        amount = expense.get("amount", 0)
        category_totals[category] = category_totals.get(category, 0) + amount
    
    # Assess impact
    impacted_categories = []
    
    for category, amount in category_totals.items():
        sensitivity = SENSITIVITY.get(category, "low")
        
        # Calculate impact multiplier
        if sensitivity == "high":
            impact_multiplier = inflation_value * 1.5  # High sensitivity
            impact_level = "high"
        elif sensitivity == "medium":
            impact_multiplier = inflation_value * 1.0
            impact_level = "medium"
        else:
            impact_multiplier = inflation_value * 0.5
            impact_level = "low"
        
        # Only include if significant impact
        if impact_multiplier > 3.0 or sensitivity == "high":
            impacted_categories.append({
                "category": category.title(),
                "amount": amount,
                "sensitivity": sensitivity,
                "impact_level": impact_level,
                "estimated_increase_pct": round(impact_multiplier, 1)
            })
    
    # Sort by impact level and amount
    impact_order = {"high": 3, "medium": 2, "low": 1}
    impacted_categories.sort(
        key=lambda x: (impact_order[x["impact_level"]], x["amount"]),
        reverse=True
    )
    
    return impacted_categories


def generate_inflation_insights(
    inflation: Dict,
    expenses: List[Dict],
    thresholds: Dict[str, float],
    monthly_income: float,
    current_allocation: Dict[str, float]
) -> List[str]:
    """
    Generate specific, actionable inflation-aware insights
    
    Args:
        inflation: Dict from get_inflation_pressure()
        expenses: List of expense dicts
        thresholds: Adjusted thresholds from adjust_budget_thresholds()
        monthly_income: User's monthly income
        current_allocation: Current spending allocation by category
    
    Returns:
        List of specific insight strings
    """
    insights = []
    
    pressure = inflation.get("pressure", "medium")
    inflation_value = inflation.get("value", 5.0)
    
    # Get impacted categories
    impacted = get_inflation_impact_categories(expenses, inflation)
    
    # Insight 1: Overall inflation context
    if pressure == "high":
        insights.append(
            f"🔴 Inflation is at {inflation_value}%, creating HIGH pressure on essential expenses. "
            f"Immediate budget adjustments recommended."
        )
    elif pressure == "medium":
        insights.append(
            f"🟡 Inflation is at {inflation_value}%, creating MODERATE pressure on your budget. "
            f"Monitor essential spending closely."
        )
    else:
        insights.append(
            f"🟢 Inflation is at {inflation_value}%, which is LOW. "
            f"Good time to increase savings and investments."
        )
    
    # Insight 2: Category-specific impacts
    if impacted:
        top_impacted = impacted[0]
        category = top_impacted["category"]
        amount = top_impacted["amount"]
        increase_pct = top_impacted["estimated_increase_pct"]
        
        estimated_increase = (amount * increase_pct) / 100
        
        insights.append(
            f"📊 Your {category} spending (₹{amount:,.0f}/month) is most affected by inflation. "
            f"Expect ~₹{estimated_increase:,.0f} increase due to {increase_pct}% price rise."
        )
    
    # Insight 3: Essential spending vs threshold
    essential_pct = current_allocation.get("essential", 0)
    essential_threshold = thresholds.get("essential", 30)
    
    if essential_pct > essential_threshold:
        excess_pct = essential_pct - essential_threshold
        excess_amount = (excess_pct / 100) * monthly_income
        
        insights.append(
            f"⚠️ Essential spending is {essential_pct:.1f}% of income, "
            f"₹{excess_amount:,.0f} above inflation-adjusted safe level ({essential_threshold:.0f}%). "
            f"Review food and transport costs."
        )
    
    # Insight 4: Lifestyle adjustment recommendation
    lifestyle_pct = current_allocation.get("lifestyle", 0)
    lifestyle_threshold = thresholds.get("lifestyle", 20)
    
    if pressure in ["high", "medium"] and lifestyle_pct > lifestyle_threshold:
        reduction_needed = lifestyle_pct - lifestyle_threshold
        reduction_amount = (reduction_needed / 100) * monthly_income
        
        insights.append(
            f"💡 Reduce lifestyle spending by ₹{reduction_amount:,.0f}/month "
            f"({reduction_needed:.1f}% of income) to offset inflation impact on essentials."
        )
    
    # Insight 5: Savings adjustment
    savings_pct = current_allocation.get("savings", 0)
    savings_threshold = thresholds.get("savings", 20)
    
    if pressure == "high" and savings_pct < savings_threshold:
        insights.append(
            f"🏦 During high inflation, maintain at least {savings_threshold:.0f}% savings "
            f"to protect against price increases. Current: {savings_pct:.1f}%."
        )
    elif pressure == "low" and savings_pct < 25:
        target_increase = 25 - savings_pct
        target_amount = (target_increase / 100) * monthly_income
        
        insights.append(
            f"💰 Low inflation period - increase savings by ₹{target_amount:,.0f}/month "
            f"to reach 25% savings rate. Lock in today's prices."
        )
    
    # Insight 6: Specific category recommendations
    for category_data in impacted[:2]:  # Top 2 impacted
        category = category_data["category"]
        sensitivity = category_data["sensitivity"]
        
        if sensitivity == "high":
            if category.lower() == "food":
                insights.append(
                    f"🛒 Food prices rising with inflation. Consider bulk buying, "
                    f"local markets, and meal planning to reduce impact."
                )
            elif category.lower() == "transport":
                insights.append(
                    f"⛽ Fuel prices affected by inflation. Explore carpooling, "
                    f"public transport, or optimize travel routes."
                )
    
    return insights


def get_inflation_adjusted_analysis(
    db: Session,
    expenses: List[Dict],
    monthly_income: float,
    current_allocation: Dict[str, float]
) -> Dict:
    """
    Complete inflation-adjusted financial analysis
    
    Args:
        db: Database session
        expenses: List of expense dicts
        monthly_income: User's monthly income
        current_allocation: Current spending allocation
    
    Returns:
        Complete analysis with inflation adjustments
    """
    # Step 1: Get inflation pressure
    inflation = get_inflation_pressure(db)
    
    # Step 2: Adjust thresholds
    adjusted_thresholds = adjust_budget_thresholds(inflation)
    
    # Step 3: Get impacted categories
    impacted_categories = get_inflation_impact_categories(expenses, inflation)
    
    # Step 4: Generate insights
    insights = generate_inflation_insights(
        inflation,
        expenses,
        adjusted_thresholds,
        monthly_income,
        current_allocation
    )
    
    # Step 5: Calculate risk level with inflation consideration
    risk_score = 0
    
    # Inflation risk
    if inflation["pressure"] == "high":
        risk_score += 3
    elif inflation["pressure"] == "medium":
        risk_score += 1
    
    # Allocation risk
    essential_pct = current_allocation.get("essential", 0)
    if essential_pct > adjusted_thresholds["essential"]:
        risk_score += 2
    
    savings_pct = current_allocation.get("savings", 0)
    if savings_pct < adjusted_thresholds["savings"]:
        risk_score += 2
    
    # Determine overall risk
    if risk_score >= 5:
        risk_level = "high"
    elif risk_score >= 3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "inflation": inflation,
        "adjusted_thresholds": adjusted_thresholds,
        "impacted_categories": impacted_categories,
        "insights": insights,
        "recommendations": _generate_recommendations(
            inflation,
            adjusted_thresholds,
            current_allocation,
            monthly_income
        )
    }


def _generate_recommendations(
    inflation: Dict,
    thresholds: Dict[str, float],
    current_allocation: Dict[str, float],
    monthly_income: float
) -> List[str]:
    """Generate specific action recommendations"""
    recommendations = []
    
    pressure = inflation.get("pressure", "medium")
    
    # Essential spending recommendations
    essential_current = current_allocation.get("essential", 0)
    essential_target = thresholds["essential"]
    
    if essential_current > essential_target:
        reduction = essential_current - essential_target
        amount = (reduction / 100) * monthly_income
        recommendations.append(
            f"Reduce essential spending by ₹{amount:,.0f}/month to reach {essential_target:.0f}% target"
        )
    
    # Lifestyle recommendations
    lifestyle_current = current_allocation.get("lifestyle", 0)
    lifestyle_target = thresholds["lifestyle"]
    
    if lifestyle_current > lifestyle_target:
        reduction = lifestyle_current - lifestyle_target
        amount = (reduction / 100) * monthly_income
        recommendations.append(
            f"Cut lifestyle expenses by ₹{amount:,.0f}/month (dining out, entertainment, shopping)"
        )
    
    # Savings recommendations
    savings_current = current_allocation.get("savings", 0)
    savings_target = thresholds["savings"]
    
    if savings_current < savings_target:
        increase = savings_target - savings_current
        amount = (increase / 100) * monthly_income
        recommendations.append(
            f"Increase monthly savings by ₹{amount:,.0f} to reach {savings_target:.0f}% target"
        )
    
    # Inflation-specific recommendations
    if pressure == "high":
        recommendations.append(
            "Build 6-month emergency fund to protect against sustained high inflation"
        )
        recommendations.append(
            "Review and renegotiate recurring subscriptions and services"
        )
    elif pressure == "low":
        recommendations.append(
            "Invest surplus in inflation-protected instruments (PPF, inflation-indexed bonds)"
        )
    
    return recommendations


def get_category_inflation_multiplier(category: str, inflation_value: float) -> float:
    """
    Get inflation multiplier for a specific category
    
    Args:
        category: Expense category
        inflation_value: Current inflation rate
    
    Returns:
        Multiplier to apply to category budget
    """
    category_lower = category.lower()
    sensitivity = SENSITIVITY.get(category_lower, "low")
    
    if sensitivity == "high":
        return 1.0 + (inflation_value / 100 * 1.5)
    elif sensitivity == "medium":
        return 1.0 + (inflation_value / 100 * 1.0)
    else:
        return 1.0 + (inflation_value / 100 * 0.5)
