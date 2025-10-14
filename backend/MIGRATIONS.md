# Database Migrations Guide

This guide explains how to manage database migrations for the AI Assistant project.

## What Are Migrations?

Migrations are version-controlled changes to your database schema. When we add new features (like the unified reasoning settings), we need to update the database structure to support them.

## For Users: How to Migrate Your Database

### Option 1: Automatic Migration (Default) 🎯

**Migrations run automatically when the backend starts!**

Just start your backend normally:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You'll see:
```
✅ Database initialized successfully
🔄 Running database migrations...
✅ Database migrations completed successfully
```

**To disable auto-migration** (if needed):
```bash
export AUTO_MIGRATE=false
# or add to .env file:
# AUTO_MIGRATE=false
```

### Option 2: Python Script ✅

Manually migrate without starting the backend:

```bash
cd backend
python migrate_db.py
```

This will:
- Check your current database version
- Apply any pending migrations
- Show you the results

**Check if you need to migrate:**
```bash
python migrate_db.py --check-pending
```

**Check your current version:**
```bash
python migrate_db.py --check
```

**View migration history:**
```bash
python migrate_db.py --history
```

### Option 3: Using Alembic Directly

If you're familiar with Alembic:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
alembic upgrade head
```

## For Developers: Creating New Migrations

### 1. Modify Your Models

Edit your SQLAlchemy models in `backend/app/models/`:

```python
# Example: backend/app/models/user_settings.py
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    # Add new field
    new_field = Column(String(100), default="default_value")
```

### 2. Create Migration

```bash
cd backend
source venv/bin/activate
alembic revision -m "add_new_field_to_user_settings"
```

This creates a new migration file in `backend/alembic/versions/`.

### 3. Edit Migration File

Open the generated file and add the upgrade/downgrade logic:

```python
def upgrade() -> None:
    op.add_column('user_settings', 
        sa.Column('new_field', sa.String(length=100), nullable=True))
    # Set default for existing rows
    op.execute("UPDATE user_settings SET new_field = 'default_value' WHERE new_field IS NULL")

def downgrade() -> None:
    op.drop_column('user_settings', 'new_field')
```

### 4. Test Migration

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-upgrade
alembic upgrade head
```

### 5. Commit

```bash
git add backend/alembic/versions/your_migration_file.py
git add backend/app/models/your_model.py
git commit -m "feat: add new_field to user_settings"
```

## Common Migration Commands

```bash
# Show current revision
alembic current

# Show history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade by 1 version
alembic upgrade +1

# Downgrade by 1 version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Show SQL without executing
alembic upgrade head --sql
```

## Troubleshooting

### "Can't locate revision identified by..."

This means your database version doesn't match the migration files. Fix it:

```python
# Check what's in the database
sqlite3 backend/localai_community.db "SELECT * FROM alembic_version"

# If the version is wrong, update it manually:
sqlite3 backend/localai_community.db "UPDATE alembic_version SET version_num='correct_version'"

# Or use Python:
python migrate_db.py --check
```

### Migration Failed Mid-Way

Alembic doesn't use transactions for SQLite by default, so failed migrations can leave your database in a bad state:

```bash
# Option 1: Fix the migration and re-run
alembic upgrade head

# Option 2: Restore from backup
cp backend/localai_community.db.backup backend/localai_community.db

# Option 3: Start fresh (⚠️ loses data)
rm backend/localai_community.db
alembic upgrade head
```

### Auto-Generate Migrations

Alembic can auto-detect model changes:

```bash
alembic revision --autogenerate -m "auto detected changes"
```

**Note:** Always review auto-generated migrations! They may not detect everything correctly.

## Migration Best Practices

1. **Always test migrations** on a copy of your database first
2. **Backup before migrating** production databases
3. **Make migrations reversible** - always implement `downgrade()`
4. **One logical change per migration** - easier to debug
5. **Use descriptive names** - "add_user_email_field" not "migration1"
6. **Set defaults for new fields** - handle existing data gracefully
7. **Test both upgrade AND downgrade** paths

## Recent Migrations

### c2756f59bd25: Add Unified Reasoning Fields (2025-10-13)

Adds support for unified reasoning settings:
- `use_unified_reasoning` (Boolean)
- `selected_reasoning_mode` (String)

**To apply:**
```bash
python migrate_db.py
```

## Need Help?

- Check `alembic history` to see migration chain
- Use `python migrate_db.py --check` to see current state
- Look at existing migrations in `backend/alembic/versions/` for examples
- Read Alembic docs: https://alembic.sqlalchemy.org/

