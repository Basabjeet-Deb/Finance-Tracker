"""
CPI Inflation Intelligence Service
Provides decision-ready inflation signals for financial decision engine

This is NOT a raw data service - it provides actionable inflation intelligence:
- Inflation pressure classification (low/medium/high)
- Data freshness confidence
- Optimized queries (last 24 months only)
- Fallback handling for stale/missing data
"""
import requests
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models import CPIData

logger = logging.getLogger(__name__)

# API Configuration
DATA_GOV_API_URL = "https://api.data.gov.in/resource/1ca957b4-0cf0-4d7e-a6a7-627d9f13b170"
API_KEY = "579b464db66ec23bdd0000019068c43cf6e74bca518f2010329bad4d"

# Month mapping
MONTH_MAP = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}


# ============================================================================
# CORE INFLATION INTELLIGENCE FUNCTIONS
# ============================================================================

def get_inflation_pressure(db: Session) -> Dict:
    """
    Get inflation pressure classification for decision-making
    
    This is the PRIMARY function that financial_engine should call.
    Returns actionable inflation intelligence, not raw data.
    
    Returns:
        {
            "pressure": "low | medium | high",
            "value": float (YoY inflation %),
            "confidence": "high | medium | low" (based on data freshness)
        }
    """
    try:
        # Get latest CPI data (optimized query - only last 2 records needed)
        latest_records = db.query(CPIData).order_by(
            CPIData.month.desc()
        ).limit(2).all()
        
        if not latest_records or len(latest_records) < 2:
            logger.warning("Insufficient CPI data for inflation calculation")
            return _get_fallback_inflation()
        
        latest = latest_records[0]
        
        # Calculate year-over-year inflation
        yoy_inflation = _calculate_yoy_inflation(db, latest)
        
        if yoy_inflation is None:
            logger.warning("Could not calculate YoY inflation")
            return _get_fallback_inflation()
        
        # Classify inflation pressure
        if yoy_inflation < 3.0:
            pressure = "low"
        elif yoy_inflation < 6.0:
            pressure = "medium"
        else:
            pressure = "high"
        
        # Determine data freshness confidence
        confidence = get_data_freshness(latest.month)
        
        return {
            "pressure": pressure,
            "value": round(yoy_inflation, 2),
            "confidence": confidence
        }
    
    except Exception as e:
        logger.error(f"Error calculating inflation pressure: {e}")
        return _get_fallback_inflation()


def get_data_freshness(latest_date: str) -> str:
    """
    Determine data freshness confidence level
    
    Args:
        latest_date: Date string in YYYY-MM format
        
    Returns:
        "high" - <= 2 months old
        "medium" - <= 6 months old
        "low" - older than 6 months
    """
    try:
        latest_dt = datetime.strptime(latest_date, "%Y-%m")
        current_dt = datetime.now()
        
        # Calculate months difference
        months_diff = (current_dt.year - latest_dt.year) * 12 + (current_dt.month - latest_dt.month)
        
        if months_diff <= 2:
            return "high"
        elif months_diff <= 6:
            return "medium"
        else:
            return "low"
    
    except Exception as e:
        logger.error(f"Error calculating data freshness: {e}")
        return "low"


def _calculate_yoy_inflation(db: Session, latest_record: CPIData) -> Optional[float]:
    """
    Calculate year-over-year inflation for a given CPI record
    
    Args:
        db: Database session
        latest_record: Latest CPI record
        
    Returns:
        YoY inflation percentage or None if cannot calculate
    """
    try:
        current_year, current_month = latest_record.month.split("-")
        prev_year = str(int(current_year) - 1)
        prev_year_month = f"{prev_year}-{current_month}"
        
        # Query for same month last year
        prev_year_record = db.query(CPIData).filter(
            CPIData.month == prev_year_month
        ).first()
        
        if not prev_year_record or prev_year_record.value <= 0:
            return None
        
        # Calculate YoY inflation
        yoy_inflation = ((latest_record.value - prev_year_record.value) / prev_year_record.value) * 100
        
        return yoy_inflation
    
    except Exception as e:
        logger.error(f"Error calculating YoY inflation: {e}")
        return None


def _get_fallback_inflation() -> Dict:
    """
    Return fallback inflation data when real data is unavailable
    
    Uses conservative medium pressure estimate
    """
    return {
        "pressure": "medium",
        "value": 5.0,
        "confidence": "low"
    }


# ============================================================================
# OPTIMIZED DATA RETRIEVAL (Internal Use Only)
# ============================================================================

def get_recent_cpi_with_inflation(db: Session, months: int = 24) -> List[Dict]:
    """
    Get recent CPI data with inflation metrics (OPTIMIZED)
    
    IMPORTANT: Only fetches last N months, not entire dataset
    Used internally for analysis, not exposed to API
    
    Args:
        db: Database session
        months: Number of recent months to fetch (default: 24)
        
    Returns:
        List of CPI records with inflation metrics
    """
    try:
        # OPTIMIZED: Fetch only recent records in descending order
        cpi_records = db.query(CPIData).order_by(
            CPIData.month.desc()
        ).limit(months).all()
        
        if not cpi_records:
            return []
        
        # Reverse to chronological order for processing
        cpi_records = list(reversed(cpi_records))
        
        result = []
        
        for i, record in enumerate(cpi_records):
            data = {
                "date": record.month,
                "cpi": record.value,
                "month_to_month_inflation": None,
                "year_over_year_inflation": None
            }
            
            # Month-to-month (only if previous record exists in our dataset)
            if i > 0:
                prev_record = cpi_records[i - 1]
                if prev_record.value > 0:
                    mtm = ((record.value - prev_record.value) / prev_record.value) * 100
                    data["month_to_month_inflation"] = round(mtm, 2)
            
            # Year-over-year
            yoy = _calculate_yoy_inflation(db, record)
            if yoy is not None:
                data["year_over_year_inflation"] = round(yoy, 2)
            
            result.append(data)
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching recent CPI data: {e}")
        return []


# ============================================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================================

def fetch_cpi_from_api(limit: int = 1000, offset: int = 0) -> Optional[Dict]:
    """Fetch CPI data from data.gov.in API"""
    try:
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": limit,
            "offset": offset
        }
        
        response = requests.get(DATA_GOV_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        logger.error(f"Error fetching CPI data: {e}")
        return None


def filter_and_transform_records(records: List[Dict]) -> List[Dict]:
    """Filter for Rural+Urban and transform to standard format"""
    transformed = []
    
    for record in records:
        try:
            if record.get("sector") != "Rural+Urban":
                continue
            
            year = record.get("year")
            month_name = record.get("month")
            general_index = record.get("general_index")
            
            if not all([year, month_name, general_index]):
                continue
            
            month_num = MONTH_MAP.get(month_name)
            if not month_num:
                continue
            
            date_str = f"{year}-{month_num}"
            cpi_value = float(general_index)
            
            transformed.append({"date": date_str, "cpi": cpi_value})
            
        except Exception as e:
            logger.error(f"Error processing record: {e}")
            continue
    
    return transformed


def fetch_and_store_cpi_data(db: Session, force_refresh: bool = False) -> bool:
    """
    Fetch CPI data from API and store in database
    
    This is a data management function, not used for decision-making
    """
    try:
        if not force_refresh:
            existing_count = db.query(func.count(CPIData.id)).scalar()
            if existing_count > 0:
                logger.info(f"CPI data exists ({existing_count} records)")
                return True
        
        # Fetch from API
        all_records = []
        offset = 0
        limit = 1000
        
        while True:
            response = fetch_cpi_from_api(limit, offset)
            if not response:
                break
            
            records = response.get("records", [])
            if not records:
                break
            
            transformed = filter_and_transform_records(records)
            all_records.extend(transformed)
            
            if len(records) < limit:
                break
            
            offset += limit
        
        if not all_records:
            logger.warning("No CPI records fetched")
            return False
        
        # Sort and store
        all_records.sort(key=lambda x: x["date"])
        
        for record in all_records:
            existing = db.query(CPIData).filter(CPIData.month == record["date"]).first()
            if existing:
                existing.value = record["cpi"]
            else:
                cpi_entry = CPIData(month=record["date"], value=record["cpi"])
                db.add(cpi_entry)
        
        db.commit()
        logger.info(f"CPI data stored: {len(all_records)} records")
        return True
        
    except Exception as e:
        logger.error(f"Error storing CPI data: {e}")
        db.rollback()
        return False


def get_latest_cpi(db: Session) -> Optional[CPIData]:
    """
    Get the most recent CPI record
    
    Used for data management, not for decision-making
    """
    return db.query(CPIData).order_by(CPIData.month.desc()).first()


def refresh_cpi_data(db: Session) -> Dict:
    """
    Manually refresh CPI data from API
    
    Admin/maintenance function
    """
    try:
        success = fetch_and_store_cpi_data(db, force_refresh=True)
        
        if success:
            count = db.query(func.count(CPIData.id)).scalar()
            return {
                "status": "success",
                "message": f"CPI data refreshed successfully",
                "total_records": count
            }
        else:
            return {
                "status": "error",
                "message": "Failed to refresh CPI data"
            }
            
    except Exception as e:
        logger.error(f"Error refreshing CPI data: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================================
# DEPRECATED FUNCTIONS (Kept for backward compatibility)
# ============================================================================

def get_all_cpi_with_inflation(db: Session, limit: int = 24) -> List[Dict]:
    """
    DEPRECATED: Use get_inflation_pressure() instead
    
    This function is kept for backward compatibility but should not be used
    by financial_engine. Use get_inflation_pressure() for decision-making.
    """
    logger.warning(
        "get_all_cpi_with_inflation() is deprecated. "
        "Use get_inflation_pressure() for decision-making."
    )
    return get_recent_cpi_with_inflation(db, months=limit)
