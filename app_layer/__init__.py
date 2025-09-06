"""
KidShield App Layer
User interface and application management layer
"""

from .api.main_api import app
from .models.user_models import Parent, Child, MessageRequest, NotificationRequest

__version__ = "1.0.0"
__all__ = ["app", "Parent", "Child", "MessageRequest", "NotificationRequest"]
