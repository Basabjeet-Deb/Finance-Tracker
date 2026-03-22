"""
Supabase client for authentication
Data operations use SQLAlchemy, auth uses Supabase Auth
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client (optional - for auth if needed)
supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize Supabase client: {e}")
        logger.info("Continuing with database-only mode")
else:
    logger.info("Supabase URL/KEY not configured - using database-only mode")


def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    
    Returns:
        Client: Supabase client for auth operations
    """
    if not supabase_client:
        raise ValueError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY.")
    return supabase_client
