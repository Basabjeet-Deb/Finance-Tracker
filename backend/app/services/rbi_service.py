"""
DEPRECATED: RBI Service

This service has been deprecated and integrated into inflation_engine.py

Use inflation_engine.calculate_emi_pressure() instead for EMI analysis

Reason for deprecation:
- Web scraping is unreliable and fragile
- RBI website structure changes frequently
- EMI logic is now part of centralized inflation intelligence
- Static baseline repo rate is sufficient for decision-making
"""
import logging

logger = logging.getLogger(__name__)


class RBIService:
    """
    DEPRECATED: Use inflation_engine.calculate_emi_pressure() instead
    """
    
    @staticmethod
    def get_current_repo_rate() -> float:
        """
        DEPRECATED: Returns static baseline repo rate
        
        Use inflation_engine.calculate_emi_pressure() for EMI analysis
        """
        logger.warning(
            "RBIService.get_current_repo_rate() is DEPRECATED. "
            "Use inflation_engine.calculate_emi_pressure() instead."
        )
        return 6.50  # Static baseline
    
    @staticmethod
    def calculate_emi_impact(current_emi: float) -> dict:
        """
        DEPRECATED: Returns static EMI impact
        
        Use inflation_engine.calculate_emi_pressure(emi_amount, income) instead
        """
        logger.warning(
            "RBIService.calculate_emi_impact() is DEPRECATED. "
            "Use inflation_engine.calculate_emi_pressure() instead."
        )
        
        if current_emi <= 0:
            return {
                "current_repo_rate": 6.50,
                "projected_emi_increase": 0,
                "alert_message": "No EMI detected"
            }
        
        projected_increase = current_emi * 0.025
        
        return {
            "current_repo_rate": 6.50,
            "projected_emi_increase": round(projected_increase, 2),
            "alert_message": f"The RBI Repo Rate is currently 6.50%. If the RBI raises rates by 0.25 bps next quarter, your ₹{current_emi} EMI could increase by approx ₹{round(projected_increase, 0)}."
        }
