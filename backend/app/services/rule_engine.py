"""
Rule Engine Service
Core financial rules and constraint evaluation
"""
from typing import Dict, List, Tuple
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
    
    # Savings
    EMERGENCY_FUND = "Emergency Fund"
    INVESTMENTS = "Investments"
    CASH_SAVINGS = "Cash Savings"


class CategoryType(Enum):
    """Category hierarchy types"""
    FIXED = "fixed"
    ESSENTIAL = "essential"
    LIFESTYLE = "lifestyle"
    SAVINGS = "savings"
    UNEXPECTED = "unexpected"


# Category mapping
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
    CategoryType.SAVINGS: [
        SpendingCategory.EMERGENCY_FUND,
        SpendingCategory.INVESTMENTS,
        SpendingCategory.CASH_SAVINGS
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
    """User's spending data by category"""
    fixed: Dict[str, float]
    essential: Dict[str, float]
    lifestyle: Dict[str, float]
    savings: Dict[str, float]
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


class RuleEngine:
    """Core rule engine for financial decisions"""
    
    @staticmethod
    def calculate_allocation(spending: Dict, income: float) -> Dict[str, float]:
        """Calculate current spending allocation as % of income"""
        fixed_total = sum(spending.get('fixed', {}).values())
        essential_total = sum(spending.get('essential', {}).values())
        lifestyle_total = sum(spending.get('lifestyle', {}).values())
        savings_total = sum(spending.get('savings', {}).values())
        unexpected_total = sum(spending.get('unexpected', {}).values())
        
        total_spending = fixed_total + essential_total + lifestyle_total + unexpected_total
        
        return {
            "fixed": (fixed_total / income * 100) if income > 0 else 0,
            "essential": (essential_total / income * 100) if income > 0 else 0,
            "lifestyle": (lifestyle_total / income * 100) if income > 0 else 0,
            "savings": (savings_total / income * 100) if income > 0 else 0,
            "unexpected": (unexpected_total / income * 100) if income > 0 else 0,
            "total_spending": (total_spending / income * 100) if income > 0 else 0,
            "remaining": ((income - total_spending) / income * 100) if income > 0 else 0
        }
    
    @staticmethod
    def evaluate_constraints(
        allocation: Dict[str, float],
        constraints: FinancialConstraints
    ) -> Dict[str, Dict]:
        """Evaluate current allocation against constraints"""
        violations = {}
        
        if allocation["fixed"] > constraints.fixed_max:
            violations["fixed"] = {
                "current": allocation["fixed"],
                "max": constraints.fixed_max,
                "excess": allocation["fixed"] - constraints.fixed_max,
                "severity": "high"
            }
        
        if allocation["essential"] > constraints.essential_max:
            violations["essential"] = {
                "current": allocation["essential"],
                "max": constraints.essential_max,
                "excess": allocation["essential"] - constraints.essential_max,
                "severity": "medium"
            }
        
        if allocation["lifestyle"] > constraints.lifestyle_max:
            violations["lifestyle"] = {
                "current": allocation["lifestyle"],
                "max": constraints.lifestyle_max,
                "excess": allocation["lifestyle"] - constraints.lifestyle_max,
                "severity": "low"
            }
        
        if allocation["savings"] < constraints.savings_min:
            violations["savings"] = {
                "current": allocation["savings"],
                "min": constraints.savings_min,
                "deficit": constraints.savings_min - allocation["savings"],
                "severity": "high"
            }
        
        return violations
    
    @staticmethod
    def assess_risk_level(
        allocation: Dict[str, float],
        violations: Dict,
        profile: Dict
    ) -> str:
        """Assess overall financial risk level"""
        risk_score = 0
        
        if allocation["fixed"] > 50:
            risk_score += 3
        elif allocation["fixed"] > 45:
            risk_score += 2
        
        if allocation["savings"] < 10:
            risk_score += 3
        elif allocation["savings"] < 15:
            risk_score += 2
        
        if not profile.get("has_emergency_fund", False):
            risk_score += 2
        
        if profile.get("medical_risk") == "high" and allocation["savings"] < 15:
            risk_score += 2
        
        risk_score += len(violations)
        
        if allocation["total_spending"] > 95:
            risk_score += 3
        elif allocation["total_spending"] > 85:
            risk_score += 1
        
        if risk_score >= 8:
            return "critical"
        elif risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def build_constraints(profile: Dict) -> FinancialConstraints:
        """Build dynamic constraints based on user profile"""
        constraints = FinancialConstraints()
        
        # Adjust for high EMI
        emi_amount = profile.get("emi_amount", 0)
        monthly_income = profile.get("monthly_income", 1)
        
        if emi_amount > 0:
            emi_pct = (emi_amount / monthly_income) * 100
            if emi_pct > 30:
                constraints.lifestyle_max = 15.0
                constraints.savings_min = 15.0
        
        # Adjust for medical risk
        medical_risk = profile.get("medical_risk", "low")
        if medical_risk == "high":
            constraints.healthcare_min = 5.0
            constraints.emergency_fund_target_months = 12
        elif medical_risk == "medium":
            constraints.healthcare_min = 3.0
            constraints.emergency_fund_target_months = 9
        
        # Adjust for family dependency
        family_dependency = profile.get("family_dependency", 0)
        if family_dependency > 0:
            constraints.essential_max = 35.0 + (family_dependency * 2.5)
            constraints.food_min = 12.0 + (family_dependency * 2.0)
        
        # Adjust for low income
        if monthly_income < 30000:
            constraints.fixed_max = 55.0
            constraints.essential_max = 35.0
            constraints.lifestyle_max = 10.0
            constraints.savings_min = 10.0
        
        return constraints



class CategorizationEngine:
    """Maps expenses to hierarchical categories"""
    
    CATEGORY_MAP = {
        "Rent": SpendingCategory.RENT,
        "Bills": SpendingCategory.UTILITIES,
        "Food": SpendingCategory.FOOD,
        "Transport": SpendingCategory.TRANSPORT,
        "Entertainment": SpendingCategory.ENTERTAINMENT,
        "Other": SpendingCategory.SHOPPING,
    }
    
    @staticmethod
    def categorize_expense(category: str, amount: float, note: str = "") -> Tuple[SpendingCategory, CategoryType]:
        """Categorize an expense into system categories"""
        spending_cat = CategorizationEngine.CATEGORY_MAP.get(category, SpendingCategory.SHOPPING)
        
        for cat_type, categories in CATEGORY_HIERARCHY.items():
            if spending_cat in categories:
                return spending_cat, cat_type
        
        return spending_cat, CategoryType.LIFESTYLE
    
    @staticmethod
    def aggregate_spending(expenses: List[Dict]) -> SpendingData:
        """Aggregate expenses into spending data structure"""
        spending = SpendingData(
            fixed={},
            essential={},
            lifestyle={},
            savings={},
            unexpected={}
        )
        
        for expense in expenses:
            cat, cat_type = CategorizationEngine.categorize_expense(
                expense.get('category', 'Other'),
                expense.get('amount', 0),
                expense.get('note', '')
            )
            
            cat_name = cat.value
            amount = expense.get('amount', 0)
            
            if cat_type == CategoryType.FIXED:
                spending.fixed[cat_name] = spending.fixed.get(cat_name, 0) + amount
            elif cat_type == CategoryType.ESSENTIAL:
                spending.essential[cat_name] = spending.essential.get(cat_name, 0) + amount
            elif cat_type == CategoryType.LIFESTYLE:
                spending.lifestyle[cat_name] = spending.lifestyle.get(cat_name, 0) + amount
            elif cat_type == CategoryType.SAVINGS:
                spending.savings[cat_name] = spending.savings.get(cat_name, 0) + amount
            elif cat_type == CategoryType.UNEXPECTED:
                spending.unexpected[cat_name] = spending.unexpected.get(cat_name, 0) + amount
        
        return spending


class ConstraintBuilder:
    """Builds financial constraints based on user profile"""
    
    @staticmethod
    def build_constraints(profile: FinancialProfile) -> FinancialConstraints:
        """Build dynamic constraints based on user profile"""
        constraints = FinancialConstraints()
        
        # Adjust for high EMI
        if profile.emi_amount > 0:
            emi_pct = (profile.emi_amount / profile.monthly_income) * 100
            if emi_pct > 30:
                constraints.lifestyle_max = 15.0
                constraints.savings_min = 15.0
                logger.info(f"High EMI detected ({emi_pct:.1f}%) - adjusted constraints")
        
        # Adjust for medical risk
        if profile.medical_risk == "high":
            constraints.healthcare_min = 5.0
            constraints.emergency_fund_target_months = 12
            logger.info("High medical risk - increased healthcare and emergency fund targets")
        elif profile.medical_risk == "medium":
            constraints.healthcare_min = 3.0
            constraints.emergency_fund_target_months = 9
        
        # Adjust for family dependency
        if profile.family_dependency > 0:
            constraints.essential_max = 35.0 + (profile.family_dependency * 2.5)
            constraints.food_min = 12.0 + (profile.family_dependency * 2.0)
            logger.info(f"Family dependency ({profile.family_dependency}) - adjusted essential budgets")
        
        # Adjust for low income
        if profile.monthly_income < 30000:
            constraints.fixed_max = 55.0
            constraints.essential_max = 35.0
            constraints.lifestyle_max = 10.0
            constraints.savings_min = 10.0
            logger.info("Low income detected - adjusted priorities")
        
        return constraints
