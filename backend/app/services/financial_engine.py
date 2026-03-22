"""
Unified Financial Decision Engine
A rule-based system that analyzes user finances and produces actionable decisions
"""
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from dataclasses import dataclass
import logging

from app.services.cpi_service import get_latest_cpi, get_all_cpi_with_inflation

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class UserProfile:
    """User financial profile"""
    monthly_income: float
    emi_amount: float = 0.0
    medical_risk: str = "low"  # low, medium, high
    family_dependency: int = 0
    has_emergency_fund: bool = False


@dataclass
class FinancialDecision:
    """Complete financial decision output"""
    risk_level: str  # low, medium, high, critical
    risk_score: int  # 0-100
    
    # Inflation context
    inflation: Dict  # {pressure, value, status}
    
    # Spending breakdown
    percentages: Dict  # {fixed, essential, lifestyle, savings}
    amounts: Dict  # Actual ₹ amounts
    
    # Issues detected
    money_leaks: List[Dict]  # Categories overspending due to inflation
    violations: List[str]  # Rule violations
    
    # Actionable output
    recommendations: List[str]  # Specific actions with ₹ amounts
    priority_actions: List[str]  # Top 3 urgent actions
    
    # Adjusted targets
    adjusted_thresholds: Dict  # Inflation-adjusted budget targets


# ============================================================================
# CORE ENGINE
# ============================================================================

class FinancialDecisionEngine:
    """
    Central decision engine that processes user finances and produces
    actionable recommendations based on rules and inflation data
    """
    
    # Category sensitivity to inflation
    INFLATION_SENSITIVITY = {
        "food": 1.5,      # High sensitivity
        "transport": 1.5,
        "healthcare": 1.5,
        "rent": 1.0,      # Medium sensitivity
        "utilities": 1.0,
        "bills": 1.0,
        "entertainment": 0.5,  # Low sensitivity
        "lifestyle": 0.5,
        "shopping": 0.5
    }
    
    # Base thresholds (% of income)
    BASE_THRESHOLDS = {
        "fixed": 50,      # Max fixed obligations
        "essential": 30,  # Max essential spending
        "lifestyle": 20,  # Max lifestyle spending
        "savings": 20     # Min savings target
    }
    
    @staticmethod
    def analyze(
        profile: UserProfile,
        expenses: List[Dict],
        db: Session
    ) -> FinancialDecision:
        """
        Main entry point: Analyze user finances and produce decisions
        
        Args:
            profile: User financial profile
            expenses: List of expense dicts with 'category', 'amount', 'note'
            db: Database session for CPI data
            
        Returns:
            FinancialDecision with complete analysis and recommendations
        """
        # Step 1: Get inflation context
        inflation = FinancialDecisionEngine._get_inflation_context(db)
        
        # Step 2: Categorize and calculate spending
        spending = FinancialDecisionEngine._categorize_expenses(expenses)
        percentages = FinancialDecisionEngine._calculate_percentages(
            spending, profile.monthly_income
        )
        
        # Step 3: Adjust thresholds based on inflation and profile
        adjusted_thresholds = FinancialDecisionEngine._adjust_thresholds(
            inflation, profile
        )
        
        # Step 4: Detect violations and money leaks
        violations = FinancialDecisionEngine._detect_violations(
            percentages, adjusted_thresholds
        )
        money_leaks = FinancialDecisionEngine._detect_money_leaks(
            spending, inflation
        )
        
        # Step 5: Calculate risk
        risk_score, risk_level = FinancialDecisionEngine._calculate_risk(
            percentages, violations, inflation, profile
        )
        
        # Step 6: Generate recommendations
        recommendations = FinancialDecisionEngine._generate_recommendations(
            spending, percentages, adjusted_thresholds, 
            inflation, profile, violations, money_leaks
        )
        
        # Step 7: Prioritize actions
        priority_actions = FinancialDecisionEngine._prioritize_actions(
            recommendations, risk_level, violations
        )
        
        # Step 8: Calculate actual amounts
        amounts = {
            category: round((pct / 100) * profile.monthly_income, 2)
            for category, pct in percentages.items()
        }
        
        return FinancialDecision(
            risk_level=risk_level,
            risk_score=risk_score,
            inflation=inflation,
            percentages=percentages,
            amounts=amounts,
            money_leaks=money_leaks,
            violations=violations,
            recommendations=recommendations,
            priority_actions=priority_actions,
            adjusted_thresholds=adjusted_thresholds
        )
    
    # ========================================================================
    # STEP 1: INFLATION CONTEXT
    # ========================================================================
    
    @staticmethod
    def _get_inflation_context(db: Session) -> Dict:
        """Extract inflation pressure from CPI data"""
        try:
            cpi_data = get_all_cpi_with_inflation(db, limit=2)
            if not cpi_data or len(cpi_data) == 0:
                return {
                    "pressure": "medium",
                    "value": 5.0,
                    "status": "estimated"
                }
            
            latest = cpi_data[-1]
            yoy_inflation = latest.get("year_over_year_inflation", 5.0) or 5.0
            
            # Determine pressure level
            if yoy_inflation < 3:
                pressure = "low"
            elif yoy_inflation < 6:
                pressure = "medium"
            else:
                pressure = "high"
            
            return {
                "pressure": pressure,
                "value": round(yoy_inflation, 2),
                "status": "actual"
            }
        except Exception as e:
            logger.warning(f"Could not fetch CPI data: {e}")
            return {
                "pressure": "medium",
                "value": 5.0,
                "status": "estimated"
            }
    
    # ========================================================================
    # STEP 2: EXPENSE CATEGORIZATION
    # ========================================================================
    
    @staticmethod
    def _categorize_expenses(expenses: List[Dict]) -> Dict[str, Dict[str, float]]:
        """
        Categorize expenses into: fixed, essential, lifestyle, savings
        
        Returns:
            {
                "fixed": {"Rent": 15000, "EMI": 10000},
                "essential": {"Food": 8000, "Transport": 3000},
                "lifestyle": {"Entertainment": 2000},
                "savings": {"Investment": 5000}
            }
        """
        categorized = {
            "fixed": {},
            "essential": {},
            "lifestyle": {},
            "savings": {}
        }
        
        # Category mapping
        CATEGORY_MAP = {
            # Fixed obligations
            "rent": "fixed",
            "emi": "fixed",
            "loan": "fixed",
            "insurance": "fixed",
            
            # Essential
            "food": "essential",
            "groceries": "essential",
            "transport": "essential",
            "healthcare": "essential",
            "utilities": "essential",
            "bills": "essential",
            
            # Lifestyle
            "entertainment": "lifestyle",
            "dining": "lifestyle",
            "shopping": "lifestyle",
            "lifestyle": "lifestyle",
            "travel": "lifestyle",
            
            # Savings
            "savings": "savings",
            "investment": "savings"
        }
        
        for expense in expenses:
            category = expense.get("category", "Other").lower()
            amount = expense.get("amount", 0)
            
            # Determine bucket
            bucket = CATEGORY_MAP.get(category, "lifestyle")
            
            # Aggregate
            if category not in categorized[bucket]:
                categorized[bucket][category] = 0
            categorized[bucket][category] += amount
        
        return categorized
    
    @staticmethod
    def _calculate_percentages(
        spending: Dict[str, Dict[str, float]], 
        income: float
    ) -> Dict[str, float]:
        """Calculate spending as % of income"""
        totals = {
            "fixed": sum(spending["fixed"].values()),
            "essential": sum(spending["essential"].values()),
            "lifestyle": sum(spending["lifestyle"].values()),
            "savings": sum(spending["savings"].values())
        }
        
        total_spent = totals["fixed"] + totals["essential"] + totals["lifestyle"]
        
        # Calculate percentages
        percentages = {
            "fixed": round((totals["fixed"] / income) * 100, 1) if income > 0 else 0,
            "essential": round((totals["essential"] / income) * 100, 1) if income > 0 else 0,
            "lifestyle": round((totals["lifestyle"] / income) * 100, 1) if income > 0 else 0,
            "savings": round((totals["savings"] / income) * 100, 1) if income > 0 else 0
        }
        
        # Calculate actual savings (income - spending)
        actual_savings = income - total_spent
        percentages["actual_savings"] = round((actual_savings / income) * 100, 1) if income > 0 else 0
        
        return percentages
    
    # ========================================================================
    # STEP 3: THRESHOLD ADJUSTMENT
    # ========================================================================
    
    @staticmethod
    def _adjust_thresholds(inflation: Dict, profile: UserProfile) -> Dict:
        """
        Adjust budget thresholds based on inflation and user profile
        
        Logic:
        - High inflation → increase essential budget, reduce lifestyle
        - High EMI → reduce lifestyle, increase savings target
        - High medical risk → increase savings target
        - Family dependency → increase essential budget
        """
        thresholds = FinancialDecisionEngine.BASE_THRESHOLDS.copy()
        
        # Inflation adjustments
        if inflation["pressure"] == "high":
            thresholds["essential"] += 5
            thresholds["lifestyle"] -= 5
            thresholds["savings"] -= 5
        elif inflation["pressure"] == "medium":
            thresholds["essential"] += 2
            thresholds["lifestyle"] -= 2
        
        # EMI adjustments
        if profile.emi_amount > 0:
            emi_pct = (profile.emi_amount / profile.monthly_income) * 100
            if emi_pct > 30:
                thresholds["lifestyle"] -= 5
                thresholds["savings"] = max(15, thresholds["savings"])
        
        # Medical risk adjustments
        if profile.medical_risk == "high":
            thresholds["savings"] = max(25, thresholds["savings"])
            thresholds["lifestyle"] -= 3
        elif profile.medical_risk == "medium":
            thresholds["savings"] = max(22, thresholds["savings"])
        
        # Family dependency adjustments
        if profile.family_dependency > 0:
            thresholds["essential"] += profile.family_dependency * 2
            thresholds["lifestyle"] -= profile.family_dependency * 1
        
        # Ensure thresholds are reasonable
        thresholds["essential"] = min(40, max(25, thresholds["essential"]))
        thresholds["lifestyle"] = min(25, max(10, thresholds["lifestyle"]))
        thresholds["savings"] = min(30, max(15, thresholds["savings"]))
        
        return thresholds
    
    # ========================================================================
    # STEP 4: VIOLATION DETECTION
    # ========================================================================
    
    @staticmethod
    def _detect_violations(
        percentages: Dict[str, float], 
        thresholds: Dict
    ) -> List[str]:
        """Detect budget rule violations"""
        violations = []
        
        if percentages["fixed"] > thresholds["fixed"]:
            excess = percentages["fixed"] - thresholds["fixed"]
            violations.append(
                f"Fixed obligations are {percentages['fixed']:.1f}% of income "
                f"({excess:.1f}% over safe limit)"
            )
        
        if percentages["essential"] > thresholds["essential"]:
            excess = percentages["essential"] - thresholds["essential"]
            violations.append(
                f"Essential spending is {percentages['essential']:.1f}% of income "
                f"({excess:.1f}% over recommended)"
            )
        
        if percentages["lifestyle"] > thresholds["lifestyle"]:
            excess = percentages["lifestyle"] - thresholds["lifestyle"]
            violations.append(
                f"Lifestyle spending is {percentages['lifestyle']:.1f}% of income "
                f"({excess:.1f}% over budget)"
            )
        
        if percentages["actual_savings"] < thresholds["savings"]:
            deficit = thresholds["savings"] - percentages["actual_savings"]
            violations.append(
                f"Savings rate is only {percentages['actual_savings']:.1f}% "
                f"({deficit:.1f}% below target)"
            )
        
        return violations
    
    @staticmethod
    def _detect_money_leaks(
        spending: Dict[str, Dict[str, float]], 
        inflation: Dict
    ) -> List[Dict]:
        """
        Detect categories where inflation is causing overspending
        """
        leaks = []
        inflation_value = inflation["value"]
        
        # Check essential categories
        for category, amount in spending["essential"].items():
            sensitivity = FinancialDecisionEngine.INFLATION_SENSITIVITY.get(
                category.lower(), 1.0
            )
            impact = inflation_value * sensitivity
            
            if impact > 5.0:  # Significant impact
                leaks.append({
                    "category": category.title(),
                    "amount": amount,
                    "inflation_impact": round(impact, 1),
                    "estimated_increase": round(amount * (impact / 100), 2)
                })
        
        # Sort by impact
        leaks.sort(key=lambda x: x["inflation_impact"], reverse=True)
        
        return leaks
    
    # ========================================================================
    # STEP 5: RISK CALCULATION
    # ========================================================================
    
    @staticmethod
    def _calculate_risk(
        percentages: Dict[str, float],
        violations: List[str],
        inflation: Dict,
        profile: UserProfile
    ) -> Tuple[int, str]:
        """
        Calculate financial risk score and level
        
        Returns:
            (risk_score: 0-100, risk_level: str)
        """
        risk_score = 0
        
        # Violation penalties
        risk_score += len(violations) * 10
        
        # Savings risk
        if percentages["actual_savings"] < 10:
            risk_score += 20
        elif percentages["actual_savings"] < 15:
            risk_score += 10
        
        # Fixed obligations risk
        if percentages["fixed"] > 50:
            risk_score += 15
        elif percentages["fixed"] > 45:
            risk_score += 8
        
        # Inflation risk
        if inflation["pressure"] == "high":
            risk_score += 15
        elif inflation["pressure"] == "medium":
            risk_score += 8
        
        # Emergency fund risk
        if not profile.has_emergency_fund:
            risk_score += 10
        
        # Medical risk
        if profile.medical_risk == "high":
            risk_score += 10
        elif profile.medical_risk == "medium":
            risk_score += 5
        
        # Cap at 100
        risk_score = min(100, risk_score)
        
        # Determine level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_score, risk_level
    
    # ========================================================================
    # STEP 6: RECOMMENDATION GENERATION
    # ========================================================================
    
    @staticmethod
    def _generate_recommendations(
        spending: Dict[str, Dict[str, float]],
        percentages: Dict[str, float],
        thresholds: Dict,
        inflation: Dict,
        profile: UserProfile,
        violations: List[str],
        money_leaks: List[Dict]
    ) -> List[str]:
        """
        Generate specific, actionable recommendations with ₹ amounts
        """
        recommendations = []
        income = profile.monthly_income
        
        # Savings recommendations
        current_savings = (percentages["actual_savings"] / 100) * income
        target_savings = (thresholds["savings"] / 100) * income
        if current_savings < target_savings:
            deficit = target_savings - current_savings
            recommendations.append(
                f"Increase monthly savings by ₹{deficit:,.0f} to reach {thresholds['savings']}% target "
                f"(currently at {percentages['actual_savings']:.1f}%)"
            )
        
        # Lifestyle reduction
        if percentages["lifestyle"] > thresholds["lifestyle"]:
            excess_pct = percentages["lifestyle"] - thresholds["lifestyle"]
            excess_amount = (excess_pct / 100) * income
            recommendations.append(
                f"Reduce lifestyle spending by ₹{excess_amount:,.0f} per month "
                f"(cut from {percentages['lifestyle']:.1f}% to {thresholds['lifestyle']}%)"
            )
        
        # Money leak recommendations
        for leak in money_leaks[:2]:  # Top 2 leaks
            recommendations.append(
                f"Monitor {leak['category']} spending (₹{leak['amount']:,.0f}/month) - "
                f"inflation impact of {leak['inflation_impact']}% adds ~₹{leak['estimated_increase']:,.0f}"
            )
        
        # Emergency fund
        if not profile.has_emergency_fund:
            target_fund = income * 6
            recommendations.append(
                f"Build emergency fund: Target ₹{target_fund:,.0f} (6 months of expenses)"
            )
        
        # Inflation-specific advice
        if inflation["pressure"] == "high":
            recommendations.append(
                f"Inflation is at {inflation['value']}% - prioritize essential spending, "
                f"delay non-urgent lifestyle purchases"
            )
        
        # EMI optimization
        if profile.emi_amount > 0:
            emi_pct = (profile.emi_amount / income) * 100
            if emi_pct > 30:
                recommendations.append(
                    f"EMI burden is {emi_pct:.1f}% of income (₹{profile.emi_amount:,.0f}) - "
                    f"consider refinancing or prepayment to reduce interest"
                )
        
        # Category-specific cuts
        lifestyle_total = sum(spending["lifestyle"].values())
        if lifestyle_total > 0:
            for category, amount in sorted(
                spending["lifestyle"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:2]:
                if amount > income * 0.05:  # More than 5% of income
                    cut_amount = amount * 0.2  # Suggest 20% cut
                    recommendations.append(
                        f"Reduce {category.title()} spending by ₹{cut_amount:,.0f} "
                        f"(20% cut from current ₹{amount:,.0f})"
                    )
        
        return recommendations
    
    # ========================================================================
    # STEP 7: ACTION PRIORITIZATION
    # ========================================================================
    
    @staticmethod
    def _prioritize_actions(
        recommendations: List[str],
        risk_level: str,
        violations: List[str]
    ) -> List[str]:
        """Extract top 3 priority actions"""
        priority = []
        
        # Critical actions first
        if risk_level in ["critical", "high"]:
            # Savings is always priority 1 if violated
            savings_recs = [r for r in recommendations if "savings" in r.lower()]
            if savings_recs:
                priority.append(savings_recs[0])
            
            # Lifestyle cuts are priority 2
            lifestyle_recs = [r for r in recommendations if "lifestyle" in r.lower() or "reduce" in r.lower()]
            if lifestyle_recs and len(priority) < 3:
                priority.append(lifestyle_recs[0])
        
        # Add remaining recommendations
        for rec in recommendations:
            if rec not in priority and len(priority) < 3:
                priority.append(rec)
        
        return priority[:3]


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def analyze_finances(
    monthly_income: float,
    expenses: List[Dict],
    db: Session,
    emi_amount: float = 0,
    medical_risk: str = "low",
    family_dependency: int = 0,
    has_emergency_fund: bool = False
) -> FinancialDecision:
    """
    Convenience function to analyze user finances
    
    Args:
        monthly_income: User's monthly income
        expenses: List of expense dicts
        db: Database session
        emi_amount: Monthly EMI payment
        medical_risk: low/medium/high
        family_dependency: Number of dependents
        has_emergency_fund: Whether user has emergency fund
        
    Returns:
        FinancialDecision with complete analysis
    """
    profile = UserProfile(
        monthly_income=monthly_income,
        emi_amount=emi_amount,
        medical_risk=medical_risk,
        family_dependency=family_dependency,
        has_emergency_fund=has_emergency_fund
    )
    
    return FinancialDecisionEngine.analyze(profile, expenses, db)
