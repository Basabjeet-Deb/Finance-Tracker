"""
Cost Optimization Service (formerly Deals Service)

Provides targeted cost-saving opportunities for overspending categories
Integrated with financial decision engine to improve financial health

DOES:
- Identify cost-saving opportunities in problem areas
- Filter based on financial risk level
- Prioritize high-impact categories
- Return measurable savings potential

DOES NOT:
- Encourage unnecessary spending
- Show deals when user is in high financial risk
- Promote deals in healthy spending categories
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# Cost optimization opportunities mapped to spending categories
OPTIMIZATION_OPPORTUNITIES = {
    "food": [
        {
            "type": "subscription",
            "provider": "Swiggy One",
            "description": "Free delivery + exclusive discounts",
            "estimated_monthly_savings": 500,
            "condition": "If ordering 8+ times/month"
        },
        {
            "type": "cashback",
            "provider": "Zomato Pro",
            "description": "Up to 25% off on dining",
            "estimated_monthly_savings": 400,
            "condition": "For frequent dining out"
        }
    ],
    "groceries": [
        {
            "type": "bulk_buying",
            "provider": "BigBasket/Amazon Pantry",
            "description": "Subscribe & Save for staples",
            "estimated_monthly_savings": 300,
            "condition": "10-15% savings on recurring items"
        }
    ],
    "transport": [
        {
            "type": "pass",
            "provider": "Metro/Bus Pass",
            "description": "Monthly commute pass",
            "estimated_monthly_savings": 800,
            "condition": "If commuting 20+ days/month"
        },
        {
            "type": "carpooling",
            "provider": "Quick Ride/BlaBlaCar",
            "description": "Share rides to work",
            "estimated_monthly_savings": 1200,
            "condition": "50% reduction in fuel costs"
        }
    ],
    "eating out": [
        {
            "type": "meal_prep",
            "provider": "Home cooking",
            "description": "Reduce dining out frequency",
            "estimated_monthly_savings": 2000,
            "condition": "Cook 3-4 meals/week instead"
        },
        {
            "type": "subscription",
            "provider": "Dineout Passport",
            "description": "20-40% off at restaurants",
            "estimated_monthly_savings": 600,
            "condition": "If dining out 4+ times/month"
        }
    ],
    "shopping": [
        {
            "type": "cashback",
            "provider": "Credit card rewards",
            "description": "Use cashback cards for purchases",
            "estimated_monthly_savings": 300,
            "condition": "2-5% cashback on shopping"
        },
        {
            "type": "behavioral",
            "provider": "30-day rule",
            "description": "Wait 30 days before non-essential purchases",
            "estimated_monthly_savings": 1500,
            "condition": "Reduces impulse buying"
        }
    ],
    "subscriptions": [
        {
            "type": "audit",
            "provider": "Subscription review",
            "description": "Cancel unused subscriptions",
            "estimated_monthly_savings": 500,
            "condition": "Review all active subscriptions"
        },
        {
            "type": "bundling",
            "provider": "Family plans",
            "description": "Share Netflix/Spotify/Prime",
            "estimated_monthly_savings": 400,
            "condition": "Split costs with family/friends"
        }
    ],
    "entertainment": [
        {
            "type": "free_alternatives",
            "provider": "Public events/parks",
            "description": "Use free entertainment options",
            "estimated_monthly_savings": 800,
            "condition": "Replace 2-3 paid activities"
        }
    ],
    "utilities": [
        {
            "type": "energy_saving",
            "provider": "LED bulbs + efficient appliances",
            "description": "Reduce electricity consumption",
            "estimated_monthly_savings": 300,
            "condition": "15-20% reduction in bills"
        }
    ]
}


class CostOptimizationService:
    """
    Provides cost-saving opportunities for overspending categories
    Integrated with financial decision engine
    """
    
    @staticmethod
    def get_optimization_opportunities(
        spending_by_category: Dict[str, float],
        income: float,
        risk_level: str,
        money_leaks: List[Dict],
        violations: List[Dict]
    ) -> List[Dict]:
        """
        Generate cost optimization opportunities based on financial context
        
        CRITICAL RULES:
        - No opportunities if risk_level == "critical" (focus on essentials only)
        - Limited opportunities if risk_level == "high" (only behavioral changes)
        - Only show for overspending categories or money leaks
        - Max 2 opportunities (highest impact)
        - Must include measurable savings potential
        
        Args:
            spending_by_category: Dict of category -> monthly amount
            income: Monthly income
            risk_level: Financial risk level (low/medium/high/critical)
            money_leaks: List of money leak dicts from financial_engine
            violations: List of violation dicts from financial_engine
            
        Returns:
            List of optimization opportunities with savings potential
        """
        # RULE 1: No deals if critical risk
        if risk_level == "critical":
            logger.info("Critical risk level - no optimization opportunities shown")
            return []
        
        # RULE 2: Only behavioral changes if high risk
        if risk_level == "high":
            return CostOptimizationService._get_behavioral_optimizations(
                spending_by_category, income, money_leaks
            )
        
        # Identify problem categories
        problem_categories = CostOptimizationService._identify_problem_categories(
            spending_by_category, income, money_leaks, violations
        )
        
        if not problem_categories:
            logger.info("No overspending detected - no optimization opportunities needed")
            return []
        
        # Generate opportunities for problem categories
        opportunities = []
        
        for category_info in problem_categories:
            category = category_info["category"]
            amount = category_info["amount"]
            percentage = category_info["percentage"]
            issue = category_info["issue"]
            
            # Get optimization options for this category
            category_lower = category.lower()
            options = OPTIMIZATION_OPPORTUNITIES.get(category_lower, [])
            
            if not options:
                # Generic optimization for unmapped categories
                options = [
                    {
                        "type": "reduction",
                        "provider": "Budget tracking",
                        "description": f"Reduce {category} spending by 20%",
                        "estimated_monthly_savings": amount * 0.2,
                        "condition": "Track and limit spending"
                    }
                ]
            
            # Pick best option (highest savings)
            best_option = max(options, key=lambda x: x["estimated_monthly_savings"])
            
            # Calculate actual savings potential
            potential_savings = min(
                best_option["estimated_monthly_savings"],
                amount * 0.3  # Cap at 30% of current spending
            )
            
            opportunities.append({
                "category": category,
                "current_spending": round(amount, 2),
                "percentage_of_income": round(percentage, 1),
                "issue": issue,
                "optimization": {
                    "type": best_option["type"],
                    "provider": best_option["provider"],
                    "description": best_option["description"],
                    "condition": best_option["condition"],
                    "potential_monthly_savings": round(potential_savings, 2),
                    "annual_impact": round(potential_savings * 12, 2)
                },
                "priority": category_info["priority"]
            })
        
        # Sort by priority and potential savings
        opportunities.sort(
            key=lambda x: (x["priority"], x["optimization"]["potential_monthly_savings"]),
            reverse=False  # Lower priority number = higher priority
        )
        
        # RULE 3: Return max 2 opportunities (highest impact)
        return opportunities[:2]
    
    @staticmethod
    def _identify_problem_categories(
        spending_by_category: Dict[str, float],
        income: float,
        money_leaks: List[Dict],
        violations: List[Dict]
    ) -> List[Dict]:
        """
        Identify categories that are overspending or problematic
        
        Returns list of problem categories with context
        """
        problem_categories = []
        
        # Extract money leak categories (highest priority)
        for leak in money_leaks:
            category = leak.get("category", "").lower()
            amount = leak.get("amount", 0)
            percentage = leak.get("percentage", 0)
            reason = leak.get("reason", "")
            
            if amount > 0:
                problem_categories.append({
                    "category": category.title(),
                    "amount": amount,
                    "percentage": percentage,
                    "issue": f"Money leak: {reason}",
                    "priority": 1  # Highest priority
                })
        
        # Check for lifestyle overspending from violations
        lifestyle_violation = next(
            (v for v in violations if v.get("type") == "lifestyle_high"),
            None
        )
        
        if lifestyle_violation:
            # Find top lifestyle spending categories
            lifestyle_categories = ["eating out", "shopping", "entertainment", "subscriptions"]
            
            for cat in lifestyle_categories:
                amount = spending_by_category.get(cat, 0)
                if amount > 0:
                    percentage = (amount / income * 100) if income > 0 else 0
                    
                    # Only include if significant (>3% of income)
                    if percentage > 3.0:
                        # Skip if already in money leaks
                        if not any(p["category"].lower() == cat for p in problem_categories):
                            problem_categories.append({
                                "category": cat.title(),
                                "amount": amount,
                                "percentage": percentage,
                                "issue": "Lifestyle overspending",
                                "priority": 2
                            })
        
        # Check for high percentage categories (>8% of income)
        for category, amount in spending_by_category.items():
            percentage = (amount / income * 100) if income > 0 else 0
            
            if percentage > 8.0:
                # Skip if already identified
                if not any(p["category"].lower() == category.lower() for p in problem_categories):
                    problem_categories.append({
                        "category": category.title(),
                        "amount": amount,
                        "percentage": percentage,
                        "issue": f"High spending ({percentage:.1f}% of income)",
                        "priority": 3
                    })
        
        return problem_categories
    
    @staticmethod
    def _get_behavioral_optimizations(
        spending_by_category: Dict[str, float],
        income: float,
        money_leaks: List[Dict]
    ) -> List[Dict]:
        """
        Get behavioral optimization suggestions for high-risk users
        
        Focus on free/low-cost behavioral changes, not subscriptions or deals
        """
        opportunities = []
        
        # Behavioral optimizations (no cost to implement)
        behavioral_tips = {
            "eating out": {
                "description": "Cook at home 4-5 days/week instead of ordering out",
                "savings_multiplier": 0.4
            },
            "shopping": {
                "description": "Implement 30-day rule: wait 30 days before non-essential purchases",
                "savings_multiplier": 0.3
            },
            "entertainment": {
                "description": "Use free alternatives: parks, libraries, community events",
                "savings_multiplier": 0.5
            },
            "subscriptions": {
                "description": "Cancel unused subscriptions immediately",
                "savings_multiplier": 0.6
            },
            "transport": {
                "description": "Use public transport or carpool instead of solo rides",
                "savings_multiplier": 0.35
            }
        }
        
        # Focus on money leaks first
        for leak in money_leaks[:2]:
            category = leak.get("category", "").lower()
            amount = leak.get("amount", 0)
            percentage = leak.get("percentage", 0)
            
            tip = behavioral_tips.get(category)
            if tip:
                potential_savings = amount * tip["savings_multiplier"]
                
                opportunities.append({
                    "category": category.title(),
                    "current_spending": round(amount, 2),
                    "percentage_of_income": round(percentage, 1),
                    "issue": "Money leak - immediate action needed",
                    "optimization": {
                        "type": "behavioral",
                        "provider": "Free behavioral change",
                        "description": tip["description"],
                        "condition": "No cost to implement",
                        "potential_monthly_savings": round(potential_savings, 2),
                        "annual_impact": round(potential_savings * 12, 2)
                    },
                    "priority": 1
                })
        
        return opportunities[:2]


# Backward compatibility alias
class DealsService:
    """
    DEPRECATED: Use CostOptimizationService instead
    
    This class is kept for backward compatibility only
    """
    
    @staticmethod
    def get_deals_for_user(spending_aggregate: dict) -> list:
        """
        DEPRECATED: Use CostOptimizationService.get_optimization_opportunities()
        """
        logger.warning(
            "DealsService.get_deals_for_user() is DEPRECATED. "
            "Use CostOptimizationService.get_optimization_opportunities() instead."
        )
        return []
