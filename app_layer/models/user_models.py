"""
User Models for KidShield App Layer
Defines data structures for users, profiles, and app-specific data
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    """User roles in the system"""
    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"

class NotificationPreference(Enum):
    """Notification preferences"""
    IMMEDIATE = "immediate"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    DISABLED = "disabled"

class ContentFilterLevel(Enum):
    """Content filtering levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    STRICT = "strict"

@dataclass
class Parent:
    """Parent user model"""
    parent_id: str
    email: str
    name: str
    phone: Optional[str] = None
    children_ids: List[str] = None
    notification_preferences: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.notification_preferences is None:
            self.notification_preferences = {
                "threat_alerts": NotificationPreference.IMMEDIATE.value,
                "daily_summary": NotificationPreference.DAILY_SUMMARY.value,
                "weekly_report": NotificationPreference.WEEKLY_SUMMARY.value,
                "educational_content": NotificationPreference.WEEKLY_SUMMARY.value
            }
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Child:
    """Child user model"""
    child_id: str
    parent_id: str
    name: str
    age: int
    grade_level: Optional[str] = None
    safety_settings: Dict[str, Any] = None
    platforms: List[str] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def __post_init__(self):
        if self.safety_settings is None:
            # Age-appropriate default settings
            if self.age < 10:
                filter_level = ContentFilterLevel.STRICT.value
                stranger_blocking = True
                educational_mode = "simple"
            elif self.age < 13:
                filter_level = ContentFilterLevel.HIGH.value
                stranger_blocking = True
                educational_mode = "age_appropriate"
            else:
                filter_level = ContentFilterLevel.MEDIUM.value
                stranger_blocking = False
                educational_mode = "comprehensive"
            
            self.safety_settings = {
                "content_filtering": filter_level,
                "stranger_contact_blocking": stranger_blocking,
                "educational_mode": educational_mode,
                "auto_block_threats": True,
                "parent_notification_threshold": "medium"
            }
        
        if self.platforms is None:
            self.platforms = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class MessageRequest:
    """Request model for message analysis"""
    content: str
    child_id: str
    sender_info: Dict[str, Any]
    platform: str
    child_age: Optional[int] = None
    child_name: Optional[str] = None
    grade_level: Optional[str] = None
    previous_incidents: Optional[int] = None
    message_frequency: Optional[int] = None
    image_data: Optional[bytes] = None
    additional_context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}

@dataclass
class NotificationRequest:
    """Request model for sending notifications"""
    recipient_type: str  # 'parent', 'child', 'sender'
    recipient_id: str
    message: str
    priority: str  # 'immediate', 'high', 'medium', 'low'
    notification_type: str  # 'threat_alert', 'educational', 'warning', 'summary'
    related_message_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

@dataclass
class SafetyReport:
    """Safety report model"""
    report_id: str
    child_id: str
    parent_id: str
    report_type: str  # 'daily', 'weekly', 'monthly', 'custom'
    period_start: datetime
    period_end: datetime
    summary: Dict[str, Any]
    threat_breakdown: Dict[str, int]
    actions_taken: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()

@dataclass
class IncidentRecord:
    """Record of a safety incident"""
    incident_id: str
    child_id: str
    message_id: str
    threat_type: str
    severity: str
    content_summary: str
    actions_taken: List[str]
    resolution_status: str  # 'pending', 'resolved', 'escalated'
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PlatformConnection:
    """Model for connected platforms"""
    connection_id: str
    child_id: str
    platform_name: str
    platform_user_id: str
    connection_status: str  # 'active', 'inactive', 'error'
    permissions: List[str]
    last_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class EducationalContent:
    """Educational content delivery record"""
    content_id: str
    child_id: str
    content_type: str  # 'safety_tip', 'interactive_lesson', 'video', 'article'
    topic: str
    age_group: str
    delivery_method: str  # 'notification', 'dashboard', 'email'
    delivered_at: Optional[datetime] = None
    viewed: bool = False
    viewed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.delivered_at is None:
            self.delivered_at = datetime.now()

class AppSettings:
    """Application-wide settings"""
    
    # Default safety settings by age group
    AGE_GROUP_SETTINGS = {
        "under_10": {
            "content_filtering": ContentFilterLevel.STRICT.value,
            "stranger_blocking": True,
            "educational_mode": "simple",
            "auto_block_threshold": 0.3,
            "parent_notification_threshold": 0.2
        },
        "10_to_12": {
            "content_filtering": ContentFilterLevel.HIGH.value,
            "stranger_blocking": True,
            "educational_mode": "age_appropriate",
            "auto_block_threshold": 0.5,
            "parent_notification_threshold": 0.4
        },
        "13_to_15": {
            "content_filtering": ContentFilterLevel.MEDIUM.value,
            "stranger_blocking": False,
            "educational_mode": "comprehensive",
            "auto_block_threshold": 0.7,
            "parent_notification_threshold": 0.6
        },
        "over_15": {
            "content_filtering": ContentFilterLevel.LOW.value,
            "stranger_blocking": False,
            "educational_mode": "comprehensive",
            "auto_block_threshold": 0.8,
            "parent_notification_threshold": 0.7
        }
    }
    
    # Supported platforms
    SUPPORTED_PLATFORMS = [
        "instagram", "snapchat", "tiktok", "discord", 
        "whatsapp", "messenger", "sms", "email"
    ]
    
    # Notification channels
    NOTIFICATION_CHANNELS = [
        "email", "sms", "push_notification", "in_app"
    ]
    
    @classmethod
    def get_age_group_settings(cls, age: int) -> Dict[str, Any]:
        """Get default settings for age group"""
        if age < 10:
            return cls.AGE_GROUP_SETTINGS["under_10"]
        elif age <= 12:
            return cls.AGE_GROUP_SETTINGS["10_to_12"]
        elif age <= 15:
            return cls.AGE_GROUP_SETTINGS["13_to_15"]
        else:
            return cls.AGE_GROUP_SETTINGS["over_15"]
