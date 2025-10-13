# 🎯 User Settings Persistence & Auto-Migrations

## Summary

Fixes user settings not persisting and adds automatic database migrations on backend startup.

## Key Changes

**User Settings:**
- ✅ Added `use_unified_reasoning` and `selected_reasoning_mode` fields to database
- ✅ Fixed user ID persistence across page refreshes (uses URL params)
- ✅ Fixed user switching to load settings instead of overwriting
- ✅ Moved User ID field to navbar for better visibility

**Database Migrations:**
- ✅ Migrations run automatically on backend startup (default behavior)
- ✅ Smart check - only migrates if needed
- ✅ Can disable with `AUTO_MIGRATE=false`
- ✅ Added `migrate_db.py` script for manual migrations

## Files Changed

- Backend: `user_settings.py`, `schemas.py`, `main.py` + new migration
- Frontend: `app.py` (user ID persistence + UI changes)
- New: `migrate_db.py`, `MIGRATIONS.md`

## Testing

✅ Auto-migrations work on startup
✅ User settings persist across refreshes
✅ User switching loads correct settings

## Migration Instructions

**No action needed!** Migrations run automatically when backend starts.

Manual option: `python backend/migrate_db.py`

---

**Ready to merge** ✅

