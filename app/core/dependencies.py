"""
QKREW Backend - FastAPI Dependencies
Provides reusable dependencies for routes (authentication, database, etc.)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_token
from app.database import get_db, get_service_db
from supabase import Client


# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: Bearer token from Authorization header
        db: Supabase client
    
    Returns:
        User dictionary with id, email, role, hierarchy_level
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        token = credentials.credentials
        payload = decode_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Fetch user from database
        response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise credentials_exception
        
        user = response.data[0]
        
        # Return user data
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "hierarchy_level": user["hierarchy_level"],
            "department": user.get("department"),
            "tech_team_id": user.get("tech_team_id"),
            "status": user.get("status"),
        }
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure user is active (not exited)
    
    Args:
        current_user: Current user from get_current_user
    
    Returns:
        Active user dictionary
    
    Raises:
        HTTPException: If user is not active
    """
    if current_user.get("status") == "exited":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return current_user


# Optional user dependency (doesn't raise error if not authenticated)
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict | None:
    """
    Optional authentication - returns None if not authenticated
    Useful for endpoints that work differently for authenticated vs anonymous users
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
