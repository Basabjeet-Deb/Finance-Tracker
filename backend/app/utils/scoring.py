"""
Financial Scoring System
Calculates financial health score (0-100) based on multiple factors
"""
from typing import Dict, List


def calculate_financial_score(
    percentages: Dict[str, float],
    violations: List[str],
    inflation: Dict,
    profile: Dict,
    money_leaks: List[Dict]
) -> int:
    """
    Calculate financial health score (0-100)
    
    Higher score = Better financial health
    
    Scoring factors:
    - Savings rate (30 points max)
    - Fixed obligations (20 points max)
    - Lifestyle spending (15 points max)
    - Emergency fund (15 points max)
    - Inflation resilience (10 points max)
    - Money leak management (10 points max)
    
    Args:
        percentages: Spending percentages by category
        violations: List of budget violations
        inflation: Inflation context
        profile: User financial profile
        money_leaks: Categories impacted by inflation
        
    Returns:
        int: Score from 0-100
    """
    score = 0
    
    # 1. Savings rate (30 points max)
    savings_rate = percentages.get("actual_savings", 0)
    if savings_rate >= 30:
        score += 30
    elif savings_rate >= 25:
        score += 25
    elif savings_rate >= 20:
        score += 20
    elif savings_rate >= 15:
        score += 15
    elif savings_rate >= 10:
        score += 10
    elif savings_rate >= 5:
        score += 5
    # else: 0 points
    
    # 2. Fixed obligations (20 points max)
    fixed_pct = percentages.get("fixed", 0)
    if fixed_pct <= 40:
        score += 20
    elif fixed_pct <= 45:
        score += 15
    elif fixed_pct <= 50:
        score += 10
    elif fixed_pct <= 55:
        score += 5
    # else: 0 points
    
    # 3. Lifestyle spending (15 points max)
    lifestyle_pct = percentages.get("lifestyle", 0)
    if lifestyle_pct <= 15:
        score += 15
    elif lifestyle_pct <= 20:
        score += 12
    elif lifestyle_pct <= 25:
        score += 8
    elif lifestyle_pct <= 30:
        score += 4
    # else: 0 points
    
    # 4. Emergency fund (15 points max)
    has_emergency_fund = profile.get("has_emergency_fund", False)
    if has_emergency_fund:
        score += 15
    elif savings_rate >= 20:
        score += 10  # Building towards emergency fund
    elif savings_rate >= 10:
        score += 5
    # else: 0 points
    
    # 5. Inflation resilience (10 points max)
    inflation_pressure = inflation.get("pressure", "medium")
    if inflation_pressure == "low":
        score += 10
    elif inflation_pressure == "medium":
        score += 6
    elif inflation_pressure == "high":
        score += 3
    # else: 0 points
    
    # 6. Money leak management (10 points max)
    num_leaks = len(money_leaks)
    if num_leaks == 0:
        score += 10
    elif num_leaks == 1:
        score += 7
    elif num_leaks == 2:
        score += 4
    elif num_leaks == 3:
        score += 2
    # else: 0 points
    
    # Penalties for violations
    violation_penalty = min(len(violations) * 5, 20)
    score -= violation_penalty
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return score


def get_score_interpretation(score: int) -> Dict[str, str]:
    """
    Get human-readable interpretation of financial score
    
    Args:
        score: Financial health score (0-100)
        
    Returns:
        Dict with interpretation details
    """
    if score >= 80:
        return {
            "level": "excellent",
            "message": "Your financial health is excellent! Keep up the great work.",
            "emoji": "🌟"
        }
    elif score >= 60:
        return {
            "level": "good",
            "message": "Your finances are in good shape with room for improvement.",
            "emoji": "✅"
        }
    elif score >= 40:
        return {
            "level": "fair",
            "message": "Your financial health needs attention. Focus on key improvements.",
            "emoji": "⚠️"
        }
    elif score >= 20:
        return {
            "level": "poor",
            "message": "Your finances need urgent attention. Take immediate action.",
            "emoji": "🚨"
        }
    else:
        return {
            "level": "critical",
            "message": "Critical financial situation. Seek professional advice immediately.",
            "emoji": "🆘"
        }


def calculate_category_scores(percentages: Dict[str, float], thresholds: Dict) -> Dict[str, Dict]:
    """
    Calculate individual scores for each spending category
    
    Args:
        percentages: Current spending percentages
        thresholds: Target thresholds
        
    Returns:
        Dict with scores for each category
    """
    scores = {}
    
    # Fixed obligations score
    fixed_pct = percentages.get("fixed", 0)
    fixed_target = thresholds.get("fixed", 50)
    if fixed_pct <= fixed_target:
        fixed_score = 100
    else:
        excess = fixed_pct - fixed_target
        fixed_score = max(0, 100 - (excess * 5))
    
    scores["fixed"] = {
        "score": round(fixed_score, 1),
        "status": "good" if fixed_score >= 70 else "needs_improvement"
    }
    
    # Essential spending score
    essential_pct = percentages.get("essential", 0)
    essential_target = thresholds.get("essential", 30)
    if essential_pct <= essential_target:
        essential_score = 100
    else:
        excess = essential_pct - essential_target
        essential_score = max(0, 100 - (excess * 4))
    
    scores["essential"] = {
        "score": round(essential_score, 1),
        "status": "good" if essential_score >= 70 else "needs_improvement"
    }
    
    # Lifestyle spending score
    lifestyle_pct = percentages.get("lifestyle", 0)
    lifestyle_target = thresholds.get("lifestyle", 20)
    if lifestyle_pct <= lifestyle_target:
        lifestyle_score = 100
    else:
        excess = lifestyle_pct - lifestyle_target
        lifestyle_score = max(0, 100 - (excess * 3))
    
    scores["lifestyle"] = {
        "score": round(lifestyle_score, 1),
        "status": "good" if lifestyle_score >= 70 else "needs_improvement"
    }
    
    # Savings score
    savings_pct = percentages.get("actual_savings", 0)
    savings_target = thresholds.get("savings", 20)
    if savings_pct >= savings_target:
        savings_score = 100
    else:
        deficit = savings_target - savings_pct
        savings_score = max(0, 100 - (deficit * 4))
    
    scores["savings"] = {
        "score": round(savings_score, 1),
        "status": "good" if savings_score >= 70 else "needs_improvement"
    }
    
    return scores
