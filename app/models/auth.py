"""
Authentication Pydantic Models
Request/Response schemas for authentication endpoints
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ============================================================================
# LOGIN MODELS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request body"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@qkrew.com",
                "password": "admin123"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "uuid",
                    "email": "admin@qkrew.com",
                    "name": "Admin User",
                    "role": "admin",
                    "hierarchy_level": "L1"
                }
            }
        }


# ============================================================================
# REFRESH TOKEN MODELS
# ============================================================================

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# ============================================================================
# USER RESPONSE MODEL
# ============================================================================

class UserResponse(BaseModel):
    """User data response (without sensitive info)"""
    id: str
    email: str
    name: str
    role: str
    hierarchy_level: str
    department: Optional[str] = None
    tech_team_id: Optional[str] = None
    status: str
    avatar_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "uuid",
                "email": "admin@qkrew.com",
                "name": "Admin User",
                "role": "admin",
                "hierarchy_level": "L1",
                "department": "Engineering",
                "tech_team_id": None,
                "status": "active",
                "avatar_url": None
            }
        }


# ============================================================================
# REGISTER MODEL (for future use)
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    name: str
    role: str
    hierarchy_level: str
    department: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@qkrew.com",
                "password": "password123",
                "name": "John Doe",
                "role": "employee",
                "hierarchy_level": "L8",
                "department": "Engineering"
            }
        }
