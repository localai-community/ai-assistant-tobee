#!/usr/bin/env python3
"""
Database Migration Script

This script runs Alembic migrations programmatically.
It can be used by other users to migrate their databases without using the command line.

Usage:
    python migrate_db.py                    # Migrate to latest version
    python migrate_db.py --downgrade -1     # Downgrade by 1 revision
    python migrate_db.py --check            # Check current version
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_alembic_config():
    """Get Alembic configuration."""
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    return alembic_cfg


def check_current_revision():
    """Check the current database revision."""
    try:
        from app.core.database import engine
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            if current_rev:
                logger.info(f"✅ Current database revision: {current_rev}")
                return current_rev
            else:
                logger.warning("⚠️  No revision found - database may not be initialized")
                return None
    except Exception as e:
        logger.error(f"❌ Error checking revision: {e}")
        return None


def check_pending_migrations():
    """Check if there are pending migrations."""
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)
        
        from app.core.database import engine
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            head_rev = script.get_current_head()
            
            if current_rev == head_rev:
                logger.info("✅ Database is up to date!")
                return False
            else:
                logger.info(f"📋 Pending migration from {current_rev} to {head_rev}")
                return True
    except Exception as e:
        logger.error(f"❌ Error checking pending migrations: {e}")
        return False


def upgrade_database(revision="head"):
    """
    Upgrade database to a specific revision.
    
    Args:
        revision (str): Target revision (default: "head" for latest)
    """
    try:
        logger.info(f"🚀 Starting database migration to {revision}...")
        alembic_cfg = get_alembic_config()
        
        # Run the upgrade
        command.upgrade(alembic_cfg, revision)
        
        logger.info("✅ Database migration completed successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def downgrade_database(revision):
    """
    Downgrade database to a specific revision.
    
    Args:
        revision (str): Target revision (e.g., "-1" for previous, specific hash)
    """
    try:
        logger.info(f"⬇️  Downgrading database to {revision}...")
        alembic_cfg = get_alembic_config()
        
        # Run the downgrade
        command.downgrade(alembic_cfg, revision)
        
        logger.info("✅ Database downgrade completed successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Downgrade failed: {e}")
        return False


def show_history():
    """Show migration history."""
    try:
        logger.info("📜 Migration History:")
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg)
        return True
    except Exception as e:
        logger.error(f"❌ Error showing history: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Database Migration Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_db.py                     # Migrate to latest
  python migrate_db.py --check             # Check current version
  python migrate_db.py --check-pending     # Check for pending migrations
  python migrate_db.py --downgrade -1      # Downgrade by 1 revision
  python migrate_db.py --history           # Show migration history
        """
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check current database revision'
    )
    
    parser.add_argument(
        '--check-pending',
        action='store_true',
        help='Check if there are pending migrations'
    )
    
    parser.add_argument(
        '--downgrade',
        type=str,
        metavar='REVISION',
        help='Downgrade to specific revision (e.g., -1 for previous)'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show migration history'
    )
    
    parser.add_argument(
        '--revision',
        type=str,
        default='head',
        help='Target revision for upgrade (default: head)'
    )
    
    args = parser.parse_args()
    
    # Handle different actions
    if args.check:
        check_current_revision()
    elif args.check_pending:
        check_pending_migrations()
    elif args.downgrade:
        downgrade_database(args.downgrade)
    elif args.history:
        show_history()
    else:
        # Default action: upgrade to head
        logger.info("=" * 60)
        logger.info("DATABASE MIGRATION")
        logger.info("=" * 60)
        
        # Check current state
        current_rev = check_current_revision()
        has_pending = check_pending_migrations()
        
        if has_pending or current_rev is None:
            # Run migration
            success = upgrade_database(args.revision)
            
            if success:
                logger.info("=" * 60)
                logger.info("✅ MIGRATION COMPLETE")
                logger.info("=" * 60)
                return 0
            else:
                logger.error("=" * 60)
                logger.error("❌ MIGRATION FAILED")
                logger.error("=" * 60)
                return 1
        else:
            logger.info("=" * 60)
            logger.info("✅ NO MIGRATION NEEDED")
            logger.info("=" * 60)
            return 0


if __name__ == "__main__":
    sys.exit(main())

