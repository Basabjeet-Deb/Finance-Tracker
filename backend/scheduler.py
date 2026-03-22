"""
Background scheduler for periodic tasks
Handles monthly CPI data refresh from data.gov.in
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from external_data import refresh_cpi_data
import logging

logger = logging.getLogger(__name__)

def scheduled_cpi_refresh():
    """
    Scheduled task to refresh CPI data
    Runs monthly on the 5th day at 2 AM
    """
    logger.info("Running scheduled CPI data refresh")
    db = SessionLocal()
    try:
        result = refresh_cpi_data(db)
        logger.info(f"Scheduled CPI refresh result: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled CPI refresh: {e}")
    finally:
        db.close()

def start_scheduler():
    """
    Start the background scheduler
    """
    scheduler = BackgroundScheduler()
    
    # Schedule CPI refresh monthly on 5th day at 2 AM
    scheduler.add_job(
        scheduled_cpi_refresh,
        trigger=CronTrigger(day=5, hour=2, minute=0),
        id='cpi_refresh',
        name='Monthly CPI data refresh',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started - CPI refresh scheduled monthly")
    
    return scheduler

def stop_scheduler(scheduler):
    """
    Stop the background scheduler
    """
    if scheduler:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
