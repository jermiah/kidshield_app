"""API-specific schemas for Guardian Layer"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from .guardian_schemas import GuardianResponse

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[GuardianResponse] = Field(None, description="Response data")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "input_id": "uuid-1234",
                    "results": {
                        "text_risk": [{"category": "sexual", "score": 0.88}],
                        "image_risk": [{"category": "nudity", "score": 0.91}]
                    },
                    "status": "flagged",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "processing_time": 0.45
                },
                "message": "Content analysis completed"
            }
        }

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid input format",
                "details": "Both text and image cannot be empty"
            }
        }

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
