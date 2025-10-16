"""
LocalAI Community - Users API Endpoints
API routes for user management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from ..core.database import get_db
from ..services.repository import UserRepository
from ..models.schemas import User, UserCreate, UserUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", response_model=List[User])
async def get_users(db: Session = Depends(get_db)):
    """
    Get all active users.
    
    Args:
        db: Database session
        
    Returns:
        List[User]: All active users
    """
    try:
        user_repo = UserRepository(db)
        users = user_repo.get_users()
        return users
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User: User information
    """
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-username/{username}")
async def check_username_exists(username: str, db: Session = Depends(get_db)):
    """
    Check if a username already exists.
    
    Args:
        username: Username to check
        db: Database session
        
    Returns:
        dict: Username existence status
    """
    try:
        user_repo = UserRepository(db)
        existing_user = user_repo.get_user_by_username(username)
        
        return {
            "username": username,
            "exists": existing_user is not None,
            "user_id": existing_user.id if existing_user else None
        }
    except Exception as e:
        logger.error(f"Failed to check username {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Args:
        user: User creation data
        db: Database session
        
    Returns:
        User: Created user
    """
    try:
        user_repo = UserRepository(db)
        
        # Check if username already exists
        existing_user = user_repo.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        created_user = user_repo.create_user(user)
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete a user and all related data.
    
    Args:
        user_id: User ID to delete
        db: Database session
        
    Returns:
        dict: Deletion status
    """
    try:
        user_repo = UserRepository(db)
        deleted = user_repo.delete_user(user_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": f"User {user_id} and all related data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/username/{username}")
async def delete_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Delete a user by username and all related data.
    
    Args:
        username: Username to delete
        db: Database session
        
    Returns:
        dict: Deletion status
    """
    try:
        user_repo = UserRepository(db)
        deleted = user_repo.delete_user_by_username(username)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        
        return {"message": f"User '{username}' and all related data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user '{username}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
