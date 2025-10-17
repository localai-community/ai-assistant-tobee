"""
LocalAI Community - User Sessions API Endpoints
API routes for user session management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..services.repository import UserSessionRepository
from ..models.schemas import UserSession, UserSessionCreate, UserSessionUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/user-sessions", tags=["user-sessions"])

@router.get("/{session_key}", response_model=UserSession)
async def get_user_session(session_key: str, db: Session = Depends(get_db)):
    """
    Get the current user for a session.
    
    Args:
        session_key: Session identifier (e.g., "default_session")
        db: Database session
        
    Returns:
        UserSession: Current user session information
    """
    try:
        session_repo = UserSessionRepository(db)
        session = session_repo.get_session(session_key)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_key}", response_model=UserSession)
async def create_user_session(
    session_key: str, 
    session_data: UserSessionCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new user session.
    
    Args:
        session_key: Session identifier
        session_data: Session creation data
        db: Database session
        
    Returns:
        UserSession: Created user session
    """
    try:
        session_repo = UserSessionRepository(db)
        
        # Check if session already exists
        existing_session = session_repo.get_session(session_key)
        if existing_session:
            raise HTTPException(status_code=400, detail="Session already exists")
        
        created_session = session_repo.create_session(session_data)
        return created_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_key}", response_model=UserSession)
async def update_user_session(
    session_key: str, 
    session_data: UserSessionUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update a user session.
    
    Args:
        session_key: Session identifier
        session_data: Session update data
        db: Database session
        
    Returns:
        UserSession: Updated user session
    """
    try:
        session_repo = UserSessionRepository(db)
        updated_session = session_repo.update_session(session_key, session_data)
        
        if not updated_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return updated_session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_key}/set-user/{user_id}", response_model=UserSession)
async def set_current_user(
    session_key: str, 
    user_id: str, 
    db: Session = Depends(get_db)
):
    """
    Set the current user for a session (create or update).
    
    Args:
        session_key: Session identifier
        user_id: User ID to set as current
        db: Database session
        
    Returns:
        UserSession: Updated user session
    """
    try:
        session_repo = UserSessionRepository(db)
        session = session_repo.upsert_session(session_key, user_id)
        return session
    except Exception as e:
        logger.error(f"Failed to set current user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
