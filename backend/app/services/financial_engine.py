"""
Unified Financial Decision Engine
A rule-based system that analyzes user finances and produces actionable decisions
"""
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from dataclasses import dataclass
import logging

from app.services.cpi_service import get_inflation_pressure
from app.services.inflation_engine import calculate_emi_pressure
from app.services.deals_service import CostOptimizationService
from app.utils.scoring import calculate_financial_score

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
    money_leaks: List[Dict]  # Categories overspending (inflation + behavior)
    violations: List[Dict]  # Structured rule violations
    
    # Actionable output
    recommendations: List[str]  # Specific actions with ₹ amounts (max 5)
    priority_actions: List[str]  # Top 3 urgent actions
    
    # Cost optimization opportunities
    optimization_opportunities: List[Dict]  # Targeted cost-saving opportunities (max 2)
    
    # Adjusted targets
    adjusted_thresholds: Dict  # Inflation-adjusted budget targets
    
    # Survival metric
    survival_months: float  # How many months can survive on savings


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
        
        # Step 1b: Get EMI pressure context
        emi_pressure = calculate_emi_pressure(profile.emi_amount, profile.monthly_income)
        
        # Step 2: Categorize and calculate spending
        spending = FinancialDecisionEngine._categorize_expenses(expenses)
        percentages = FinancialDecisionEngine._calculate_percentages(
            spending, profile.monthly_income
        )
        
        # Step 3: Adjust thresholds based on inflation, EMI pressure, and profile
        adjusted_thresholds = FinancialDecisionEngine._adjust_thresholds(
            inflation, profile, emi_pressure
        )
        
        # Step 4: Detect violations and money leaks
        violations = FinancialDecisionEngine._detect_violations(
            percentages, adjusted_thresholds
        )
        money_leaks = FinancialDecisionEngine._detect_money_leaks(
            spending, inflation, profile.monthly_income
        )
        
        # Step 5: Calculate risk (FIXED: now passes money_leaks)
        risk_score, risk_level = FinancialDecisionEngine._calculate_risk(
            percentages, violations, inflation, profile, money_leaks
        )
        
        # Step 6: Generate recommendations
        recommendations = FinancialDecisionEngine._generate_recommendations(
            spending, percentages, adjusted_thresholds, 
            inflation, profile, violations, money_leaks, emi_pressure
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
        
        # Step 9: Calculate survival months
        # Use actual savings from current month (income - spending)
        total_spending = sum(
            sum(spending[category].values()) 
            for category in ["fixed", "essential", "lifestyle"]
        )
        current_month_savings = max(0, profile.monthly_income - total_spending)
        
        # Estimate total savings balance (assume 6 months of accumulated savings)
        # In production, this should come from user profile
        estimated_savings_balance = current_month_savings * 6
        
        survival_months = FinancialDecisionEngine._calculate_survival_months(
            estimated_savings_balance, total_spending
        )
        
        # Step 10: Generate cost optimization opportunities
        # Convert spending dict to flat category -> amount mapping
        spending_flat = {}
        for bucket, categories in spending.items():
            for category, amount in categories.items():
                spending_flat[category] = amount
        
        optimization_opportunities = CostOptimizationService.get_optimization_opportunities(
            spending_by_category=spending_flat,
            income=profile.monthly_income,
            risk_level=risk_level,
            money_leaks=money_leaks,
            violations=violations
        )
        
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
            optimization_opportunities=optimization_opportunities,
            adjusted_thresholds=adjusted_thresholds,
            survival_months=survival_months
        )
    
    # ========================================================================
    # STEP 1: INFLATION CONTEXT
    # ========================================================================
    
    @staticmethod
    def _get_inflation_context(db: Session) -> Dict:
        """
        Extract inflation pressure from CPI intelligence service
        
        Uses the new get_inflation_pressure() function which returns
        decision-ready inflation signals instead of raw CPI data
        """
        try:
            # Get inflation intelligence (not raw CPI data)
            inflation_intel = get_inflation_pressure(db)
            
            return {
                "pressure": inflation_intel["pressure"],
                "value": inflation_intel["value"],
                "status": "actual" if inflation_intel["confidence"] in ["high", "medium"] else "estimated"
            }
        
        except Exception as e:
            logger.warning(f"Could not fetch inflation intelligence: {e}")
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
        Categorize expenses into: fixed, essential, lifestyle ONLY
        
        CRITICAL: Savings is NOT an expense category - it's computed as leftover money
        
        Returns:
            {
                "fixed": {"Rent": 15000, "EMI": 10000},
                "essential": {"Food": 8000, "Transport": 3000},
                "lifestyle": {"Entertainment": 2000}
            }
        """
        categorized = {
            "fixed": {},
            "essential": {},
            "lifestyle": {}
        }
        
        # Category mapping - REMOVED savings category
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
            
            # Lifestyle (default for unknown categories)
            "entertainment": "lifestyle",
            "dining": "lifestyle",
            "shopping": "lifestyle",
            "lifestyle": "lifestyle",
            "travel": "lifestyle",
            "other": "lifestyle"
        }
        
        for expense in expenses:
            category = expense.get("category", "Other").lower()
            amount = expense.get("amount", 0)
            
            # Skip savings/investment categories - they are NOT expenses
            if category in ["savings", "investment", "saving"]:
                logger.warning(f"Skipping '{category}' - savings is not an expense category")
                continue
            
            # Determine bucket (default to lifestyle for unknown)
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
        """
        Calculate spending as % of income
        
        CRITICAL FIX: Savings is computed as leftover money, NOT from expenses
        """
        totals = {
            "fixed": sum(spending["fixed"].values()),
            "essential": sum(spending["essential"].values()),
            "lifestyle": sum(spending["lifestyle"].values())
        }
        
        # Total spent = fixed + essential + lifestyle
        total_spent = totals["fixed"] + totals["essential"] + totals["lifestyle"]
        
        # Actual savings = income - total_spent (leftover money)
        actual_savings = income - total_spent
        
        # Calculate percentages
        percentages = {
            "fixed": round((totals["fixed"] / income) * 100, 1) if income > 0 else 0,
            "essential": round((totals["essential"] / income) * 100, 1) if income > 0 else 0,
            "lifestyle": round((totals["lifestyle"] / income) * 100, 1) if income > 0 else 0,
            "savings": round((actual_savings / income) * 100, 1) if income > 0 else 0
        }
        
        return percentages
    
    # ========================================================================
    # STEP 3: THRESHOLD ADJUSTMENT
    # ========================================================================
    
    @staticmethod
    def _adjust_thresholds(
        inflation: Dict, 
        profile: UserProfile,
        emi_pressure: Dict
    ) -> Dict:
        """
        Adjust budget thresholds based on inflation, EMI pressure, and user profile
        
        Logic:
        - High inflation → increase essential budget, reduce lifestyle
        - High EMI pressure → reduce lifestyle, increase savings target
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
        
        # EMI pressure adjustments (INTEGRATED from inflation_engine)
        if emi_pressure["emi_pressure"] == "high":
            thresholds["lifestyle"] -= 5
            thresholds["savings"] = max(15, thresholds["savings"])
            logger.info(f"High EMI pressure ({emi_pressure['percentage']}%) - reduced lifestyle allowance")
        elif emi_pressure["emi_pressure"] == "medium":
            thresholds["lifestyle"] -= 3
            logger.info(f"Medium EMI pressure ({emi_pressure['percentage']}%) - slight lifestyle reduction")
        
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
    ) -> List[Dict]:
        """
        Detect budget rule violations
        
        Returns structured violations instead of plain strings
        """
        violations = []
        
        if percentages["fixed"] > thresholds["fixed"]:
            excess = percentages["fixed"] - thresholds["fixed"]
            violations.append({
                "type": "fixed_high",
                "severity": "high",
                "current": percentages["fixed"],
                "threshold": thresholds["fixed"],
                "excess": round(excess, 1),
                "message": f"Fixed obligations are {percentages['fixed']:.1f}% of income ({excess:.1f}% over safe limit)"
            })
        
        if percentages["essential"] > thresholds["essential"]:
            excess = percentages["essential"] - thresholds["essential"]
            violations.append({
                "type": "essential_high",
                "severity": "medium",
                "current": percentages["essential"],
                "threshold": thresholds["essential"],
                "excess": round(excess, 1),
                "message": f"Essential spending is {percentages['essential']:.1f}% of income ({excess:.1f}% over recommended)"
            })
        
        if percentages["lifestyle"] > thresholds["lifestyle"]:
            excess = percentages["lifestyle"] - thresholds["lifestyle"]
            violations.append({
                "type": "lifestyle_high",
                "severity": "medium",
                "current": percentages["lifestyle"],
                "threshold": thresholds["lifestyle"],
                "excess": round(excess, 1),
                "message": f"Lifestyle spending is {percentages['lifestyle']:.1f}% of income ({excess:.1f}% over budget)"
            })
        
        if percentages["savings"] < thresholds["savings"]:
            deficit = thresholds["savings"] - percentages["savings"]
            violations.append({
                "type": "savings_low",
                "severity": "high",
                "current": percentages["savings"],
                "threshold": thresholds["savings"],
                "deficit": round(deficit, 1),
                "message": f"Savings rate is only {percentages['savings']:.1f}% ({deficit:.1f}% below target)"
            })
        
        return violations
    
    @staticmethod
    def _detect_money_leaks(
        spending: Dict[str, Dict[str, float]], 
        inflation: Dict,
        income: float
    ) -> List[Dict]:
        """
        Detect money leaks using HYBRID approach:
        A. Lifestyle leaks: category spending > 5% of income
        B. Inflation leaks: essential category with high inflation AND inflation > 6%
        
        Returns structured leaks sorted by amount
        """
        leaks = []
        inflation_value = inflation["value"]
        
        # A. LIFESTYLE LEAKS: Check if any category exceeds 5% of income
        for category, amount in spending["lifestyle"].items():
            percentage = (amount / income * 100) if income > 0 else 0
            if percentage > 5.0:
                leaks.append({
                    "category": category.title(),
                    "amount": amount,
                    "percentage": round(percentage, 1),
                    "reason": "lifestyle_overspending",
                    "message": f"{category.title()} spending is {percentage:.1f}% of income (₹{amount:,.0f})"
                })
        
        # B. INFLATION LEAKS: Check essential categories with high inflation
        if inflation_value > 6.0:
            for category, amount in spending["essential"].items():
                sensitivity = FinancialDecisionEngine.INFLATION_SENSITIVITY.get(
                    category.lower(), 1.0
                )
                impact = inflation_value * sensitivity
                
                # Only flag if inflation impact is significant
                if impact > 8.0:
                    percentage = (amount / income * 100) if income > 0 else 0
                    estimated_increase = amount * (impact / 100)
                    leaks.append({
                        "category": category.title(),
                        "amount": amount,
                        "percentage": round(percentage, 1),
                        "reason": "inflation_impact",
                        "inflation_impact": round(impact, 1),
                        "estimated_increase": round(estimated_increase, 2),
                        "message": f"{category.title()} impacted by {impact:.1f}% inflation (adds ~₹{estimated_increase:,.0f})"
                    })
        
        # Sort by amount (highest first)
        leaks.sort(key=lambda x: x["amount"], reverse=True)
        
        return leaks
    
    # ========================================================================
    # STEP 5: RISK CALCULATION
    # ========================================================================
    
    @staticmethod
    def _calculate_risk(
        percentages: Dict[str, float],
        violations: List[Dict],
        inflation: Dict,
        profile: UserProfile,
        money_leaks: List[Dict]
    ) -> Tuple[int, str]:
        """
        Calculate financial risk score and level
        Uses centralized scoring module
        
        CRITICAL FIX: Now passes money_leaks to scoring function
        
        Returns:
            (risk_score: 0-100, risk_level: str)
        """
        # Use centralized scoring system
        # Note: Scoring module calculates health score (higher = better)
        # We need risk score (higher = worse), so we invert it
        
        profile_dict = {
            "has_emergency_fund": profile.has_emergency_fund,
            "medical_risk": profile.medical_risk,
            "monthly_income": profile.monthly_income
        }
        
        # Calculate health score (0-100, higher is better)
        # FIXED: Now passing money_leaks
        health_score = calculate_financial_score(
            percentages=percentages,
            violations=[v["message"] for v in violations],  # Convert to strings for scoring
            inflation=inflation,
            profile=profile_dict,
            money_leaks=money_leaks
        )
        
        # Convert health score to risk score (invert)
        risk_score = 100 - health_score
        
        # Determine risk level based on risk score
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
        violations: List[Dict],
        money_leaks: List[Dict],
        emi_pressure: Dict
    ) -> List[str]:
        """
        Generate specific, actionable recommendations with ₹ amounts
        
        CRITICAL: Returns only top 5 recommendations
        Includes EMI pressure insights
        """
        recommendations = []
        income = profile.monthly_income
        
        # Savings recommendations
        current_savings = (percentages["savings"] / 100) * income
        target_savings = (thresholds["savings"] / 100) * income
        if current_savings < target_savings:
            deficit = target_savings - current_savings
            recommendations.append(
                f"Increase monthly savings by ₹{deficit:,.0f} to reach {thresholds['savings']}% target "
                f"(currently at {percentages['savings']:.1f}%)"
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
            if leak["reason"] == "inflation_impact":
                recommendations.append(
                    f"Monitor {leak['category']} spending (₹{leak['amount']:,.0f}/month) - "
                    f"inflation impact of {leak['inflation_impact']}% adds ~₹{leak['estimated_increase']:,.0f}"
                )
            else:  # lifestyle_overspending
                recommendations.append(
                    f"Reduce {leak['category']} spending from ₹{leak['amount']:,.0f} ({leak['percentage']:.1f}% of income) - "
                    f"this is a money leak"
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
        
        # EMI optimization (INTEGRATED from inflation_engine)
        if emi_pressure["emi_pressure"] in ["medium", "high"]:
            recommendations.append(
                f"EMI burden is {emi_pressure['percentage']:.1f}% of income (₹{profile.emi_amount:,.0f}) - "
                f"{emi_pressure['impact']}. Potential increase: ₹{emi_pressure['projected_increase']:,.0f} if rates rise."
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
        
        # CRITICAL: Return only top 5 recommendations
        return recommendations[:5]
    
    # ========================================================================
    # STEP 7: ACTION PRIORITIZATION
    # ========================================================================
    
    @staticmethod
    def _prioritize_actions(
        recommendations: List[str],
        risk_level: str,
        violations: List[Dict]
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
    
    # ========================================================================
    # STEP 8: SURVIVAL METRIC
    # ========================================================================
    
    @staticmethod
    def _calculate_survival_months(
        savings_amount: float,
        monthly_expenses: float
    ) -> float:
        """
        Calculate how many months user can survive on current savings
        
        Args:
            savings_amount: Current savings amount
            monthly_expenses: Monthly expenses (not income)
            
        Returns:
            Number of months of survival
        """
        if monthly_expenses <= 0:
            return 0.0
        
        # Survival months = savings / monthly expenses
        survival_months = savings_amount / monthly_expenses
        
        return round(survival_months, 1)


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
