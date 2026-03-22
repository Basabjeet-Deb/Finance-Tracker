"""
Optimization Engine - Constraint optimization for spending reallocation
Extracted from financial_engine.py for clean architecture
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """Result of optimization"""
    current_allocation: Dict[str, float]
    recommended_allocation: Dict[str, float]
    reallocation_needed: Dict[str, float]
    savings_potential: float
    risk_level: str
    priority_actions: List[str]


class OptimizationEngine:
    """Constraint optimization for spending reallocation"""
    
    @staticmethod
    def optimize_allocation(
        spending,
        profile,
        constraints,
        inflation_data: Optional[Dict] = None
    ) -> OptimizationResult:
        """
        Optimize spending allocation to maximize savings and stability
        
        Steps:
        1. Calculate current allocation
        2. Identify violations
        3. Compute recommended allocation
        4. Generate reallocation plan
        5. Calculate savings potential
        """
        from app.services.rule_engine import RuleEngine
        
        income = profile.monthly_income
        
        # Step 1: Current allocation
        current_alloc = RuleEngine.calculate_allocation(spending, income)
        
        # Step 2: Identify violations
        violations = RuleEngine.evaluate_constraints(current_alloc, constraints)
        
        # Step 3: Compute recommended allocation
        recommended = OptimizationEngine._compute_recommended_allocation(
            current_alloc,
            constraints,
            profile,
            inflation_data
        )
        
        # Step 4: Generate reallocation plan
        reallocation = OptimizationEngine._generate_reallocation_plan(
            spending,
            current_alloc,
            recommended,
            income,
            violations
        )
        
        # Step 5: Calculate savings potential
        savings_potential = OptimizationEngine._calculate_savings_potential(
            current_alloc,
            recommended,
            income
        )
        
        # Step 6: Generate priority actions
        priority_actions = OptimizationEngine._generate_priority_actions(
            violations,
            reallocation,
            profile,
            income
        )
        
        # Step 7: Assess risk
        risk_level = RuleEngine.assess_risk_level(current_alloc, violations, profile)
        
        return OptimizationResult(
            current_allocation=current_alloc,
            recommended_allocation=recommended,
            reallocation_needed=reallocation,
            savings_potential=savings_potential,
            risk_level=risk_level,
            priority_actions=priority_actions
        )
    
    @staticmethod
    def _compute_recommended_allocation(
        current: Dict[str, float],
        constraints,
        profile,
        inflation_data: Optional[Dict]
    ) -> Dict[str, float]:
        """Compute optimal allocation percentages"""
        recommended = {}
        
        # Fixed obligations - cannot change
        recommended["fixed"] = current["fixed"]
        
        # Adjust for inflation if available
        inflation_adjustment = 0
        if inflation_data:
            food_inflation = inflation_data.get("food_inflation", 0)
            fuel_inflation = inflation_data.get("fuel_inflation", 0)
            
            # Allow higher essential budget if inflation is high
            if food_inflation > 6:
                inflation_adjustment += 2
            if fuel_inflation > 8:
                inflation_adjustment += 1
        
        # Essentials - adjust for inflation
        essential_target = min(
            constraints.essential_max,
            max(constraints.food_min + constraints.transport_min + constraints.healthcare_min,
                current["essential"])
        ) + inflation_adjustment
        recommended["essential"] = essential_target
        
        # Calculate remaining after fixed and essential
        remaining = 100 - recommended["fixed"] - recommended["essential"]
        
        # Prioritize savings
        savings_target = max(constraints.savings_min, min(30, remaining * 0.4))
        recommended["savings"] = savings_target
        
        # Lifestyle gets what's left
        lifestyle_target = max(0, remaining - savings_target)
        lifestyle_target = min(lifestyle_target, constraints.lifestyle_max)
        recommended["lifestyle"] = lifestyle_target
        
        # Adjust if total > 100
        total = sum([recommended["fixed"], recommended["essential"], 
                     recommended["savings"], recommended["lifestyle"]])
        
        if total > 100:
            # Reduce lifestyle first
            excess = total - 100
            if recommended["lifestyle"] >= excess:
                recommended["lifestyle"] -= excess
            else:
                recommended["lifestyle"] = 0
                excess -= recommended["lifestyle"]
                # Then reduce savings if needed
                recommended["savings"] = max(10, recommended["savings"] - excess)
        
        return recommended
    
    @staticmethod
    def _generate_reallocation_plan(
        spending,
        current: Dict[str, float],
        recommended: Dict[str, float],
        income: float,
        violations: Dict
    ) -> Dict[str, float]:
        """Generate specific reallocation amounts"""
        reallocation = {}
        
        for category in ["fixed", "essential", "lifestyle", "savings"]:
            diff_pct = recommended[category] - current[category]
            diff_amount = (diff_pct / 100) * income
            
            if abs(diff_amount) > 100:  # Only if significant
                reallocation[category] = diff_amount
        
        return reallocation
    
    @staticmethod
    def _calculate_savings_potential(
        current: Dict[str, float],
        recommended: Dict[str, float],
        income: float
    ) -> float:
        """Calculate potential savings increase"""
        current_savings = (current["savings"] / 100) * income
        recommended_savings = (recommended["savings"] / 100) * income
        
        return recommended_savings - current_savings
    
    @staticmethod
    def _generate_priority_actions(
        violations: Dict,
        reallocation: Dict,
        profile,
        income: float
    ) -> List[str]:
        """Generate prioritized action items"""
        actions = []
        
        # Priority 1: Critical violations
        if "fixed" in violations and violations["fixed"]["severity"] == "high":
            excess_amount = (violations["fixed"]["excess"] / 100) * income
            actions.append(
                f"🚨 CRITICAL: Fixed expenses are {violations['fixed']['current']:.1f}% of income "
                f"(₹{excess_amount:,.0f} over limit). Consider refinancing or reducing housing costs."
            )
        
        if "savings" in violations and violations["savings"]["severity"] == "high":
            deficit_amount = (violations["savings"]["deficit"] / 100) * income
            actions.append(
                f"🚨 CRITICAL: Savings rate is only {violations['savings']['current']:.1f}% "
                f"(need ₹{deficit_amount:,.0f} more per month). Immediate action required."
            )
        
        # Priority 2: Lifestyle overspending
        if "lifestyle" in violations:
            excess_amount = (violations["lifestyle"]["excess"] / 100) * income
            actions.append(
                f"⚠️ Lifestyle spending is {violations['lifestyle']['current']:.1f}% of income. "
                f"Reduce by ₹{excess_amount:,.0f}/month."
            )
        
        # Priority 3: Reallocation suggestions
        if "lifestyle" in reallocation and reallocation["lifestyle"] < -500:
            actions.append(
                f"💡 Reduce lifestyle spending by ₹{abs(reallocation['lifestyle']):,.0f}/month"
            )
        
        if "savings" in reallocation and reallocation["savings"] > 500:
            actions.append(
                f"💰 Increase savings by ₹{reallocation['savings']:,.0f}/month to reach {profile.monthly_income * 0.2:,.0f}"
            )
        
        # Priority 4: Emergency fund
        if not profile.has_emergency_fund:
            target = profile.monthly_income * 6
            actions.append(
                f"🏦 Build emergency fund: Target ₹{target:,.0f} (6 months of expenses)"
            )
        
        # Priority 5: Specific category advice
        if "essential" in violations:
            actions.append(
                f"📊 Essential expenses are high ({violations['essential']['current']:.1f}%). "
                "Review food and transport costs."
            )
        
        return actions


class InsightGenerator:
    """Generate human-readable insights"""
    
    @staticmethod
    def generate_insights(
        result: OptimizationResult,
        spending,
        profile,
        inflation_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive financial insights
        
        Returns structured insights with:
        - Risk assessment
        - Spending analysis
        - Recommendations
        - Specific actions
        """
        income = profile.monthly_income
        current = result.current_allocation
        
        insights = {
            "risk_level": result.risk_level,
            "savings_rate": round(current["savings"], 1),
            "spending_summary": InsightGenerator._generate_spending_summary(
                current, income
            ),
            "violations": InsightGenerator._generate_violation_insights(
                result, income
            ),
            "recommendations": result.priority_actions,
            "inflation_context": InsightGenerator._generate_inflation_context(
                spending, inflation_data, income
            ),
            "optimization_potential": {
                "savings_increase": round(result.savings_potential, 2),
                "reallocation_needed": {
                    k: round(v, 2) for k, v in result.reallocation_needed.items()
                }
            }
        }
        
        return insights
    
    @staticmethod
    def _generate_spending_summary(allocation: Dict[str, float], income: float) -> Dict:
        """Generate spending summary"""
        return {
            "fixed_obligations": {
                "percentage": round(allocation["fixed"], 1),
                "amount": round((allocation["fixed"] / 100) * income, 2),
                "status": "high" if allocation["fixed"] > 50 else "normal"
            },
            "essentials": {
                "percentage": round(allocation["essential"], 1),
                "amount": round((allocation["essential"] / 100) * income, 2),
                "status": "high" if allocation["essential"] > 30 else "normal"
            },
            "lifestyle": {
                "percentage": round(allocation["lifestyle"], 1),
                "amount": round((allocation["lifestyle"] / 100) * income, 2),
                "status": "high" if allocation["lifestyle"] > 20 else "normal"
            },
            "savings": {
                "percentage": round(allocation["savings"], 1),
                "amount": round((allocation["savings"] / 100) * income, 2),
                "status": "low" if allocation["savings"] < 20 else "good"
            }
        }
    
    @staticmethod
    def _generate_violation_insights(result: OptimizationResult, income: float) -> List[Dict]:
        """Generate insights about constraint violations"""
        violations = []
        
        current = result.current_allocation
        recommended = result.recommended_allocation
        
        for category in ["fixed", "essential", "lifestyle", "savings"]:
            diff = current[category] - recommended[category]
            if abs(diff) > 2:  # Significant difference
                violations.append({
                    "category": category,
                    "current": round(current[category], 1),
                    "recommended": round(recommended[category], 1),
                    "difference": round(diff, 1),
                    "amount_difference": round((diff / 100) * income, 2)
                })
        
        return violations
    
    @staticmethod
    def _generate_inflation_context(
        spending,
        inflation_data: Optional[Dict],
        income: float
    ) -> List[str]:
        """Generate inflation-adjusted insights"""
        if not inflation_data:
            return []
        
        insights = []
        
        food_spending = spending.essential.get("Food", 0)
        transport_spending = spending.essential.get("Transport", 0)
        
        food_inflation = inflation_data.get("food_inflation", 0)
        fuel_inflation = inflation_data.get("fuel_inflation", 0)
        general_inflation = inflation_data.get("general_inflation", 0)
        
        # Food context
        if food_spending > 0 and food_inflation > 5:
            food_pct = (food_spending / income) * 100
            insights.append(
                f"Food inflation is {food_inflation:.1f}%. Your food spending ({food_pct:.1f}%) "
                f"is justified by current market conditions."
            )
        
        # Transport context
        if transport_spending > 0 and fuel_inflation > 6:
            transport_pct = (transport_spending / income) * 100
            insights.append(
                f"Fuel prices increased by {fuel_inflation:.1f}%. Your transport costs ({transport_pct:.1f}%) "
                f"reflect this increase."
            )
        
        # General inflation
        if general_inflation > 6:
            insights.append(
                f"General inflation is {general_inflation:.1f}%. Consider increasing savings to maintain purchasing power."
            )
        
        return insights
