"""
Service to fetch real-time Petrol prices in metro cities.
Uses free scraping from public fuel tracking websites.
"""
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class FuelService:
    @staticmethod
    def get_petrol_prices() -> dict:
        """
        Scrape latest petrol prices for major metros.
        Provides a realistic fallback if scraping blocked.
        """
        # Fallback realistic prices in INR
        prices = {
            "Delhi": 96.72,
            "Mumbai": 106.31,
            "Bangalore": 101.94,
            "Chennai": 102.63
        }
        
        try:
            url = "https://www.goodreturns.in/petrol-price.html"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # goodreturns usually has tables mapping city -> price
                # We attempt to find matching rows for our metros
                metros = ["New Delhi", "Mumbai", "Bangalore", "Chennai"]
                
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            city_name = cols[0].get_text().strip()
                            price_text = cols[1].get_text().strip()
                            
                            # Clean price (e.g., "₹ 96.72" -> 96.72)
                            try:
                                val = float(price_text.replace('₹', '').replace(',', '').strip())
                                if "Delhi" in city_name:
                                    prices["Delhi"] = val
                                elif "Mumbai" in city_name:
                                    prices["Mumbai"] = val
                                elif "Bangalore" in city_name:
                                    prices["Bangalore"] = val
                                elif "Chennai" in city_name:
                                    prices["Chennai"] = val
                            except ValueError:
                                continue
                                
        except Exception as e:
            logger.warning(f"Could not fetch live fuel prices: {e}")
            
        return prices

    @staticmethod
    def calculate_fuel_impact(transport_spend: float) -> dict:
        """Analyze if fuel inflation is hurting the user's budget"""
        if transport_spend <= 0:
            return {
                "current_avg_petrol_price": None,
                "metro_prices": {},
                "insight": "No transport spending detected"
            }
            
        prices = FuelService.get_petrol_prices()
        avg_price = sum(prices.values()) / len(prices)
        
        # If transport spend is high, create an insight
        return {
            "current_avg_petrol_price": round(avg_price, 2),
            "metro_prices": prices,
            "insight": f"Average petrol in metros is ₹{round(avg_price, 2)}. If you drive a car, your ₹{transport_spend} transport spend handles about {round(transport_spend/avg_price, 1)} liters of fuel. Consider carpooling or public transit to optimize this."
        }
