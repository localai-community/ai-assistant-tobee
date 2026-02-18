from sqlalchemy.orm import Session
from app.models.user_settings import UserSettings
from app.models.schemas import UserSettingsCreate, UserSettingsUpdate
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UserSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_settings(self, user_id: str) -> Optional[UserSettings]:
        """Get user settings by user ID."""
        try:
            return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user settings for user {user_id}: {e}")
            return None

    def create_user_settings(self, user_settings: UserSettingsCreate) -> Optional[UserSettings]:
        """Create new user settings."""
        try:
            db_settings = UserSettings(**user_settings.dict())
            self.db.add(db_settings)
            self.db.commit()
            self.db.refresh(db_settings)
            logger.info(f"Created user settings for user {user_settings.user_id}")
            return db_settings
        except Exception as e:
            logger.error(f"Error creating user settings for user {user_settings.user_id}: {e}")
            self.db.rollback()
            return None

    def update_user_settings(self, user_id: str, user_settings: UserSettingsUpdate) -> Optional[UserSettings]:
        """Update existing user settings."""
        try:
            db_settings = self.get_user_settings(user_id)
            if not db_settings:
                return None

            # Update only provided fields
            update_data = user_settings.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_settings, field, value)

            self.db.commit()
            self.db.refresh(db_settings)
            logger.info(f"Updated user settings for user {user_id}")
            return db_settings
        except Exception as e:
            logger.error(f"Error updating user settings for user {user_id}: {e}")
            self.db.rollback()
            return None

    def upsert_user_settings(self, user_settings: UserSettingsCreate) -> Optional[UserSettings]:
        """Create or update user settings."""
        try:
            existing = self.get_user_settings(user_settings.user_id)
            if existing:
                # Update existing settings
                update_data = UserSettingsUpdate(**user_settings.dict())
                return self.update_user_settings(user_settings.user_id, update_data)
            else:
                # Create new settings
                return self.create_user_settings(user_settings)
        except Exception as e:
            logger.error(f"Error upserting user settings for user {user_settings.user_id}: {e}")
            return None

    def get_default_settings(self, user_id: str) -> Dict[str, Any]:
        """Get default settings for a user."""
        return {
            "user_id": user_id,
            "enable_context_awareness": True,
            "include_memory": False,
            "context_strategy": "conversation_only",
            "selected_model": "llama3:latest",
            "use_streaming": True,
            "use_rag": False,
            "use_advanced_rag": False,
            "use_phase2_reasoning": False,
            "use_reasoning_chat": False,
            "use_phase3_reasoning": False,
            "selected_phase2_engine": "auto",
            "selected_phase3_strategy": "auto",
            "temperature": 0.7,
            "theme": "system"
        }
