"""
Optimization Engine - Pure allocation optimization

FOCUSED RESPONSIBILITIES:
- Compute recommended spending allocation
- Calculate reallocation amounts (₹ values)
- Calculate savings potential

DOES NOT:
- Calculate risk scores (use centralized scoring)
- Generate recommendations (use financial_engine)
- Generate insights (use financial_engine)
- Handle inflation parsing (use inflation_engine)
"""
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """
    Result of optimization
    
    SIMPLIFIED: Only contains allocation data, no risk or recommendations
    """
    recommended_allocation: Dict[str, float]
    reallocation_needed: Dict[str, float]
    savings_potential: float


class OptimizationEngine:
    """
    Pure constraint optimization for spending reallocation
    
    Focuses ONLY on computing optimal allocation percentages
    """
    
    @staticmethod
    def optimize_allocation(
        current_allocation: Dict[str, float],
        constraints,
        inflation: Optional[Dict] = None
    ) -> OptimizationResult:
        """
        Optimize spending allocation to maximize savings and stability
        
        CRITICAL FIX: Takes current_allocation directly (savings already computed)
        
        Args:
            current_allocation: Current spending percentages
                {
                    "fixed": %,
                    "essential": %,
                    "lifestyle": %,
                    "savings": % (computed as leftover)
                }
            constraints: Financial constraints from rule_engine
            inflation: Optional inflation data from cpi_service
        
        Returns:
            OptimizationResult with recommended allocation and reallocation plan
        """
        # Step 1: Compute recommended allocation
        recommended = OptimizationEngine._compute_recommended_allocation(
            current_allocation,
            constraints,
            inflation
        )
        
        # Step 2: Calculate reallocation amounts (percentages)
        reallocation = OptimizationEngine._calculate_reallocation(
            current_allocation,
            recommended
        )
        
        # Step 3: Calculate savings potential (percentage points)
        savings_potential = recommended["savings"] - current_allocation.get("savings", 0)
        
        return OptimizationResult(
            recommended_allocation=recommended,
            reallocation_needed=reallocation,
            savings_potential=round(savings_potential, 1)
        )
    
    @staticmethod
    def _compute_recommended_allocation(
        current: Dict[str, float],
        constraints,
        inflation: Optional[Dict]
    ) -> Dict[str, float]:
        """
        Compute optimal allocation percentages
        
        CRITICAL FIX: Savings is computed as leftover, not from input
        """
        recommended = {}
        
        # Fixed obligations - cannot change
        recommended["fixed"] = current["fixed"]
        
        # Essentials - adjust for inflation pressure
        inflation_adjustment = 0
        if inflation:
            pressure = inflation.get("pressure", "medium")
            
            # Simple inflation adjustment based on pressure
            if pressure == "high":
                inflation_adjustment = 3.0
            elif pressure == "medium":
                inflation_adjustment = 1.0
        
        # Essentials target
        essential_target = min(
            constraints.essential_max,
            max(
                constraints.food_min + constraints.transport_min + constraints.healthcare_min,
                current["essential"]
            )
        ) + inflation_adjustment
        
        recommended["essential"] = round(essential_target, 1)
        
        # Calculate remaining after fixed and essential
        remaining = 100 - recommended["fixed"] - recommended["essential"]
        
        # Prioritize savings (40% of remaining, but respect constraints)
        savings_target = max(
            constraints.savings_min,
            min(30, remaining * 0.4)
        )
        recommended["savings"] = round(savings_target, 1)
        
        # Lifestyle gets what's left
        lifestyle_target = remaining - recommended["savings"]
        lifestyle_target = max(0, min(lifestyle_target, constraints.lifestyle_max))
        recommended["lifestyle"] = round(lifestyle_target, 1)
        
        # Ensure total = 100 (handle rounding)
        total = (
            recommended["fixed"] + 
            recommended["essential"] + 
            recommended["lifestyle"] + 
            recommended["savings"]
        )
        
        if total > 100:
            # Reduce lifestyle first
            excess = total - 100
            if recommended["lifestyle"] >= excess:
                recommended["lifestyle"] = round(recommended["lifestyle"] - excess, 1)
            else:
                # Reduce savings if lifestyle can't absorb it
                recommended["lifestyle"] = 0
                excess -= recommended["lifestyle"]
                recommended["savings"] = round(max(10, recommended["savings"] - excess), 1)
        
        return recommended
    
    @staticmethod
    def _calculate_reallocation(
        current: Dict[str, float],
        recommended: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate reallocation needed (percentage points)
        
        Positive = increase, Negative = decrease
        Only includes significant changes (>1%)
        """
        reallocation = {}
        
        for category in ["fixed", "essential", "lifestyle", "savings"]:
            diff_pct = recommended[category] - current.get(category, 0)
            
            # Only include if significant (>1% change)
            if abs(diff_pct) > 1.0:
                reallocation[category] = round(diff_pct, 1)
        
        return reallocation
