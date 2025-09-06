"""Data models for the Guardian App Pipeline"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from datetime import datetime

class RiskLevel(Enum):
    """Risk levels for content assessment"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ContentType(Enum):
    """Types of content that can be processed"""
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"

class ThreatCategory(Enum):
    """Categories of threats detected"""
    PROFANITY = "profanity"
    HATE_SPEECH = "hate_speech"
    GROOMING = "grooming"
    SELF_HARM = "self_harm"
    NSFW = "nsfw"
    VIOLENCE = "violence"
    WEAPONS = "weapons"
    PREDATORY = "predatory"
    CSAM = "csam"
    NONE = "none"

@dataclass
class InputMessage:
    """Input message containing text and/or image"""
    message_id: str
    text: Optional[str] = None
    image_data: Optional[bytes] = None
    image_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def content_type(self) -> ContentType:
        """Determine the content type of the message"""
        has_text = self.text is not None and len(self.text.strip()) > 0
        has_image = self.image_data is not None or self.image_path is not None
        
        if has_text and has_image:
            return ContentType.MULTIMODAL
        elif has_image:
            return ContentType.IMAGE
        elif has_text:
            return ContentType.TEXT
        else:
            raise ValueError("Message must contain either text or image")

@dataclass
class AgentResult:
    """Result from an individual agent"""
    agent_name: str
    confidence: float
    risk_score: float
    threats_detected: List[ThreatCategory]
    explanation: str
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PipelineResult:
    """Final result from the entire pipeline"""
    message_id: str
    risk_level: RiskLevel
    overall_risk_score: float
    threats_detected: List[ThreatCategory]
    agent_results: List[AgentResult]
    decision: str
    child_message: Optional[str] = None
    parent_message: Optional[str] = None
    blocked: bool = False
    processing_time: float = 0.0
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class EducationContent:
    """Educational content for children and parents"""
    child_message: str
    parent_message: str
    severity_explanation: str
    recommended_actions: List[str]
    resources: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.resources is None:
            self.resources = []

@dataclass
class NotificationData:
    """Data for parent notifications"""
    message_id: str
    risk_level: RiskLevel
    threats_detected: List[ThreatCategory]
    content_summary: str
    timestamp: datetime
    recommended_actions: List[str]
    child_id: Optional[str] = None
    
class PipelineStage(Enum):
    """Stages in the pipeline"""
    INPUT = "input"
    TEXT_CLASSIFIER = "text_classifier"
    IMAGE_CLASSIFIER = "image_classifier"
    CROSS_MODAL = "cross_modal"
    REASONING = "reasoning"
    DECISION = "decision"
    EDUCATION = "education"
    COMPLETE = "complete"
