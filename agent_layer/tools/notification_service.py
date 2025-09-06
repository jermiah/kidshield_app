"""
Notification Service for Agent Layer
Handles parent notifications, sender warnings, and child education delivery
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

from ..models.actions import CommunicationContent
from ..utils.logger import setup_logger

class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push_notification"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    """Notification priority levels"""
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NotificationService:
    """
    Service for sending notifications to parents, warnings to senders,
    and educational content to children
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger("NotificationService")
        
        # Email configuration
        self.smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.email_user = self.config.get('email_user', '')
        self.email_password = self.config.get('email_password', '')
        
        # SMS configuration (would integrate with service like Twilio)
        self.sms_enabled = self.config.get('sms_enabled', False)
        self.sms_api_key = self.config.get('sms_api_key', '')
        
        # Push notification configuration
        self.push_enabled = self.config.get('push_enabled', False)
        
    def notify_parent(self, communication: CommunicationContent, parent_contact: Dict[str, Any]) -> bool:
        """
        Send notification to parent about child safety incident
        
        Args:
            communication: Communication content from agent layer
            parent_contact: Parent contact information
            
        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Sending parent notification: {communication.subject}")
            
            # Determine notification channels based on priority
            channels = self._determine_channels(communication.priority.value, parent_contact)
            
            success = True
            for channel in channels:
                try:
                    if channel == NotificationChannel.EMAIL:
                        self._send_email_notification(communication, parent_contact)
                    elif channel == NotificationChannel.SMS:
                        self._send_sms_notification(communication, parent_contact)
                    elif channel == NotificationChannel.PUSH:
                        self._send_push_notification(communication, parent_contact)
                    elif channel == NotificationChannel.IN_APP:
                        self._send_in_app_notification(communication, parent_contact)
                        
                    self.logger.info(f"Successfully sent {channel.value} notification to parent")
                    
                except Exception as e:
                    self.logger.error(f"Failed to send {channel.value} notification: {str(e)}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to notify parent: {str(e)}")
            return False
    
    def warn_sender(self, communication: CommunicationContent, sender_contact: Dict[str, Any]) -> bool:
        """
        Send warning to message sender about inappropriate behavior
        
        Args:
            communication: Warning communication content
            sender_contact: Sender contact information
            
        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Sending sender warning: {communication.subject}")
            
            # For sender warnings, typically use the same platform where the message was sent
            platform = sender_contact.get('platform', 'email')
            
            if platform == 'email':
                success = self._send_email_warning(communication, sender_contact)
            elif platform in ['sms', 'text']:
                success = self._send_sms_warning(communication, sender_contact)
            else:
                # For social media platforms, would integrate with their APIs
                success = self._send_platform_warning(communication, sender_contact, platform)
            
            if success:
                self.logger.info(f"Successfully sent warning to sender via {platform}")
            else:
                self.logger.error(f"Failed to send warning to sender via {platform}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to warn sender: {str(e)}")
            return False
    
    def educate_child(self, communication: CommunicationContent, child_info: Dict[str, Any]) -> bool:
        """
        Deliver educational content to child
        
        Args:
            communication: Educational communication content
            child_info: Child information and preferences
            
        Returns:
            bool: Success status
        """
        try:
            self.logger.info(f"Delivering education to child: {communication.subject}")
            
            # Choose age-appropriate delivery method
            age = child_info.get('age', 12)
            delivery_method = self._choose_education_delivery_method(age, child_info)
            
            success = False
            
            if delivery_method == 'in_app':
                success = self._deliver_in_app_education(communication, child_info)
            elif delivery_method == 'email':
                success = self._deliver_email_education(communication, child_info)
            elif delivery_method == 'interactive':
                success = self._deliver_interactive_education(communication, child_info)
            
            if success:
                self.logger.info(f"Successfully delivered education via {delivery_method}")
                # Log educational content delivery for tracking
                self._log_education_delivery(communication, child_info, delivery_method)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to educate child: {str(e)}")
            return False
    
    def _determine_channels(self, priority: str, contact_info: Dict[str, Any]) -> List[NotificationChannel]:
        """Determine which notification channels to use based on priority"""
        
        available_channels = []
        
        # Email is always available if provided
        if contact_info.get('email'):
            available_channels.append(NotificationChannel.EMAIL)
        
        # SMS for high priority if available
        if contact_info.get('phone') and self.sms_enabled:
            available_channels.append(NotificationChannel.SMS)
        
        # Push notifications if enabled
        if contact_info.get('push_token') and self.push_enabled:
            available_channels.append(NotificationChannel.PUSH)
        
        # In-app notifications
        available_channels.append(NotificationChannel.IN_APP)
        
        # Filter based on priority
        if priority == NotificationPriority.IMMEDIATE.value:
            # Use all available channels for immediate notifications
            return available_channels
        elif priority == NotificationPriority.HIGH.value:
            # Use email, SMS, and push for high priority
            return [ch for ch in available_channels if ch != NotificationChannel.IN_APP]
        else:
            # Use email and in-app for medium/low priority
            return [ch for ch in available_channels if ch in [NotificationChannel.EMAIL, NotificationChannel.IN_APP]]
    
    def _send_email_notification(self, communication: CommunicationContent, contact_info: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            if not self.email_user or not self.email_password:
                self.logger.warning("Email credentials not configured")
                return False
            
            msg = MimeMultipart()
            msg['From'] = self.email_user
            msg['To'] = contact_info['email']
            msg['Subject'] = f"KidShield Alert: {communication.subject}"
            
            # Create HTML email body
            html_body = f"""
            <html>
            <body>
                <h2>KidShield Safety Alert</h2>
                <p><strong>Subject:</strong> {communication.subject}</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {communication.content}
                </div>
                <p><em>This is an automated message from KidShield. Please do not reply to this email.</em></p>
                <p>For support, contact: support@kidshield.com</p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _send_sms_notification(self, communication: CommunicationContent, contact_info: Dict[str, Any]) -> bool:
        """Send SMS notification (would integrate with Twilio or similar)"""
        try:
            # This is a placeholder - would integrate with actual SMS service
            phone = contact_info.get('phone')
            message = f"KidShield Alert: {communication.subject}\n\n{communication.content[:100]}..."
            
            self.logger.info(f"SMS would be sent to {phone}: {message}")
            
            # In real implementation:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # client.messages.create(body=message, from_='+1234567890', to=phone)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def _send_push_notification(self, communication: CommunicationContent, contact_info: Dict[str, Any]) -> bool:
        """Send push notification"""
        try:
            # This is a placeholder - would integrate with push notification service
            push_token = contact_info.get('push_token')
            
            notification_data = {
                'title': 'KidShield Alert',
                'body': communication.subject,
                'data': {
                    'type': 'safety_alert',
                    'priority': communication.priority.value,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"Push notification would be sent to {push_token}: {notification_data}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    def _send_in_app_notification(self, communication: CommunicationContent, contact_info: Dict[str, Any]) -> bool:
        """Send in-app notification"""
        try:
            # This would typically store in database for app to retrieve
            notification_record = {
                'user_id': contact_info.get('user_id'),
                'type': 'safety_alert',
                'title': communication.subject,
                'content': communication.content,
                'priority': communication.priority.value,
                'created_at': datetime.now().isoformat(),
                'read': False
            }
            
            self.logger.info(f"In-app notification created: {notification_record}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create in-app notification: {str(e)}")
            return False
    
    def _send_email_warning(self, communication: CommunicationContent, sender_contact: Dict[str, Any]) -> bool:
        """Send email warning to sender"""
        try:
            # Similar to email notification but with warning tone
            if not self.email_user or not self.email_password:
                return False
            
            msg = MimeMultipart()
            msg['From'] = self.email_user
            msg['To'] = sender_contact['email']
            msg['Subject'] = f"Important: {communication.subject}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Important Notice</h2>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107;">
                    {communication.content}
                </div>
                <p>Please review our community guidelines and ensure all future communications are appropriate.</p>
                <p><em>This is an automated message. Continued inappropriate behavior may result in further action.</em></p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email warning: {str(e)}")
            return False
    
    def _send_sms_warning(self, communication: CommunicationContent, sender_contact: Dict[str, Any]) -> bool:
        """Send SMS warning to sender"""
        # Similar to SMS notification but with warning content
        return self._send_sms_notification(communication, sender_contact)
    
    def _send_platform_warning(self, communication: CommunicationContent, sender_contact: Dict[str, Any], platform: str) -> bool:
        """Send warning via social media platform API"""
        try:
            # This would integrate with platform-specific APIs
            self.logger.info(f"Platform warning would be sent via {platform} API")
            
            # In real implementation, would use platform APIs:
            # - Instagram/Facebook Graph API
            # - Discord API
            # - etc.
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send platform warning: {str(e)}")
            return False
    
    def _choose_education_delivery_method(self, age: int, child_info: Dict[str, Any]) -> str:
        """Choose appropriate education delivery method based on age"""
        
        if age < 10:
            return 'interactive'  # Interactive, visual content for young children
        elif age < 13:
            return 'in_app'  # In-app notifications with age-appropriate content
        else:
            return 'email'  # Email with comprehensive educational content
    
    def _deliver_in_app_education(self, communication: CommunicationContent, child_info: Dict[str, Any]) -> bool:
        """Deliver educational content via in-app notification"""
        try:
            education_record = {
                'child_id': child_info.get('child_id'),
                'type': 'educational_content',
                'title': communication.subject,
                'content': communication.content,
                'age_appropriate': True,
                'interactive': child_info.get('age', 12) < 10,
                'created_at': datetime.now().isoformat(),
                'viewed': False
            }
            
            self.logger.info(f"Educational content delivered in-app: {education_record}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deliver in-app education: {str(e)}")
            return False
    
    def _deliver_email_education(self, communication: CommunicationContent, child_info: Dict[str, Any]) -> bool:
        """Deliver educational content via email"""
        # Similar to email notification but with educational content
        return True
    
    def _deliver_interactive_education(self, communication: CommunicationContent, child_info: Dict[str, Any]) -> bool:
        """Deliver interactive educational content"""
        try:
            # This would create interactive educational content
            interactive_content = {
                'child_id': child_info.get('child_id'),
                'type': 'interactive_lesson',
                'title': communication.subject,
                'content': communication.content,
                'activities': [
                    'safety_quiz',
                    'scenario_practice',
                    'reporting_tutorial'
                ],
                'age_group': 'under_10' if child_info.get('age', 12) < 10 else 'over_10',
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Interactive education created: {interactive_content}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create interactive education: {str(e)}")
            return False
    
    def _log_education_delivery(self, communication: CommunicationContent, child_info: Dict[str, Any], method: str):
        """Log educational content delivery for tracking and analytics"""
        
        delivery_log = {
            'child_id': child_info.get('child_id'),
            'content_type': 'safety_education',
            'topic': communication.subject,
            'delivery_method': method,
            'age_at_delivery': child_info.get('age'),
            'delivered_at': datetime.now().isoformat(),
            'triggered_by': communication.context.get('triggered_by', 'threat_detection')
        }
        
        self.logger.info(f"Education delivery logged: {delivery_log}")
        
        # In real implementation, this would be stored in database for analytics
