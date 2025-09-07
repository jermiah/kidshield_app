"""API-specific schemas for Guardian Layer"""

from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
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

class AgentProcessingInfo(BaseModel):
    """Information about agent layer processing"""
    triggered: bool = Field(..., description="Whether agent processing was triggered")
    message_id: Optional[str] = Field(None, description="Message ID in agent system")
    actions_planned: Optional[int] = Field(None, description="Number of actions planned")
    action_types: Optional[List[str]] = Field(None, description="Types of actions planned")
    followup_required: Optional[bool] = Field(None, description="Whether followup is required")
    followup_date: Optional[str] = Field(None, description="Followup date in ISO format")
    action_plan: Optional[Dict[str, Any]] = Field(None, description="Complete action plan with decisions and communications")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class EnhancedAPIResponse(BaseModel):
    """Enhanced API response wrapper for auto-analyze endpoint"""
    success: bool = Field(..., description="Whether the request was successful")
    data: Dict[str, Any] = Field(..., description="Response data with guardian analysis and agent processing")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "guardian_analysis": {
                        "input_id": "uuid-1234",
                        "results": {
                            "text_risk": [{"category": "sexual", "score": 0.88}],
                            "image_risk": []
                        },
                        "status": "flagged",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "processing_time": 0.45
                    },
                    "agent_processing": {
                        "triggered": True,
                        "message_id": "msg-5678",
                        "actions_planned": 2,
                        "action_types": ["notify_parent", "educate_child"],
                        "followup_required": True,
                        "followup_date": "2025-09-14T10:00:00",
                        "action_plan": {
                            "message_id": "msg-5678",
                            "decisions": [
                                {
                                    "action_type": "notify_parent",
                                    "priority": "immediate",
                                    "reasoning": "High-risk content detected requiring immediate parental awareness",
                                    "confidence": 0.95,
                                    "target_audience": ["parent"],
                                    "estimated_impact": "High - immediate protection"
                                }
                            ],
                            "communications": [
                                {
                                    "recipient_type": "parent",
                                    "subject": "Urgent: Concerning Content Detected",
                                    "message": "We detected potentially harmful content...",
                                    "tone": "supportive",
                                    "additional_resources": []
                                }
                            ],
                            "timeline": {
                                "notify_parent_0": "2025-09-07T10:36:50"
                            },
                            "followup_required": True,
                            "followup_date": "2025-09-14T10:00:00",
                            "created_at": "2025-09-07T10:36:50"
                        }
                    }
                },
                "message": "Text analysis completed - Risks detected, agent actions initiated"
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
