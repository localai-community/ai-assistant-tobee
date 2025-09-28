from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_settings_repository import UserSettingsRepository
from app.models.schemas import UserSettingsCreate, UserSettingsUpdate, UserSettingsResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/user-settings", tags=["user-settings"])

@router.get("/{user_id}", response_model=UserSettingsResponse)
def get_user_settings(user_id: str, db: Session = Depends(get_db)):
    """Get user settings by user ID."""
    try:
        settings_repo = UserSettingsRepository(db)
        settings = settings_repo.get_user_settings(user_id)
        
        if not settings:
            # Return default settings if none exist
            default_settings = settings_repo.get_default_settings(user_id)
            return UserSettingsResponse(**default_settings)
        
        return UserSettingsResponse.from_orm(settings)
    except Exception as e:
        logger.error(f"Error getting user settings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user settings")

@router.post("/", response_model=UserSettingsResponse)
def create_user_settings(settings: UserSettingsCreate, db: Session = Depends(get_db)):
    """Create new user settings."""
    try:
        settings_repo = UserSettingsRepository(db)
        created_settings = settings_repo.create_user_settings(settings)
        
        if not created_settings:
            raise HTTPException(status_code=400, detail="Failed to create user settings")
        
        return UserSettingsResponse.from_orm(created_settings)
    except Exception as e:
        logger.error(f"Error creating user settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user settings")

@router.put("/{user_id}", response_model=UserSettingsResponse)
def update_user_settings(user_id: str, settings: UserSettingsUpdate, db: Session = Depends(get_db)):
    """Update user settings."""
    try:
        settings_repo = UserSettingsRepository(db)
        updated_settings = settings_repo.update_user_settings(user_id, settings)
        
        if not updated_settings:
            raise HTTPException(status_code=404, detail="User settings not found")
        
        return UserSettingsResponse.from_orm(updated_settings)
    except Exception as e:
        logger.error(f"Error updating user settings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user settings")

@router.post("/{user_id}/upsert", response_model=UserSettingsResponse)
def upsert_user_settings(user_id: str, settings: UserSettingsUpdate, db: Session = Depends(get_db)):
    """Create or update user settings."""
    try:
        settings_repo = UserSettingsRepository(db)
        
        # Convert update to create format
        settings_data = settings.dict(exclude_unset=True)
        settings_data["user_id"] = user_id
        
        # Fill in defaults for missing fields
        default_settings = settings_repo.get_default_settings(user_id)
        for key, value in default_settings.items():
            if key not in settings_data:
                settings_data[key] = value
        
        settings_create = UserSettingsCreate(**settings_data)
        upserted_settings = settings_repo.upsert_user_settings(settings_create)
        
        if not upserted_settings:
            raise HTTPException(status_code=500, detail="Failed to upsert user settings")
        
        return UserSettingsResponse.from_orm(upserted_settings)
    except Exception as e:
        logger.error(f"Error upserting user settings for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upsert user settings")
