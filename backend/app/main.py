from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.models import HealthResponse, RootResponse, ApiStatusResponse
from app.core.database import get_db, init_db
from app.api.chat import router as chat_router
from app.api.reasoning import router as reasoning_router
from app.api.user_settings import router as user_settings_router
from app.api.users import router as users_router
from app.api.user_sessions import router as user_sessions_router
from app.api.view_prompts_context import router as view_prompts_context_router

# Create FastAPI app
app = FastAPI(
    title="LocalAI Community",
    description="A local-first AI assistant with MCP and RAG capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
if os.path.exists("storage/uploads"):
    app.mount("/uploads", StaticFiles(directory="storage/uploads"), name="uploads")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        print("✅ Database initialized successfully")
        
        # Auto-run migrations (can be disabled with AUTO_MIGRATE=false)
        auto_migrate = os.getenv("AUTO_MIGRATE", "true").lower() == "true"
        if auto_migrate:
            from alembic.config import Config
            from alembic import command
            from alembic.script import ScriptDirectory
            from alembic.runtime.migration import MigrationContext
            from pathlib import Path
            from sqlalchemy import create_engine
            
            # Get the backend directory path
            backend_dir = Path(__file__).parent.parent
            alembic_ini = backend_dir / "alembic.ini"
            alembic_dir = backend_dir / "alembic"
            
            alembic_cfg = Config(str(alembic_ini))
            alembic_cfg.set_main_option("script_location", str(alembic_dir))
            
            try:
                # Check if migrations are needed
                script = ScriptDirectory.from_config(alembic_cfg)
                
                # Get database engine
                from app.core.database import engine
                with engine.connect() as connection:
                    context = MigrationContext.configure(connection)
                    current_rev = context.get_current_revision()
                    head_rev = script.get_current_head()
                    
                    if current_rev == head_rev:
                        print("✅ Database schema is up to date")
                    else:
                        print(f"🔄 Running database migrations ({current_rev or 'empty'} → {head_rev})...")
                        command.upgrade(alembic_cfg, "head")
                        print("✅ Database migrations completed successfully")
            except Exception as migration_error:
                print(f"⚠️  Migration warning: {migration_error}")
                print("💡 Tip: Run 'python migrate_db.py' to manually migrate or set AUTO_MIGRATE=false to disable")
        else:
            print("ℹ️  Auto-migration disabled (AUTO_MIGRATE=false)")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")

# Shutdown MCP manager on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown MCP manager on shutdown."""
    try:
        from app.services.chat import shutdown_mcp_manager
        await shutdown_mcp_manager()
        print("✅ MCP manager shutdown successfully")
    except Exception as e:
        print(f"❌ Failed to shutdown MCP manager: {e}")

# Include API routers
app.include_router(chat_router)
app.include_router(reasoning_router)
app.include_router(user_settings_router)
app.include_router(users_router)
app.include_router(user_sessions_router)
app.include_router(view_prompts_context_router)

@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint"""
    return RootResponse(
        message="LocalAI Community API",
        version="1.0.0",
        status="running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="localai-community-backend"
    )

@app.get("/api/v1/status", response_model=ApiStatusResponse)
async def api_status():
    """API status endpoint"""
    return ApiStatusResponse(
        api_version="v1",
        status="operational",
        features={
            "chat": "enabled",
            "streaming_chat": "enabled",
            "mcp": "enabled",
            "reasoning": "enabled",
            "user_settings": "enabled",
            "view_prompts_context": "enabled"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 