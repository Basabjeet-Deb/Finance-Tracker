"""
Inflation Intelligence Module
Focused responsibilities: inflation pressure, threshold adjustment, and inflation-specific insights

DOES:
- Adjust budget thresholds based on inflation
- Generate inflation-specific insights (max 4)
- Provide category inflation multipliers
- Calculate transport inflation factor (integrated from fuel service)
- Detect transport pressure

DOES NOT:
- Calculate risk scores (use centralized scoring)
- Generate general recommendations (use optimizer)
- Perform full financial analysis (use financial_engine)
- Scrape external websites during requests
"""
from typing import Dict, List
from sqlalchemy.orm import Session
import logging

from app.services.cpi_service import get_inflation_pressure as get_cpi_inflation_pressure

logger = logging.getLogger(__name__)


# Category sensitivity to inflation - ALIGNED with rule_engine categories
SENSITIVITY = {
    # Fixed (medium sensitivity)
    "rent": "medium",
    "emi": "medium",
    "insurance": "medium",
    "utilities": "medium",
    
    # Essential (high sensitivity)
    "food": "high",
    "groceries": "high",
    "transport": "high",
    "healthcare": "high",
    "education": "medium",
    
    # Lifestyle (low sensitivity)
    "eating out": "low",
    "dining": "low",
    "shopping": "low",
    "subscriptions": "low",
    "entertainment": "low",
    "lifestyle": "low",
    
    # Unexpected (medium sensitivity)
    "emergency": "medium",
    "medical emergency": "high"
}


def adjust_budget_thresholds(inflation: Dict) -> Dict[str, float]:
    """
    Dynamically adjust budget thresholds based on inflation pressure
    
    This is the PRIMARY function for inflation-aware budget adjustment
    
    Args:
        inflation: Dict from cpi_service.get_inflation_pressure()
            {
                "pressure": "low | medium | high",
                "value": float,
                "confidence": "high | medium | low"
            }
    
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
        
        logger.info(f"High inflation ({inflation_value}%) - adjusted thresholds")
    
    # Medium inflation adjustments
    elif pressure == "medium":
        thresholds["essential"] += 2.0
        thresholds["lifestyle"] = max(15.0, thresholds["lifestyle"] - 2.0)
        logger.info(f"Medium inflation ({inflation_value}%) - slight adjustments")
    
    # Low inflation - encourage savings
    else:
        thresholds["savings"] += 5.0
        thresholds["lifestyle"] = max(15.0, thresholds["lifestyle"] - 2.0)
        logger.info(f"Low inflation ({inflation_value}%) - encouraging savings")
    
    # Ensure no negative values
    for key in thresholds:
        thresholds[key] = max(0.0, thresholds[key])
    
    return thresholds


def get_transport_inflation_factor(inflation: Dict) -> float:
    """
    Calculate transport-specific inflation factor
    
    Transport costs (fuel) typically inflate 1.2-1.5x faster than general CPI
    This replaces unreliable fuel price scraping with CPI-derived estimates
    
    Args:
        inflation: Dict from cpi_service.get_inflation_pressure()
    
    Returns:
        Transport inflation factor (e.g., 1.075 for 7.5% transport inflation)
    """
    cpi_value = inflation.get("value", 5.0)
    
    # Transport inflates 1.2-1.5x faster than general CPI
    # Use 1.3x as middle ground
    transport_inflation = cpi_value * 1.3
    
    # Cap at realistic values (max 20% annual inflation)
    transport_inflation = min(transport_inflation, 20.0)
    
    # Convert to factor
    factor = 1.0 + (transport_inflation / 100)
    
    return round(factor, 3)


def calculate_transport_pressure(
    transport_spend: float,
    income: float,
    inflation: Dict
) -> Dict:
    """
    Calculate transport spending pressure
    
    Combines spending percentage with inflation impact
    
    Args:
        transport_spend: Monthly transport spending
        income: Monthly income
        inflation: Dict from cpi_service.get_inflation_pressure()
    
    Returns:
        {
            "pressure": "low | medium | high",
            "factor": float (inflation factor),
            "impact": "low | medium | high",
            "percentage": float (% of income),
            "estimated_increase": float (₹ amount)
        }
    """
    if income <= 0:
        return {
            "pressure": "low",
            "factor": 1.0,
            "impact": "low",
            "percentage": 0.0,
            "estimated_increase": 0.0
        }
    
    # Calculate percentage of income
    transport_pct = (transport_spend / income) * 100
    
    # Get transport inflation factor
    transport_factor = get_transport_inflation_factor(inflation)
    transport_inflation_pct = (transport_factor - 1.0) * 100
    
    # Estimate increase in transport costs
    estimated_increase = transport_spend * (transport_inflation_pct / 100)
    
    # Determine pressure level
    if transport_pct > 10:
        pressure = "high"
    elif transport_pct > 5:
        pressure = "medium"
    else:
        pressure = "low"
    
    # Determine impact level (combines spending % and inflation)
    if transport_pct > 10 and inflation.get("pressure") == "high":
        impact = "high"
    elif transport_pct > 5 and inflation.get("pressure") in ["medium", "high"]:
        impact = "medium"
    else:
        impact = "low"
    
    return {
        "pressure": pressure,
        "factor": transport_factor,
        "impact": impact,
        "percentage": round(transport_pct, 1),
        "estimated_increase": round(estimated_increase, 2)
    }


def generate_inflation_insights(
    inflation: Dict,
    expenses: List[Dict],
    monthly_income: float
) -> List[str]:
    """
    Generate inflation-specific insights ONLY
    
    CRITICAL: Returns maximum 4 insights
    Does NOT generate general recommendations
    
    Args:
        inflation: Dict from cpi_service.get_inflation_pressure()
        expenses: List of expense dicts
        monthly_income: User's monthly income
    
    Returns:
        List of max 4 inflation-specific insight strings
    """
    insights = []
    
    pressure = inflation.get("pressure", "medium")
    inflation_value = inflation.get("value", 5.0)
    
    # Insight 1: Overall inflation context
    if pressure == "high":
        insights.append(
            f"Inflation is at {inflation_value}%, creating HIGH pressure on essential expenses. "
            f"Immediate budget adjustments recommended."
        )
    elif pressure == "medium":
        insights.append(
            f"Inflation is at {inflation_value}%, creating MODERATE pressure on your budget. "
            f"Monitor essential spending closely."
        )
    else:
        insights.append(
            f"Inflation is at {inflation_value}%, which is LOW. "
            f"Good time to increase savings and investments."
        )
    
    # Insight 2: Category-specific impacts
    impacted = _get_inflation_impact_categories(expenses, inflation)
    
    if impacted:
        top_impacted = impacted[0]
        category = top_impacted["category"]
        amount = top_impacted["amount"]
        increase_pct = top_impacted["estimated_increase_pct"]
        
        estimated_increase = (amount * increase_pct) / 100
        
        insights.append(
            f"Your {category} spending (₹{amount:,.0f}/month) is most affected by inflation. "
            f"Expect ~₹{estimated_increase:,.0f} increase due to {increase_pct}% price rise."
        )
    
    # Insight 3: Transport-specific insight (integrated from fuel service)
    transport_spend = sum(
        exp.get("amount", 0) 
        for exp in expenses 
        if exp.get("category", "").lower() in ["transport", "fuel"]
    )
    
    if transport_spend > 0:
        transport_pressure = calculate_transport_pressure(
            transport_spend, monthly_income, inflation
        )
        
        if transport_pressure["impact"] in ["medium", "high"]:
            insights.append(
                f"Transport costs (₹{transport_spend:,.0f}/month, {transport_pressure['percentage']:.1f}% of income) "
                f"are rising {(transport_pressure['factor'] - 1.0) * 100:.1f}% due to fuel inflation. "
                f"Consider carpooling or public transit."
            )
    
    # Insight 4: Inflation-period specific advice
    if pressure == "high":
        insights.append(
            "During high inflation, prioritize essential spending and "
            "delay non-urgent lifestyle purchases."
        )
    elif pressure == "low":
        insights.append(
            "Low inflation period - good time to lock in prices for "
            "long-term contracts and increase investments."
        )
    
    # CRITICAL: Return only top 4 insights
    return insights[:4]


def get_category_inflation_multiplier(category: str, inflation_value: float) -> float:
    """
    Get inflation multiplier for a specific category
    
    Used to adjust category budgets based on inflation
    
    Args:
        category: Expense category
        inflation_value: Current inflation rate (%)
    
    Returns:
        Multiplier to apply to category budget (e.g., 1.075 for 7.5% increase)
    """
    category_lower = category.lower()
    sensitivity = SENSITIVITY.get(category_lower, "low")
    
    if sensitivity == "high":
        return 1.0 + (inflation_value / 100 * 1.5)
    elif sensitivity == "medium":
        return 1.0 + (inflation_value / 100 * 1.0)
    else:
        return 1.0 + (inflation_value / 100 * 0.5)


def calculate_emi_pressure(
    emi_amount: float,
    income: float
) -> Dict:
    """
    Calculate EMI burden pressure
    
    Integrated from RBI service - provides EMI analysis without web scraping
    
    Args:
        emi_amount: Monthly EMI payment
        income: Monthly income
    
    Returns:
        {
            "repo_rate": float (static baseline),
            "emi_pressure": "low | medium | high",
            "percentage": float (% of income),
            "impact": str (description),
            "projected_increase": float (potential increase if rates rise)
        }
    """
    if income <= 0 or emi_amount <= 0:
        return {
            "repo_rate": 6.50,
            "emi_pressure": "low",
            "percentage": 0.0,
            "impact": "No EMI detected",
            "projected_increase": 0.0
        }
    
    # Calculate EMI as percentage of income
    emi_pct = (emi_amount / income) * 100
    
    # Determine pressure level
    if emi_pct > 40:
        pressure = "high"
        impact = "EMI burden is very high - consider refinancing or prepayment"
    elif emi_pct > 30:
        pressure = "medium"
        impact = "EMI burden is moderate - monitor interest rate changes"
    else:
        pressure = "low"
        impact = "EMI burden is manageable"
    
    # Static repo rate baseline (no scraping)
    repo_rate = 6.50
    
    # Projected increase if repo rate rises by 0.25%
    # Typically translates to 2-3% EMI increase for floating rate loans
    projected_increase = emi_amount * 0.025
    
    return {
        "repo_rate": repo_rate,
        "emi_pressure": pressure,
        "percentage": round(emi_pct, 1),
        "impact": impact,
        "projected_increase": round(projected_increase, 2)
    }


# ============================================================================
# INTERNAL HELPER FUNCTIONS
# ============================================================================

def _get_inflation_impact_categories(
    expenses: List[Dict],
    inflation: Dict
) -> List[Dict]:
    """
    Identify categories most affected by inflation (internal use only)
    
    Args:
        expenses: List of expense dicts with 'category' and 'amount'
        inflation: Dict from cpi_service.get_inflation_pressure()
    
    Returns:
        List of categories with impact assessment, sorted by impact
    """
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
