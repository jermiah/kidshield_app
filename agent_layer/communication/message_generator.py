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
    Generates concise communications for parents, children, and senders
    based on the threat type, severity, and child's profile
    """
    
    def __init__(self, templates_config: Dict[str, Any] = None, use_llm: bool = True):
        self.templates = templates_config or self._load_default_templates()
        self.logger = logging.getLogger(__name__)
        self.use_llm = use_llm
        
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
        if audience == "parent":
            return self._generate_parent_communication(message, decision)
        elif audience == "child":
            return self._generate_child_communication(message, decision)
        elif audience == "sender":
            return self._generate_sender_communication(message, decision)
        return None
    
    def _generate_parent_communication(self, message: SuspiciousMessage, 
                                     decision: ActionDecision) -> CommunicationContent:
        child_name = message.child_profile.name
        threat_type = message.threat_type.value.replace('_', ' ').title()
        if decision.action_type == ActionType.NOTIFY_PARENT:
            tone = "urgent" if message.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] else "informative"
        else:
            tone = "supportive"
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
                subject, message_content = self._generate_template_parent_message(
                    message, decision, child_name, threat_type, tone
                )
        else:
            subject, message_content = self._generate_template_parent_message(
                message, decision, child_name, threat_type, tone
            )
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
        if decision.action_type == ActionType.NOTIFY_PARENT:
            template_key = "parent_urgent_notification" if message.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] else "parent_standard_notification"
        else:
            template_key = "parent_general_update"
        template = self.templates["parent"].get(template_key, self.templates["parent"]["parent_standard_notification"])
        subject = template["subject"].format(child_name=child_name, threat_type=threat_type)
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
        age = message.child_profile.age
        child_name = message.child_profile.name
        if age <= 10:
            age_group = "young_child"
            tone = "gentle"
        elif age <= 13:
            age_group = "pre_teen"
            tone = "supportive"
        else:
            age_group = "teenager"
            tone = "respectful"
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
                subject, message_content = self._generate_template_child_message(
                    message, decision, child_name, age, age_group
                )
        else:
            subject, message_content = self._generate_template_child_message(
                message, decision, child_name, age, age_group
            )
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
        if decision.action_type == ActionType.NOTIFY_CHILD:
            template_key = f"{age_group}_notification"
        elif decision.action_type == ActionType.EDUCATE_CHILD:
            template_key = f"{age_group}_education"
        else:
            template_key = f"{age_group}_general"
        available_templates = self.templates["child"]
        if template_key not in available_templates:
            template_key = f"{age_group}_notification"
            if template_key not in available_templates:
                template_key = "young_child_notification"
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
        tone = "firm" if decision.action_type == ActionType.WARN_SENDER else "informative"
        if self.use_llm and self.llm_client:
            try:
                llm_message = self.llm_client.generate_sender_warning(
                    threat_type=message.threat_type.value,
                    platform=message.metadata.platform,
                    severity=message.severity.value
                )
                subject = llm_message["subject"]
                message_content = llm_message["message"]
            except Exception as e:
                self.logger.warning(f"Failed to generate LLM sender message: {str(e)}. Using template.")
                subject, message_content = self._generate_template_sender_message(
                    message, decision
                )
        else:
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
        template = self.templates["sender"]["warning"] if decision.action_type == ActionType.WARN_SENDER else self.templates["sender"].get("general", self.templates["sender"]["warning"])
        threat_classification = message.threat_type.value.replace('_', ' ').title()
        subject = template["subject"].format(
            threat_classification=threat_classification,
            severity=message.severity.value.upper()
        )
        message_content = template["message"].format(
            threat_classification=threat_classification,
            violation_type=message.threat_type.value.replace('_', ' '),
            severity_level=message.severity.value,
            platform=message.metadata.platform,
            consequences=self._get_consequence_description(message.threat_type, message.severity)
        )
        return subject, message_content
    
    def _get_child_friendly_description(self, threat_type: ThreatType, age: int) -> str:
        descriptions = {
            ThreatType.BULLYING: {
                "young": "someone was not being kind to you online",
                "older": "you received messages meant to upset you"
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
        tips = {
            ThreatType.BULLYING: {
                "young": "It's not your fault. Talk to a grown-up you trust.",
                "older": "Bullying isn't acceptable. Stay safe and talk to someone you trust."
            },
            ThreatType.STRANGER_CONTACT: {
                "young": "Never share personal info with unknown people.",
                "older": "Be careful sharing info online with strangers."
            }
        }
        age_key = "young" if age <= 12 else "older"
        return tips.get(threat_type, {}).get(age_key, "Talk to an adult if something online makes you uncomfortable.")
    
    def _get_action_description(self, action_type: ActionType) -> str:
        descriptions = {
            ActionType.BLOCK_SENDER: "Sender blocked",
            ActionType.WARN_SENDER: "Warning sent to sender",
            ActionType.NOTIFY_PARENT: "You have been notified",
            ActionType.EDUCATE_CHILD: "Resources shared with your child"
        }
        return descriptions.get(action_type, "Action taken")
    
    def _get_consequence_description(self, threat_type: ThreatType, severity: SeverityLevel = None) -> str:
        base_consequences = {
            ThreatType.SEXUAL_CONTENT: "account suspension, report to authorities",
            ThreatType.VIOLENT_CONTENT: "account suspension, report to authorities",
            ThreatType.MANIPULATION: "account suspension, content removal",
            ThreatType.BULLYING: "account restrictions, content removal",
            ThreatType.HARASSMENT: "account restrictions, content removal",
            ThreatType.SCAM: "account suspension, content removal",
            ThreatType.PHISHING: "account suspension, content removal",
            ThreatType.INAPPROPRIATE_REQUEST: "account restrictions, monitoring",
            ThreatType.STRANGER_CONTACT: "account restrictions, monitoring"
        }
        consequences = base_consequences.get(threat_type, "account restrictions, monitoring")
        if severity and severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
            if "report to authorities" not in consequences:
                consequences += ", report to authorities"
            if "immediate" not in consequences:
                consequences = consequences.replace("account", "immediate account")
        return consequences
    
    def _get_parent_resources(self, threat_type: ThreatType) -> List[Dict[str, str]]:
        base_resources = [
            {
                "title": "Parent Digital Safety Guide",
                "url": "https://example.com/parent-guide",
                "description": "Quick tips for keeping children safe online"
            }
        ]
        threat_specific = {
            ThreatType.BULLYING: [
                {
                    "title": "Cyberbullying Help",
                    "url": "https://example.com/cyberbullying-help",
                    "description": "How to address and prevent bullying"
                }
            ],
            ThreatType.SEXUAL_CONTENT: [
                {
                    "title": "Online Predator Info",
                    "url": "https://example.com/predator-protection",
                    "description": "Signs and prevention"
                }
            ]
        }
        return base_resources + threat_specific.get(threat_type, [])
    
    def _get_child_resources(self, threat_type: ThreatType, age: int) -> List[Dict[str, str]]:
        if age <= 10:
            return [
                {
                    "title": "Internet Safety for Kids",
                    "url": "https://example.com/kids-safety",
                    "description": "Fun safety tips for young users"
                }
            ]
        else:
            return [
                {
                    "title": "Teen Digital Guide",
                    "url": "https://example.com/teen-guide",
                    "description": "Practical online safety for teens"
                }
            ]
    
    def _load_default_templates(self) -> Dict[str, Any]:
        return {
            "parent": {
                "parent_urgent_notification": {
                    "subject": "URGENT: Safety Alert for {child_name}",
                    "message": "Alert: {child_name} had a {threat_type} incident on {platform} at {timestamp}. {action_taken}."
                },
                "parent_standard_notification": {
                    "subject": "Safety Notification for {child_name}",
                    "message": "{child_name} had a {threat_type} situation on {platform} at {timestamp}. {action_taken}."
                }
            },
            "child": {
                "young_child_notification": {
                    "subject": "Hi {child_name}, stay safe online!",
                    "message": "Hi {child_name}, {situation}. {safety_tip}"
                },
                "teenager_notification": {
                    "subject": "Safety Info for {child_name}",
                    "message": "{child_name}, {situation}. {safety_tip}"
                }
            },
            "sender": {
                "warning": {
                    "subject": "{severity} Warning: {threat_classification} Detected",
                    "message": "Warning: Your message is classified as {threat_classification} ({violation_type}) on {platform}. {consequences}."
                }
            }
        }