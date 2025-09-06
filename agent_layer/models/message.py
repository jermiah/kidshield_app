"""
Message models for the AI agent system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ThreatType(Enum):
    """Types of threats that can be detected"""
    BULLYING = "bullying"
    HARASSMENT = "harassment"
    INAPPROPRIATE_REQUEST = "inappropriate_request"
    SEXUAL_CONTENT = "sexual_content"
    VIOLENT_CONTENT = "violent_content"
    MANIPULATION = "manipulation"
    SCAM = "scam"
    PHISHING = "phishing"
    STRANGER_CONTACT = "stranger_contact"
    OTHER = "other"


class SeverityLevel(Enum):
    """Severity levels for threats"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChildProfile:
    """Profile information for the child"""
    child_id: str
    age: int
    name: str
    grade_level: Optional[str] = None
    previous_incidents: int = 0
    parental_notification_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parental_notification_preferences is None:
            self.parental_notification_preferences = {
                "immediate_notification": True,
                "daily_summary": False,
                "weekly_summary": True
            }


@dataclass
class MessageMetadata:
    """Metadata associated with a suspicious message"""
    sender_id: str
    sender_type: str  # "known_contact", "stranger", "anonymous"
    platform: str  # "social_media", "messaging_app", "email", "game_chat"
    timestamp: datetime
    message_frequency: int  # Number of messages from this sender in last 24h
    sender_history: Dict[str, Any]  # Previous interactions/reports
    confidence_score: float  # Detection system confidence (0.0-1.0)
    
    def __post_init__(self):
        if self.sender_history is None:
            self.sender_history = {}


@dataclass
class SuspiciousMessage:
    """Main message object containing all relevant information"""
    message_id: str
    content: str
    threat_type: ThreatType
    severity: SeverityLevel
    child_profile: ChildProfile
    metadata: MessageMetadata
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for logging/storage"""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "child_profile": {
                "child_id": self.child_profile.child_id,
                "age": self.child_profile.age,
                "name": self.child_profile.name,
                "grade_level": self.child_profile.grade_level,
                "previous_incidents": self.child_profile.previous_incidents
            },
            "metadata": {
                "sender_id": self.metadata.sender_id,
                "sender_type": self.metadata.sender_type,
                "platform": self.metadata.platform,
                "timestamp": self.metadata.timestamp.isoformat(),
                "message_frequency": self.metadata.message_frequency,
                "confidence_score": self.metadata.confidence_score
            },
            "context": self.context
        }
