from pydantic import BaseModel
from typing import Dict, Any, Optional

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str

class RootResponse(BaseModel):
    """Root endpoint response model"""
    message: str
    version: str
    status: str

class ApiStatusResponse(BaseModel):
    """API status response model"""
    api_version: str
    status: str
    features: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    status_code: int 