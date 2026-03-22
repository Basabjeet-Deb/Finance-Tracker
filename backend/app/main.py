"""
FastAPI Application Entry Point
Clean architecture with modular routes
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.db.database import engine, get_db, Base
from app.routes import user, expenses, analysis
from app.models import CPIData, FuelData
from app.schemas import CPIDataResponse, FuelDataResponse
from app.services.cpi_service import (
    fetch_and_store_cpi_data,
    get_all_cpi_with_inflation,
    refresh_cpi_data
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Finance Tracker - India",
    version="2.0.0",
    description="AI-powered personal finance tracker with rule-based optimization"
)

# CORS middleware - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(expenses.router)
app.include_router(analysis.router)

# Global scheduler instance
scheduler = None


@app.on_event("startup")
async def startup_event():
    """Initialize external data and start background scheduler"""
    global scheduler
    db = next(get_db())
    try:
        # Fetch initial CPI and fuel data
        fetch_and_store_cpi_data(db)
        
        # Fetch fuel data if available
        try:
            from external_data import fetch_and_store_fuel_data
            fetch_and_store_fuel_data(db)
        except:
            pass
        
        # Start background scheduler for monthly updates
        try:
            from scheduler import start_scheduler
            scheduler = start_scheduler()
        except:
            pass
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler"""
    global scheduler
    if scheduler:
        try:
            from scheduler import stop_scheduler
            stop_scheduler(scheduler)
        except:
            pass


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Personal Finance Tracker API - India",
        "version": "2.0.0",
        "status": "active"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running" if scheduler else "stopped"
    }


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
    """Get current inflation pressure score and level"""
    from app.services.inflation_engine import get_inflation_pressure
    return get_inflation_pressure(db)


@app.get("/inflation/thresholds")
def get_inflation_adjusted_thresholds(db: Session = Depends(get_db)):
    """Get inflation-adjusted budget thresholds"""
    from app.services.inflation_engine import (
        get_inflation_pressure,
        adjust_budget_thresholds
    )
    inflation = get_inflation_pressure(db)
    thresholds = adjust_budget_thresholds(inflation)
    return {
        "inflation": inflation,
        "adjusted_thresholds": thresholds
    }


@app.get("/cpi")
def get_cpi_with_inflation(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get CPI data with computed inflation metrics"""
    return get_all_cpi_with_inflation(db, limit)


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
