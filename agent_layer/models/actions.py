"""
Action models for the AI agent system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be taken"""
    NOTIFY_PARENT = "notify_parent"
    NOTIFY_CHILD = "notify_child"
    EDUCATE_CHILD = "educate_child"
    WARN_SENDER = "warn_sender"
    BLOCK_SENDER = "block_sender"
    ESCALATE_TO_AUTHORITIES = "escalate_to_authorities"
    PROVIDE_RESOURCES = "provide_resources"
    SCHEDULE_FOLLOWUP = "schedule_followup"
    NO_ACTION = "no_action"


class ActionPriority(Enum):
    """Priority levels for actions"""
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ActionDecision:
    """Represents a decision made by the AI agent"""
    action_type: ActionType
    priority: ActionPriority
    reasoning: str
    confidence: float  # 0.0-1.0
    target_audience: List[str]  # ["parent", "child", "sender"]
    estimated_impact: str
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class CommunicationContent:
    """Content for communications to different stakeholders"""
    recipient_type: str  # "parent", "child", "sender"
    subject: str
    message: str
    tone: str  # "supportive", "educational", "warning", "firm"
    additional_resources: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.additional_resources is None:
            self.additional_resources = []


@dataclass
class ActionPlan:
    """Complete action plan for handling a suspicious message"""
    message_id: str
    decisions: List[ActionDecision]
    communications: List[CommunicationContent]
    timeline: Dict[str, datetime]  # When each action should be executed
    followup_required: bool
    followup_date: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action plan to dictionary for logging/storage"""
        return {
            "message_id": self.message_id,
            "decisions": [
                {
                    "action_type": decision.action_type.value,
                    "priority": decision.priority.value,
                    "reasoning": decision.reasoning,
                    "confidence": decision.confidence,
                    "target_audience": decision.target_audience,
                    "estimated_impact": decision.estimated_impact
                }
                for decision in self.decisions
            ],
            "communications": [
                {
                    "recipient_type": comm.recipient_type,
                    "subject": comm.subject,
                    "message": comm.message,
                    "tone": comm.tone,
                    "additional_resources": comm.additional_resources
                }
                for comm in self.communications
            ],
            "timeline": {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in self.timeline.items()
            },
            "followup_required": self.followup_required,
            "followup_date": self.followup_date.isoformat() if self.followup_date else None,
            "created_at": self.created_at.isoformat()
        }
