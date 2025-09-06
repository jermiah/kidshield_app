"""Pydantic schemas for Guardian Layer structured outputs"""

from typing import List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class GuardianStatus(str, Enum):
    """Status of the guardian analysis"""
    SAFE = "safe"
    FLAGGED = "flagged"
    ERROR = "error"

class RiskCategory(BaseModel):
    """Individual risk category with confidence score"""
    category: str = Field(..., description="Risk category name")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class RiskResult(BaseModel):
    """Risk analysis results for a specific content type"""
    text_risk: List[RiskCategory] = Field(default_factory=list, description="Text-based risk categories")
    image_risk: List[RiskCategory] = Field(default_factory=list, description="Image-based risk categories")

class GuardianRequest(BaseModel):
    """Request schema for Guardian API"""
    text: Optional[str] = Field(None, description="Text content to analyze")
    image: Optional[str] = Field(None, description="Base64 encoded image content")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hey, send me your private pics",
                "image": "base64_encoded_image_here",
                "user_id": "user123"
            }
        }

class GuardianResponse(BaseModel):
    """Structured response schema for Guardian API"""
    input_id: str = Field(..., description="Unique identifier for this analysis")
    results: RiskResult = Field(..., description="Risk analysis results")
    status: GuardianStatus = Field(..., description="Overall status of the content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_id": "uuid-1234",
                "results": {
                    "text_risk": [
                        {"category": "bullying", "score": 0.15},
                        {"category": "sexual", "score": 0.88},
                        {"category": "self_harm", "score": 0.02}
                    ],
                    "image_risk": [
                        {"category": "nudity", "score": 0.91},
                        {"category": "violence", "score": 0.03}
                    ]
                },
                "status": "flagged",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time": 0.45
            }
        }

# Standard risk categories mapping
STANDARD_TEXT_CATEGORIES = [
    "bullying",
    "sexual", 
    "self_harm",
    "hate_speech",
    "violence",
    "profanity",
    "grooming",
    "predatory"
]

STANDARD_IMAGE_CATEGORIES = [
    "nudity",
    "violence", 
    "weapons",
    "self_harm",
    "inappropriate"
]

def generate_input_id() -> str:
    """Generate unique input ID for tracking"""
    return str(uuid.uuid4())

def determine_status(text_risks: List[RiskCategory], image_risks: List[RiskCategory]) -> GuardianStatus:
    """Determine overall status based on risk scores"""
    all_risks = text_risks + image_risks
    
    if not all_risks:
        return GuardianStatus.SAFE
    
    # Check for high-risk scores (>0.7)
    high_risk_threshold = 0.7
    for risk in all_risks:
        if risk.score >= high_risk_threshold:
            return GuardianStatus.FLAGGED
    
    # Check for medium-risk scores (>0.5)
    medium_risk_threshold = 0.5
    for risk in all_risks:
        if risk.score >= medium_risk_threshold:
            return GuardianStatus.FLAGGED
    
    return GuardianStatus.SAFE
