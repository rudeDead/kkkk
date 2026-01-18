"""
QKREW Backend - Supabase Database Client
Initializes and provides Supabase client for database operations
"""

from supabase import create_client, Client
from app.config import settings


class Database:
    """Supabase database client wrapper"""
    
    def __init__(self):
        self.client: Client = None
        self.service_client: Client = None
    
    def connect(self):
        """Initialize Supabase clients"""
        # Regular client (with anon key)
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Service client (with service role key - for admin operations)
        self.service_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        print(f"[OK] Connected to Supabase: {settings.SUPABASE_URL}")
    
    def get_client(self) -> Client:
        """Get regular Supabase client"""
        if not self.client:
            self.connect()
        return self.client
    
    def get_service_client(self) -> Client:
        """Get service role client (admin access)"""
        if not self.service_client:
            self.connect()
        return self.service_client


# Global database instance
db = Database()


def get_db() -> Client:
    """Dependency to get database client"""
    return db.get_client()


def get_service_db() -> Client:
    """Dependency to get service database client (admin operations)"""
    return db.get_service_client()
