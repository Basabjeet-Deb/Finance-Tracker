"""
CPI Data Service
Handles fetching, processing, and serving India CPI data
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
    """Fetch CPI data from API and store in database"""
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


def get_all_cpi_with_inflation(db: Session, limit: int = 100) -> List[Dict]:
    """Get CPI data with computed inflation metrics"""
    cpi_records = db.query(CPIData).order_by(CPIData.month).all()
    
    if not cpi_records:
        return []
    
    result = []
    
    for i, record in enumerate(cpi_records):
        data = {
            "date": record.month,
            "cpi": record.value,
            "month_to_month_inflation": None,
            "year_over_year_inflation": None
        }
        
        # Month-to-month
        if i > 0:
            prev_record = cpi_records[i - 1]
            if prev_record.value > 0:
                mtm = ((record.value - prev_record.value) / prev_record.value) * 100
                data["month_to_month_inflation"] = round(mtm, 2)
        
        # Year-over-year
        current_year, current_month = record.month.split("-")
        prev_year = str(int(current_year) - 1)
        prev_year_month = f"{prev_year}-{current_month}"
        
        prev_year_record = db.query(CPIData).filter(CPIData.month == prev_year_month).first()
        if prev_year_record and prev_year_record.value > 0:
            yoy = ((record.value - prev_year_record.value) / prev_year_record.value) * 100
            data["year_over_year_inflation"] = round(yoy, 2)
        
        result.append(data)
    
    if limit and limit < len(result):
        return result[-limit:]
    
    return result


def get_latest_cpi(db: Session):
    """Get the most recent CPI data"""
    return db.query(CPIData).order_by(CPIData.month.desc()).first()



def refresh_cpi_data(db: Session) -> Dict:
    """Manually refresh CPI data from API"""
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
