"""
Message Generator for AI Agent System
Creates tailored communications for different stakeholders
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..models.message import SuspiciousMessage, ThreatType, SeverityLevel
from ..models.actions import ActionDecision, ActionType, CommunicationContent
from ..utils.blackbox_client import BlackBoxClient


class MessageGenerator:
    """
    Generates appropriate communications for parents, children, and senders
    based on the threat type, severity, and child's profile
    """
    
    def __init__(self, templates_config: Dict[str, Any] = None, use_llm: bool = True):
        self.templates = templates_config or self._load_default_templates()
        self.logger = logging.getLogger(__name__)
        self.use_llm = use_llm
        
        # Initialize BlackBox client if LLM is enabled
        if self.use_llm:
            try:
                self.llm_client = BlackBoxClient()
                self.logger.info("BlackBox LLM client initialized for message generation")
            except Exception as e:
                self.logger.warning(f"Failed to initialize BlackBox client: {str(e)}. Using template-based messages.")
                self.use_llm = False
                self.llm_client = None
        else:
            self.llm_client = None
    
    def generate_communications(self, message: SuspiciousMessage, decisions: List[ActionDecision]) -> List[CommunicationContent]:
        """
        Generate all necessary communications based on action decisions
        
        Args:
            message: The suspicious message being handled
            decisions: List of action decisions requiring communications
            
        Returns:
            List of CommunicationContent objects
        """
        communications = []
        
        for decision in decisions:
            if decision.action_type in [ActionType.NOTIFY_PARENT, ActionType.NOTIFY_CHILD, 
                                      ActionType.WARN_SENDER, ActionType.EDUCATE_CHILD]:
                
                for audience in decision.target_audience:
                    if audience in ["parent", "child", "sender"]:
                        comm = self._generate_communication_for_audience(
                            message, decision, audience
                        )
                        if comm:
                            communications.append(comm)
        
        self.logger.info(f"Generated {len(communications)} communications for message {message.message_id}")
        return communications
    
    def _generate_communication_for_audience(self, message: SuspiciousMessage, 
                                           decision: ActionDecision, audience: str) -> CommunicationContent:
        """Generate communication content for specific audience"""
        
        if audience == "parent":
            return self._generate_parent_communication(message, decision)
        elif audience == "child":
            return self._generate_child_communication(message, decision)
        elif audience == "sender":
            return self._generate_sender_communication(message, decision)
        
        return None
    
    def _generate_parent_communication(self, message: SuspiciousMessage, 
                                     decision: ActionDecision) -> CommunicationContent:
        """Generate communication for parents"""
        
        child_name = message.child_profile.name
        threat_type = message.threat_type.value.replace('_', ' ').title()
        
        # Determine tone based on action type and severity
        if decision.action_type == ActionType.NOTIFY_PARENT:
            if message.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                tone = "urgent"
            else:
                tone = "informative"
        else:
            tone = "supportive"
        
        # Try to generate LLM-enhanced message first
        if self.use_llm and self.llm_client:
            try:
                llm_message = self.llm_client.generate_parent_message(
                    child_name=child_name,
                    threat_type=threat_type,
                    severity=message.severity.value,
                    action_taken=self._get_action_description(decision.action_type),
                    tone=tone
                )
                
                subject = llm_message["subject"]
                message_content = llm_message["message"]
                
            except Exception as e:
                self.logger.warning(f"Failed to generate LLM parent message: {str(e)}. Using template.")
                # Fall back to template-based generation
                subject, message_content = self._generate_template_parent_message(
                    message, decision, child_name, threat_type, tone
                )
        else:
            # Use template-based generation
            subject, message_content = self._generate_template_parent_message(
                message, decision, child_name, threat_type, tone
            )
        
        # Add resources based on threat type
        resources = self._get_parent_resources(message.threat_type)
        
        return CommunicationContent(
            recipient_type="parent",
            subject=subject,
            message=message_content,
            tone=tone,
            additional_resources=resources
        )
    
    def _generate_template_parent_message(self, message: SuspiciousMessage, 
                                        decision: ActionDecision, child_name: str, 
                                        threat_type: str, tone: str) -> tuple[str, str]:
        """Generate parent message using templates (fallback method)"""
        
        # Select appropriate template based on action type and severity
        if decision.action_type == ActionType.NOTIFY_PARENT:
            if message.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                template_key = "parent_urgent_notification"
            else:
                template_key = "parent_standard_notification"
        else:
            template_key = "parent_general_update"
        
        template = self.templates["parent"].get(template_key, self.templates["parent"]["parent_standard_notification"])
        
        subject = template["subject"].format(
            child_name=child_name,
            threat_type=threat_type
        )
        
        message_content = template["message"].format(
            child_name=child_name,
            threat_type=threat_type,
            platform=message.metadata.platform,
            timestamp=message.metadata.timestamp.strftime("%Y-%m-%d %H:%M"),
            action_taken=self._get_action_description(decision.action_type)
        )
        
        return subject, message_content
    
    def _generate_child_communication(self, message: SuspiciousMessage, 
                                    decision: ActionDecision) -> CommunicationContent:
        """Generate age-appropriate communication for children"""
        
        age = message.child_profile.age
        child_name = message.child_profile.name
        
        # Determine age group for appropriate messaging
        if age <= 10:
            age_group = "young_child"
            tone = "gentle"
        elif age <= 13:
            age_group = "pre_teen"
            tone = "supportive"
        else:
            age_group = "teenager"
            tone = "respectful"
        
        # Try to generate LLM-enhanced message first
        if self.use_llm and self.llm_client:
            try:
                llm_message = self.llm_client.generate_child_message(
                    child_name=child_name,
                    child_age=age,
                    threat_type=message.threat_type.value,
                    tone=tone
                )
                
                subject = llm_message["subject"]
                message_content = llm_message["message"]
                
            except Exception as e:
                self.logger.warning(f"Failed to generate LLM child message: {str(e)}. Using template.")
                # Fall back to template-based generation
                subject, message_content = self._generate_template_child_message(
                    message, decision, child_name, age, age_group
                )
        else:
            # Use template-based generation
            subject, message_content = self._generate_template_child_message(
                message, decision, child_name, age, age_group
            )
        
        # Add age-appropriate resources
        resources = self._get_child_resources(message.threat_type, age)
        
        return CommunicationContent(
            recipient_type="child",
            subject=subject,
            message=message_content,
            tone=tone,
            additional_resources=resources
        )
    
    def _generate_template_child_message(self, message: SuspiciousMessage, 
                                       decision: ActionDecision, child_name: str, 
                                       age: int, age_group: str) -> tuple[str, str]:
        """Generate child message using templates (fallback method)"""
        
        # Select template based on action type and age group
        if decision.action_type == ActionType.NOTIFY_CHILD:
            template_key = f"{age_group}_notification"
        elif decision.action_type == ActionType.EDUCATE_CHILD:
            template_key = f"{age_group}_education"
        else:
            template_key = f"{age_group}_general"
        
        # Use available template or fallback
        available_templates = self.templates["child"]
        if template_key not in available_templates:
            template_key = f"{age_group}_notification"
            if template_key not in available_templates:
                template_key = "young_child_notification"  # Ultimate fallback
        
        template = available_templates[template_key]
        
        subject = template["subject"].format(child_name=child_name)
        
        message_content = template["message"].format(
            child_name=child_name,
            situation=self._get_child_friendly_description(message.threat_type, age),
            safety_tip=self._get_age_appropriate_safety_tip(message.threat_type, age)
        )
        
        return subject, message_content
    
    def _generate_sender_communication(self, message: SuspiciousMessage, 
                                     decision: ActionDecision) -> CommunicationContent:
        """Generate warning communication for senders"""
        
        if decision.action_type == ActionType.WARN_SENDER:
            tone = "firm"
        else:
            tone = "informative"
        
        # Try to generate LLM-enhanced message first
        if self.use_llm and self.llm_client:
            try:
                llm_message = self.llm_client.generate_sender_warning(
                    threat_type=message.threat_type.value,
                    platform=message.metadata.platform
                )
                
                subject = llm_message["subject"]
                message_content = llm_message["message"]
                
            except Exception as e:
                self.logger.warning(f"Failed to generate LLM sender message: {str(e)}. Using template.")
                # Fall back to template-based generation
                subject, message_content = self._generate_template_sender_message(
                    message, decision
                )
        else:
            # Use template-based generation
            subject, message_content = self._generate_template_sender_message(
                message, decision
            )
        
        return CommunicationContent(
            recipient_type="sender",
            subject=subject,
            message=message_content,
            tone=tone,
            additional_resources=[]
        )
    
    def _generate_template_sender_message(self, message: SuspiciousMessage, 
                                        decision: ActionDecision) -> tuple[str, str]:
        """Generate sender message using templates (fallback method)"""
        
        if decision.action_type == ActionType.WARN_SENDER:
            template = self.templates["sender"]["warning"]
        else:
            template = self.templates["sender"].get("general", self.templates["sender"]["warning"])
        
        subject = template["subject"]
        
        message_content = template["message"].format(
            violation_type=message.threat_type.value.replace('_', ' '),
            platform=message.metadata.platform,
            consequences=self._get_consequence_description(message.threat_type)
        )
        
        return subject, message_content
    
    def _get_child_friendly_description(self, threat_type: ThreatType, age: int) -> str:
        """Get age-appropriate description of the threat"""
        descriptions = {
            ThreatType.BULLYING: {
                "young": "someone was not being kind to you online",
                "older": "you received messages that were meant to hurt or upset you"
            },
            ThreatType.INAPPROPRIATE_REQUEST: {
                "young": "someone asked you to do something that doesn't feel right",
                "older": "you received a request that made you uncomfortable"
            },
            ThreatType.STRANGER_CONTACT: {
                "young": "someone you don't know tried to talk to you",
                "older": "you were contacted by someone unfamiliar"
            }
        }
        
        age_key = "young" if age <= 12 else "older"
        return descriptions.get(threat_type, {}).get(age_key, "something concerning happened online")
    
    def _get_age_appropriate_safety_tip(self, threat_type: ThreatType, age: int) -> str:
        """Get age-appropriate safety tip"""
        tips = {
            ThreatType.BULLYING: {
                "young": "Remember, it's not your fault and you should always tell a grown-up you trust.",
                "older": "Remember that online bullying is not acceptable, and you have the right to feel safe online."
            },
            ThreatType.STRANGER_CONTACT: {
                "young": "Never share personal information with people you don't know.",
                "older": "Be cautious about sharing personal information with unknown contacts online."
            }
        }
        
        age_key = "young" if age <= 12 else "older"
        return tips.get(threat_type, {}).get(age_key, "Always talk to a trusted adult if something online makes you uncomfortable.")
    
    def _get_action_description(self, action_type: ActionType) -> str:
        """Get human-readable description of action taken"""
        descriptions = {
            ActionType.BLOCK_SENDER: "The sender has been blocked from contacting your child",
            ActionType.WARN_SENDER: "A warning has been sent to the sender",
            ActionType.NOTIFY_PARENT: "You have been notified of this incident",
            ActionType.EDUCATE_CHILD: "Educational resources have been provided to your child"
        }
        return descriptions.get(action_type, "Appropriate action has been taken")
    
    def _get_consequence_description(self, threat_type: ThreatType) -> str:
        """Get description of potential consequences for sender"""
        if threat_type in [ThreatType.SEXUAL_CONTENT, ThreatType.VIOLENT_CONTENT]:
            return "account suspension, reporting to authorities, and potential legal action"
        elif threat_type in [ThreatType.BULLYING, ThreatType.HARASSMENT]:
            return "account restrictions, content removal, and potential account suspension"
        else:
            return "account restrictions and content monitoring"
    
    def _get_parent_resources(self, threat_type: ThreatType) -> List[Dict[str, str]]:
        """Get relevant resources for parents"""
        base_resources = [
            {
                "title": "Digital Safety Guide for Parents",
                "url": "https://example.com/parent-guide",
                "description": "Comprehensive guide on keeping children safe online"
            }
        ]
        
        threat_specific = {
            ThreatType.BULLYING: [
                {
                    "title": "Dealing with Cyberbullying",
                    "url": "https://example.com/cyberbullying-help",
                    "description": "Resources for addressing and preventing cyberbullying"
                }
            ],
            ThreatType.SEXUAL_CONTENT: [
                {
                    "title": "Protecting Children from Online Predators",
                    "url": "https://example.com/predator-protection",
                    "description": "Information on recognizing and preventing online predation"
                }
            ]
        }
        
        return base_resources + threat_specific.get(threat_type, [])
    
    def _get_child_resources(self, threat_type: ThreatType, age: int) -> List[Dict[str, str]]:
        """Get age-appropriate resources for children"""
        if age <= 10:
            return [
                {
                    "title": "Internet Safety for Kids",
                    "url": "https://example.com/kids-safety",
                    "description": "Fun and educational safety tips for young internet users"
                }
            ]
        else:
            return [
                {
                    "title": "Teen Digital Citizenship Guide",
                    "url": "https://example.com/teen-guide",
                    "description": "Guide to responsible and safe online behavior for teens"
                }
            ]
    
    def _load_default_templates(self) -> Dict[str, Any]:
        """Load default message templates"""
        return {
            "parent": {
                "parent_urgent_notification": {
                    "subject": "URGENT: Safety Alert for {child_name}",
                    "message": """Dear Parent/Guardian,

We are writing to inform you of a serious safety concern involving your child, {child_name}.

Our system has detected a {threat_type} incident on {platform} at {timestamp}. We have immediately taken action: {action_taken}.

We recommend discussing this incident with {child_name} and reviewing their online activities. Please find attached resources to help you navigate this situation.

If you have any concerns or questions, please don't hesitate to contact us.

Best regards,
Digital Safety Team"""
                },
                "parent_standard_notification": {
                    "subject": "Safety Notification for {child_name}",
                    "message": """Dear Parent/Guardian,

We wanted to inform you about a safety incident involving your child, {child_name}.

Our monitoring system detected a {threat_type} situation on {platform} at {timestamp}. We have taken appropriate action: {action_taken}.

This is a good opportunity to have a conversation with {child_name} about online safety. We've included some helpful resources below.

Best regards,
Digital Safety Team"""
                }
            },
            "child": {
                "young_child_notification": {
                    "subject": "Hi {child_name}, let's talk about staying safe online",
                    "message": """Hi {child_name},

We noticed that {situation}. You did nothing wrong, and we want to help keep you safe.

{safety_tip}

Remember, you can always talk to your parents or a trusted grown-up if something online makes you feel scared, sad, or confused.

Stay safe!
Your Digital Safety Friends"""
                },
                "teenager_notification": {
                    "subject": "Important Safety Information for {child_name}",
                    "message": """Hi {child_name},

We're reaching out because {situation}. We want to make sure you have the information and support you need to stay safe online.

{safety_tip}

Remember, you have the right to feel safe and respected online. If you ever need help or have questions about online safety, don't hesitate to reach out to a trusted adult.

Take care,
Digital Safety Team"""
                }
            },
            "sender": {
                "warning": {
                    "subject": "Warning: Inappropriate Communication Detected",
                    "message": """This is an official warning regarding your recent communication on {platform}.

Your message has been identified as {violation_type}, which violates our community guidelines and potentially applicable laws.

Continued inappropriate behavior may result in: {consequences}

We strongly advise you to review our community guidelines and modify your online behavior accordingly.

Digital Safety Enforcement Team"""
                }
            }
        }
