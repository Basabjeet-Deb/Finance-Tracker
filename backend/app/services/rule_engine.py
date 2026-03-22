"""
Rule Engine Service
Core financial rules and constraint evaluation

FOCUSED RESPONSIBILITIES:
- Constraint evaluation (not scoring, not recommendations)
- Inflation-aware threshold adjustment
- Structured violation detection
- Savings computed as leftover (not input)
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SpendingCategory(Enum):
    """Hierarchical spending categories"""
    # Fixed Obligations
    RENT = "Rent"
    EMI = "EMI"
    INSURANCE = "Insurance"
    UTILITIES = "Utilities"
    
    # Essentials
    FOOD = "Food"
    TRANSPORT = "Transport"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    
    # Lifestyle
    EATING_OUT = "Eating Out"
    SHOPPING = "Shopping"
    SUBSCRIPTIONS = "Subscriptions"
    ENTERTAINMENT = "Entertainment"
    
    # Unexpected
    EMERGENCY = "Emergency"
    MEDICAL_EMERGENCY = "Medical Emergency"


class CategoryType(Enum):
    """
    Category hierarchy types
    
    CRITICAL: Savings is NOT a category - it's computed as leftover money
    """
    FIXED = "fixed"
    ESSENTIAL = "essential"
    LIFESTYLE = "lifestyle"
    UNEXPECTED = "unexpected"


# Category mapping - REMOVED SAVINGS
CATEGORY_HIERARCHY = {
    CategoryType.FIXED: [
        SpendingCategory.RENT,
        SpendingCategory.EMI,
        SpendingCategory.INSURANCE,
        SpendingCategory.UTILITIES
    ],
    CategoryType.ESSENTIAL: [
        SpendingCategory.FOOD,
        SpendingCategory.TRANSPORT,
        SpendingCategory.HEALTHCARE,
        SpendingCategory.EDUCATION
    ],
    CategoryType.LIFESTYLE: [
        SpendingCategory.EATING_OUT,
        SpendingCategory.SHOPPING,
        SpendingCategory.SUBSCRIPTIONS,
        SpendingCategory.ENTERTAINMENT
    ],
    CategoryType.UNEXPECTED: [
        SpendingCategory.EMERGENCY,
        SpendingCategory.MEDICAL_EMERGENCY
    ]
}


@dataclass
class FinancialProfile:
    """User's financial profile"""
    monthly_income: float
    emi_amount: float = 0.0
    medical_risk: str = "low"
    family_dependency: int = 0
    has_emergency_fund: bool = False
    emergency_fund_months: int = 0


@dataclass
class SpendingData:
    """
    User's spending data by category
    
    CRITICAL: No savings field - savings is computed separately
    """
    fixed: Dict[str, float]
    essential: Dict[str, float]
    lifestyle: Dict[str, float]
    unexpected: Dict[str, float]


@dataclass
class FinancialConstraints:
    """Financial constraints and thresholds"""
    fixed_max: float = 50.0
    essential_max: float = 30.0
    lifestyle_max: float = 20.0
    savings_min: float = 20.0
    food_min: float = 10.0
    transport_min: float = 5.0
    healthcare_min: float = 2.0
    emergency_fund_target_months: int = 6


@dataclass
class Violation:
    """Structured violation with priority"""
    type: str
    current: float
    limit: float
    severity: str  # low, medium, high
    priority: int  # 1 (highest) to 5 (lowest)
    message: str


class RuleEngine:
    """
    Core rule engine for financial constraint evaluation
    
    DOES NOT:
    - Calculate risk scores (use scoring module)
    - Generate recommendations (use optimizer)
    - Format output (use financial_engine)
    
    DOES:
    - Evaluate constraints
    - Detect violations
    - Adjust thresholds based on inflation
    """
    
    @staticmethod
    def calculate_allocation(spending: Dict, income: float) -> Dict[str, float]:
        """
        Calculate current spending allocation as % of income
        
        CRITICAL FIX: Savings is computed as leftover, not from input
        
        Returns:
            {
                "fixed": %,
                "essential": %,
                "lifestyle": %,
                "unexpected": %,
                "savings": % (computed from remaining income)
            }
        """
        fixed_total = sum(spending.get('fixed', {}).values())
        essential_total = sum(spending.get('essential', {}).values())
        lifestyle_total = sum(spending.get('lifestyle', {}).values())
        unexpected_total = sum(spending.get('unexpected', {}).values())
        
        # Total spending = fixed + essential + lifestyle + unexpected
        total_spending = fixed_total + essential_total + lifestyle_total + unexpected_total
        
        # Savings = income - total_spending (leftover money)
        savings_amount = income - total_spending
        
        return {
            "fixed": round((fixed_total / income * 100), 1) if income > 0 else 0,
            "essential": round((essential_total / income * 100), 1) if income > 0 else 0,
            "lifestyle": round((lifestyle_total / income * 100), 1) if income > 0 else 0,
            "unexpected": round((unexpected_total / income * 100), 1) if income > 0 else 0,
            "savings": round((savings_amount / income * 100), 1) if income > 0 else 0,
            "total_spending": round((total_spending / income * 100), 1) if income > 0 else 0
        }
    
    @staticmethod
    def evaluate_constraints(
        allocation: Dict[str, float],
        constraints: FinancialConstraints
    ) -> List[Violation]:
        """
        Evaluate current allocation against constraints
        
        Returns structured violations with priority
        """
        violations = []
        
        # Priority 1: Fixed obligations too high (critical)
        if allocation["fixed"] > constraints.fixed_max:
            excess = allocation["fixed"] - constraints.fixed_max
            violations.append(Violation(
                type="fixed_high",
                current=allocation["fixed"],
                limit=constraints.fixed_max,
                severity="high",
                priority=1,
                message=f"Fixed obligations are {allocation['fixed']:.1f}% of income ({excess:.1f}% over safe limit)"
            ))
        
        # Priority 1: Savings too low (critical)
        if allocation["savings"] < constraints.savings_min:
            deficit = constraints.savings_min - allocation["savings"]
            violations.append(Violation(
                type="savings_low",
                current=allocation["savings"],
                limit=constraints.savings_min,
                severity="high",
                priority=1,
                message=f"Savings rate is only {allocation['savings']:.1f}% ({deficit:.1f}% below target)"
            ))
        
        # Priority 2: Essential spending too high
        if allocation["essential"] > constraints.essential_max:
            excess = allocation["essential"] - constraints.essential_max
            violations.append(Violation(
                type="essential_high",
                current=allocation["essential"],
                limit=constraints.essential_max,
                severity="medium",
                priority=2,
                message=f"Essential spending is {allocation['essential']:.1f}% of income ({excess:.1f}% over recommended)"
            ))
        
        # Priority 3: Lifestyle spending too high
        if allocation["lifestyle"] > constraints.lifestyle_max:
            excess = allocation["lifestyle"] - constraints.lifestyle_max
            violations.append(Violation(
                type="lifestyle_high",
                current=allocation["lifestyle"],
                limit=constraints.lifestyle_max,
                severity="medium",
                priority=3,
                message=f"Lifestyle spending is {allocation['lifestyle']:.1f}% of income ({excess:.1f}% over budget)"
            ))
        
        # Sort by priority
        violations.sort(key=lambda v: v.priority)
        
        return violations
    
    @staticmethod
    def build_constraints(
        profile: FinancialProfile,
        inflation: Optional[Dict] = None,
        emi_pressure: Optional[Dict] = None
    ) -> FinancialConstraints:
        """
        Build dynamic constraints based on user profile, inflation, AND EMI pressure
        
        CRITICAL FIX: Now integrates inflation data and EMI pressure
        
        Args:
            profile: User financial profile
            inflation: Inflation data with "pressure" and "value"
            emi_pressure: EMI pressure data from inflation_engine.calculate_emi_pressure()
            
        Returns:
            Adjusted financial constraints
        """
        constraints = FinancialConstraints()
        
        # INFLATION ADJUSTMENTS
        if inflation:
            pressure = inflation.get("pressure", "medium")
            
            if pressure == "high":
                # High inflation: allow more essential spending, reduce lifestyle
                constraints.essential_max += 5.0
                constraints.lifestyle_max -= 5.0
                constraints.savings_min = max(15.0, constraints.savings_min - 5.0)
                logger.info(f"High inflation ({inflation.get('value')}%) - adjusted thresholds")
            
            elif pressure == "medium":
                # Medium inflation: slight adjustments
                constraints.essential_max += 2.0
                constraints.lifestyle_max -= 2.0
                logger.info(f"Medium inflation ({inflation.get('value')}%) - slight adjustments")
        
        # EMI PRESSURE ADJUSTMENTS (INTEGRATED from inflation_engine)
        if emi_pressure:
            pressure_level = emi_pressure.get("emi_pressure", "low")
            
            if pressure_level == "high":
                # High EMI pressure: significantly reduce lifestyle, maintain savings
                constraints.lifestyle_max = max(10.0, constraints.lifestyle_max - 5.0)
                constraints.savings_min = max(15.0, constraints.savings_min)
                logger.info(f"High EMI pressure ({emi_pressure.get('percentage')}%) - reduced lifestyle allowance")
            
            elif pressure_level == "medium":
                # Medium EMI pressure: moderate lifestyle reduction
                constraints.lifestyle_max = max(15.0, constraints.lifestyle_max - 3.0)
                logger.info(f"Medium EMI pressure ({emi_pressure.get('percentage')}%) - slight lifestyle reduction")
        
        # Legacy EMI adjustments (kept for backward compatibility if emi_pressure not provided)
        if not emi_pressure and profile.emi_amount > 0:
            emi_pct = (profile.emi_amount / profile.monthly_income) * 100
            if emi_pct > 30:
                constraints.lifestyle_max = 15.0
                constraints.savings_min = max(15.0, constraints.savings_min)
                logger.info(f"High EMI detected ({emi_pct:.1f}%) - adjusted constraints")
        
        # Medical risk adjustments
        if profile.medical_risk == "high":
            constraints.healthcare_min = 5.0
            constraints.emergency_fund_target_months = 12
            constraints.savings_min = max(25.0, constraints.savings_min)
            logger.info("High medical risk - increased healthcare and savings targets")
        elif profile.medical_risk == "medium":
            constraints.healthcare_min = 3.0
            constraints.emergency_fund_target_months = 9
            constraints.savings_min = max(22.0, constraints.savings_min)
        
        # Family dependency adjustments
        if profile.family_dependency > 0:
            constraints.essential_max = 35.0 + (profile.family_dependency * 2.5)
            constraints.food_min = 12.0 + (profile.family_dependency * 2.0)
            logger.info(f"Family dependency ({profile.family_dependency}) - adjusted essential budgets")
        
        # Low income adjustments
        if profile.monthly_income < 30000:
            constraints.fixed_max = 55.0
            constraints.essential_max = min(40.0, constraints.essential_max + 5.0)
            constraints.lifestyle_max = 10.0
            constraints.savings_min = 10.0
            logger.info("Low income detected - adjusted priorities")
        
        # Ensure constraints are reasonable
        constraints.essential_max = min(40.0, max(25.0, constraints.essential_max))
        constraints.lifestyle_max = min(25.0, max(10.0, constraints.lifestyle_max))
        constraints.savings_min = min(30.0, max(10.0, constraints.savings_min))
        
        return constraints


class CategorizationEngine:
    """
    Maps expenses to hierarchical categories
    
    CRITICAL FIX: Unknown categories default to lifestyle and are flagged
    """
    
    CATEGORY_MAP = {
        "Rent": SpendingCategory.RENT,
        "EMI": SpendingCategory.EMI,
        "Insurance": SpendingCategory.INSURANCE,
        "Bills": SpendingCategory.UTILITIES,
        "Utilities": SpendingCategory.UTILITIES,
        "Food": SpendingCategory.FOOD,
        "Groceries": SpendingCategory.FOOD,
        "Transport": SpendingCategory.TRANSPORT,
        "Healthcare": SpendingCategory.HEALTHCARE,
        "Education": SpendingCategory.EDUCATION,
        "Entertainment": SpendingCategory.ENTERTAINMENT,
        "Shopping": SpendingCategory.SHOPPING,
        "Dining": SpendingCategory.EATING_OUT,
        "Subscriptions": SpendingCategory.SUBSCRIPTIONS,
        "Emergency": SpendingCategory.EMERGENCY,
        "Other": SpendingCategory.SHOPPING,
    }
    
    @staticmethod
    def categorize_expense(
        category: str,
        amount: float,
        note: str = ""
    ) -> Tuple[SpendingCategory, CategoryType, bool]:
        """
        Categorize an expense into system categories
        
        Returns:
            (spending_category, category_type, is_uncategorized)
        """
        # Try to find in category map
        spending_cat = CategorizationEngine.CATEGORY_MAP.get(category)
        is_uncategorized = False
        
        if not spending_cat:
            # Unknown category - default to SHOPPING (lifestyle)
            spending_cat = SpendingCategory.SHOPPING
            is_uncategorized = True
            logger.warning(f"Uncategorized expense: '{category}' - defaulting to lifestyle")
        
        # Find category type
        for cat_type, categories in CATEGORY_HIERARCHY.items():
            if spending_cat in categories:
                return spending_cat, cat_type, is_uncategorized
        
        # Fallback to lifestyle
        return spending_cat, CategoryType.LIFESTYLE, is_uncategorized
    
    @staticmethod
    def aggregate_spending(expenses: List[Dict]) -> SpendingData:
        """
        Aggregate expenses into spending data structure
        
        CRITICAL: No savings aggregation - savings is computed separately
        """
        spending = SpendingData(
            fixed={},
            essential={},
            lifestyle={},
            unexpected={}
        )
        
        uncategorized_count = 0
        
        for expense in expenses:
            cat, cat_type, is_uncategorized = CategorizationEngine.categorize_expense(
                expense.get('category', 'Other'),
                expense.get('amount', 0),
                expense.get('note', '')
            )
            
            if is_uncategorized:
                uncategorized_count += 1
            
            cat_name = cat.value
            amount = expense.get('amount', 0)
            
            if cat_type == CategoryType.FIXED:
                spending.fixed[cat_name] = spending.fixed.get(cat_name, 0) + amount
            elif cat_type == CategoryType.ESSENTIAL:
                spending.essential[cat_name] = spending.essential.get(cat_name, 0) + amount
            elif cat_type == CategoryType.LIFESTYLE:
                spending.lifestyle[cat_name] = spending.lifestyle.get(cat_name, 0) + amount
            elif cat_type == CategoryType.UNEXPECTED:
                spending.unexpected[cat_name] = spending.unexpected.get(cat_name, 0) + amount
        
        if uncategorized_count > 0:
            logger.warning(f"{uncategorized_count} expenses were uncategorized and defaulted to lifestyle")
        
        return spending
