"""
Authentication API Endpoints
Handles login, logout, token refresh, and current user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.models.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.rbac import get_user_permissions
from app.database import get_db


router = APIRouter()


# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Client = Depends(get_db)
):
    """
    User login endpoint
    
    - Validates email and password
    - Returns JWT access token and refresh token
    - Returns user data (without password)
    
    **Admin credentials (default):**
    - Email: admin@qkrew.com
    - Password: admin123
    """
    try:
        # Fetch user by email
        response = db.table("users").select("*").eq("email", credentials.email).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = response.data[0]
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if user.get("status") == "exited":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # ========================================================================
        # 🔐 VERBOSE LOGIN LOGGING
        # ========================================================================
        print("\n" + "=" * 80)
        print("🔐 USER LOGIN SUCCESSFUL")
        print("=" * 80)
        print(f"📧 Email:          {user['email']}")
        print(f"👤 Name:           {user['name']}")
        print(f"🎭 Role:           {user['role'].upper()}")
        print(f"📊 Hierarchy:      {user['hierarchy_level']}")
        print(f"🏢 Department:     {user.get('department', 'N/A')}")
        print(f"🆔 User ID:        {user['id']}")
        print(f"✅ Status:         {user.get('status', 'active')}")
        print("=" * 80)
        
        # Determine role description
        role_descriptions = {
            "admin": "🔴 SUPREME ADMIN - FULL CONTROL OVER EVERYTHING",
            "hr": "🟢 HR - Employee Management & Leave Governance",
            "project_manager": "🟧 PROJECT MANAGER - Project Delivery & Management",
            "technical_lead": "🟦 TECHNICAL LEAD - Team Execution & Quality",
            "employee": "🟢 EMPLOYEE - Personal Productivity & Tasks"
        }
        
        role_desc = role_descriptions.get(user['role'], "Unknown Role")
        print(f"🎯 Access Level:   {role_desc}")
        print("=" * 80 + "\n")
        
        # Create JWT tokens
        token_data = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "hierarchy_level": user["hierarchy_level"]
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Prepare user response (without password)
        user_response = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "hierarchy_level": user["hierarchy_level"],
            "department": user.get("department"),
            "tech_team_id": user.get("tech_team_id"),
            "status": user.get("status"),
            "avatar_url": user.get("avatar_url")
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


# ============================================================================
# REFRESH TOKEN ENDPOINT
# ============================================================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Client = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Returns new access token and refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(request.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Fetch user
        response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user = response.data[0]
        
        # Create new tokens
        token_data = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "hierarchy_level": user["hierarchy_level"]
        }
        
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Prepare user response
        user_response = {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "hierarchy_level": user["hierarchy_level"],
            "department": user.get("department"),
            "tech_team_id": user.get("tech_team_id"),
            "status": user.get("status"),
            "avatar_url": user.get("avatar_url")
        }
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


# ============================================================================
# GET CURRENT USER ENDPOINT
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get current authenticated user
    
    - Requires valid JWT token
    - Returns user data
    """
    return current_user


# ============================================================================
# LOGOUT ENDPOINT (Optional - client-side token removal)
# ============================================================================

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user)
):
    """
    Logout endpoint
    
    - In JWT-based auth, logout is handled client-side by removing the token
    - This endpoint is optional and just confirms logout
    """
    return {
        "message": "Logged out successfully",
        "user_id": current_user["id"]
    }


# ============================================================================
# GET USER PERMISSIONS ENDPOINT
# ============================================================================

@router.get("/permissions")
async def get_permissions(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get user's role-based permissions
    
    - Returns all permissions for the current user
    - Used by frontend to show/hide features based on role
    - ADMIN gets all permissions
    """
    permissions = get_user_permissions(current_user)
    
    # ========================================================================
    # 🔑 VERBOSE PERMISSIONS LOGGING
    # ========================================================================
    print("\n" + "=" * 80)
    print("🔑 PERMISSIONS REQUEST")
    print("=" * 80)
    print(f"👤 User:           {current_user.get('name', 'Unknown')}")
    print(f"📧 Email:          {current_user.get('email', 'Unknown')}")
    print(f"🎭 Role:           {current_user.get('role', 'Unknown').upper()}")
    print(f"📊 Hierarchy:      {current_user.get('hierarchy_level', 'Unknown')}")
    print("=" * 80)
    print("📋 PERMISSIONS SUMMARY:")
    print("=" * 80)
    
    # Count permissions
    module_count = 0
    total_perms = 0
    
    for module, perms in permissions.items():
        if isinstance(perms, dict) and module not in ['is_admin', 'is_hr', 'is_pm', 'is_tl', 'is_l6', 'is_l7']:
            module_count += 1
            perm_count = sum(1 for v in perms.values() if v is True)
            total_perms += perm_count
            
            if perm_count > 0:
                perm_list = [k for k, v in perms.items() if v is True]
                print(f"  ✅ {module.upper()}: {perm_count} permissions")
                print(f"     → {', '.join(perm_list[:5])}{' ...' if len(perm_list) > 5 else ''}")
    
    print("=" * 80)
    print(f"📊 Total Modules:  {module_count}")
    print(f"🔐 Total Perms:    {total_perms}")
    print(f"🎯 Admin:          {permissions.get('is_admin', False)}")
    print(f"🎯 HR:             {permissions.get('is_hr', False)}")
    print(f"🎯 PM:             {permissions.get('is_pm', False)}")
    print(f"🎯 TL:             {permissions.get('is_tl', False)}")
    print("=" * 80 + "\n")
    
    return {
        "user_id": current_user["id"],
        "role": current_user.get("role"),
        "hierarchy_level": current_user.get("hierarchy_level"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "is_admin": permissions.get("is_admin", False),
        "is_hr": permissions.get("is_hr", False),
        "is_pm": permissions.get("is_pm", False),
        "is_tl": permissions.get("is_tl", False),
        "permissions": permissions
    }
