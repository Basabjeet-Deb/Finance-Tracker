"""
FastAPI Application Entry Point
Clean architecture with modular routes and Supabase PostgreSQL
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.database import engine, get_db, Base, test_connection, create_tables
from app.routes import user, expenses, analysis, unified_analysis
from app.models import CPIData, FuelData
from app.schemas import CPIDataResponse, FuelDataResponse
from app.services.cpi_service import (
    fetch_and_store_cpi_data,
    get_all_cpi_with_inflation,
    refresh_cpi_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Finance Tracker - India",
    version="3.0.0",
    description="AI-powered personal finance tracker with Supabase PostgreSQL and rule-based optimization"
)

# CORS middleware - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(expenses.router)
app.include_router(analysis.router)
app.include_router(unified_analysis.router)  # NEW: Unified analysis endpoint

# Global scheduler instance
scheduler = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and external data on startup"""
    global scheduler
    
    logger.info("Starting application...")
    
    # Test database connection
    if not test_connection():
        logger.error("Failed to connect to database. Please check DATABASE_URL.")
        raise Exception("Database connection failed")
    
    logger.info("Database connection successful")
    
    # Create tables if they don't exist
    try:
        create_tables()
        logger.info("Database tables verified/created")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    
    # Initialize external data
    db = next(get_db())
    try:
        # Fetch initial CPI data
        logger.info("Fetching initial CPI data...")
        fetch_and_store_cpi_data(db)
        
        # Fetch fuel data if available
        try:
            from external_data import fetch_and_store_fuel_data
            fetch_and_store_fuel_data(db)
        except Exception as e:
            logger.warning(f"Could not fetch fuel data: {e}")
        
        # Start background scheduler for monthly updates
        try:
            from scheduler import start_scheduler
            scheduler = start_scheduler()
            logger.info("Background scheduler started")
        except Exception as e:
            logger.warning(f"Could not start scheduler: {e}")
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
    finally:
        db.close()
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on shutdown"""
    global scheduler
    logger.info("Shutting down application...")
    
    if scheduler:
        try:
            from scheduler import stop_scheduler
            stop_scheduler(scheduler)
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.warning(f"Error stopping scheduler: {e}")
    
    logger.info("Application shutdown complete")


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Personal Finance Tracker API - India",
        "version": "3.0.0",
        "status": "active",
        "database": "Supabase PostgreSQL"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    db_status = "connected" if test_connection() else "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "database_type": "PostgreSQL (Supabase)",
        "scheduler": "running" if scheduler else "stopped",
        "version": "3.0.0"
    }


@app.get("/health/db")
def health_check_database():
    """
    Database connection health check
    Tests actual database connectivity
    """
    try:
        from sqlalchemy import text
        db = next(get_db())
        # Execute a simple query
        result = db.execute(text("SELECT 1 as health_check"))
        row = result.fetchone()
        db.close()
        
        if row and row[0] == 1:
            return {
                "status": "success",
                "message": "Database connection is healthy",
                "database": "PostgreSQL (Supabase)",
                "connection": "active"
            }
        else:
            raise Exception("Unexpected query result")
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "Database connection failed",
                "error": str(e)
            }
        )


@app.get("/test-analysis")
def test_analysis(db: Session = Depends(get_db)):
    """Test endpoint to debug financial analysis"""
    try:
        from app.services.inflation_engine import get_inflation_pressure
        inflation = get_inflation_pressure(db)
        return {"status": "success", "inflation": inflation}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}


# CPI and External Data Endpoints
@app.get("/inflation/pressure")
def get_inflation_pressure_endpoint(db: Session = Depends(get_db)):
    """
    Get current inflation pressure classification
    
    Returns decision-ready inflation intelligence:
    - pressure: low/medium/high
    - value: YoY inflation %
    - confidence: high/medium/low (based on data freshness)
    """
    from app.services.cpi_service import get_inflation_pressure
    return get_inflation_pressure(db)


@app.get("/inflation/thresholds")
def get_inflation_adjusted_thresholds(db: Session = Depends(get_db)):
    """
    Get inflation-adjusted budget thresholds
    
    Uses inflation intelligence to adjust budget recommendations
    """
    from app.services.cpi_service import get_inflation_pressure
    from app.services.inflation_engine import adjust_budget_thresholds
    
    inflation = get_inflation_pressure(db)
    thresholds = adjust_budget_thresholds(inflation)
    return {
        "inflation": inflation,
        "adjusted_thresholds": thresholds
    }


@app.get("/cpi")
def get_cpi_with_inflation(
    limit: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get recent CPI data with inflation metrics
    
    NOTE: This endpoint returns historical data for analysis.
    For decision-making, use /inflation/pressure instead.
    """
    from app.services.cpi_service import get_recent_cpi_with_inflation
    return get_recent_cpi_with_inflation(db, months=limit)


@app.post("/cpi/refresh")
def refresh_cpi_data_endpoint(db: Session = Depends(get_db)):
    """Manually trigger CPI data refresh from data.gov.in API"""
    result = refresh_cpi_data(db)
    return result


@app.get("/external/cpi", response_model=List[CPIDataResponse])
def get_cpi_data(
    limit: int = 12,
    db: Session = Depends(get_db)
):
    """Get CPI data (basic format without inflation metrics)"""
    cpi_data = db.query(CPIData).order_by(CPIData.month.desc()).limit(limit).all()
    return cpi_data


@app.get("/external/fuel", response_model=List[FuelDataResponse])
def get_fuel_data(db: Session = Depends(get_db)):
    """Get fuel price data"""
    fuel_data = db.query(FuelData).order_by(FuelData.date.desc()).limit(12).all()
    return fuel_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
