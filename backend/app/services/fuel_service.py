"""
DEPRECATED: Fuel Service

This service has been integrated into inflation_engine.py for better stability and integration.

Use instead:
- inflation_engine.get_transport_inflation_factor()
- inflation_engine.calculate_transport_pressure()

This file is kept for backward compatibility only.
"""
import logging

logger = logging.getLogger(__name__)


class FuelService:
    """
    DEPRECATED: Use inflation_engine functions instead
    
    This class is kept for backward compatibility but should not be used.
    All fuel/transport logic has been integrated into inflation_engine.py
    """
    
    @staticmethod
    def get_petrol_prices() -> dict:
        """
        DEPRECATED: Returns static baseline prices
        
        Real-time scraping was unreliable. Use inflation_engine.get_transport_inflation_factor()
        to get CPI-derived transport inflation estimates instead.
        """
        logger.warning(
            "FuelService.get_petrol_prices() is deprecated. "
            "Use inflation_engine.get_transport_inflation_factor() instead."
        )
        
        # Return static baseline prices (no scraping)
        return {
            "Delhi": 96.72,
            "Mumbai": 106.31,
            "Bangalore": 101.94,
            "Chennai": 102.63
        }
    
    @staticmethod
    def calculate_fuel_impact(transport_spend: float) -> dict:
        """
        DEPRECATED: Use inflation_engine.calculate_transport_pressure() instead
        
        The new function provides structured output integrated with the financial decision system.
        """
        logger.warning(
            "FuelService.calculate_fuel_impact() is deprecated. "
            "Use inflation_engine.calculate_transport_pressure() instead."
        )
        
        if transport_spend <= 0:
            return {
                "current_avg_petrol_price": None,
                "metro_prices": {},
                "insight": "No transport spending detected"
            }
        
        # Return minimal fallback data
        prices = FuelService.get_petrol_prices()
        avg_price = sum(prices.values()) / len(prices)
        
        return {
            "current_avg_petrol_price": round(avg_price, 2),
            "metro_prices": prices,
            "insight": (
                f"Average petrol in metros is ₹{round(avg_price, 2)}. "
                f"Use inflation_engine.calculate_transport_pressure() for integrated analysis."
            )
        }

