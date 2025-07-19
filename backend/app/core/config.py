from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "LocalAI Community"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./localai_community.db"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Vector Database
    vector_db_path: str = "./storage/vector_db"
    
    # File Storage
    upload_dir: str = "./storage/uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".txt", ".md"]
    
    # MCP
    mcp_config_path: str = "./mcp-config-local.json"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure storage directories exist
def ensure_directories():
    """Ensure required directories exist"""
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.vector_db_path, exist_ok=True)

# Initialize directories on import
ensure_directories() 