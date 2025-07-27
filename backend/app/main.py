from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.models import HealthResponse, RootResponse, ApiStatusResponse
from app.core.database import get_db, init_db
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from app.api.advanced_rag import router as advanced_rag_router
from app.api.reasoning import router as reasoning_router

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
app.include_router(rag_router)
app.include_router(advanced_rag_router)
app.include_router(reasoning_router)

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
            "rag": "enabled",
            "advanced_rag": "enabled",
            "mcp": "enabled",
            "reasoning": "enabled"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 