#!/usr/bin/env python3
"""
Utility script to delete a user and all related data from the database.
This script is useful for database maintenance and cleanup.

Usage: python delete_user.py <username> [--force]
Example: python delete_user.py default --force

The --force flag skips the confirmation prompt (useful for automation).
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.repository import UserRepository
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_user_by_username(username: str) -> bool:
    """
    Delete a user by username and all related data.
    
    Args:
        username: Username to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    db: Session = SessionLocal()
    try:
        user_repo = UserRepository(db)
        
        # First, let's check if the user exists
        user = user_repo.get_user_by_username(username)
        if not user:
            logger.warning(f"User '{username}' not found")
            return False
        
        logger.info(f"Found user '{username}' (ID: {user.id})")
        
        # Get some stats before deletion
        conversations_count = len(user.conversations) if user.conversations else 0
        logger.info(f"User has {conversations_count} conversations")
        
        # Delete the user (cascade delete will handle all related data)
        deleted = user_repo.delete_user_by_username(username)
        
        if deleted:
            logger.info(f"✅ Successfully deleted user '{username}' and all related data")
            return True
        else:
            logger.error(f"❌ Failed to delete user '{username}'")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error deleting user '{username}': {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python delete_user.py <username> [--force]")
        print("Example: python delete_user.py default")
        print("Example: python delete_user.py default --force")
        sys.exit(1)
    
    username = sys.argv[1]
    force = len(sys.argv) == 3 and sys.argv[2] == '--force'
    
    print(f"🗑️  Deleting user '{username}' and all related data...")
    print("⚠️  This action cannot be undone!")
    
    # Ask for confirmation unless --force is used
    if not force:
        try:
            confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("❌ Deletion cancelled")
                sys.exit(0)
        except EOFError:
            print("❌ Cannot get user input. Use --force flag to skip confirmation.")
            print("Example: python delete_user.py default --force")
            sys.exit(1)
    
    success = delete_user_by_username(username)
    
    if success:
        print(f"✅ User '{username}' has been successfully deleted")
        sys.exit(0)
    else:
        print(f"❌ Failed to delete user '{username}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
