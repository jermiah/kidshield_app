"""
Decision Engine for AI Agent System
Analyzes suspicious messages and determines appropriate actions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..models.message import SuspiciousMessage, ThreatType, SeverityLevel
from ..models.actions import ActionDecision, ActionType, ActionPriority
from ..utils.blackbox_client import BlackBoxClient


class DecisionEngine:
    """
    Core decision-making component that analyzes suspicious messages
    and determines appropriate actions based on context and severity
    """
    
    def __init__(self, config: Dict[str, Any] = None, use_llm: bool = True):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.use_llm = use_llm
        
        # Initialize BlackBox client if LLM is enabled
        if self.use_llm:
            try:
                self.llm_client = BlackBoxClient()
                self.logger.info("BlackBox LLM client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize BlackBox client: {str(e)}. Falling back to rule-based decisions.")
                self.use_llm = False
                self.llm_client = None
        else:
            self.llm_client = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for decision making"""
        return {
            "severity_thresholds": {
                "critical": 0.9,
                "high": 0.7,
                "medium": 0.4,
                "low": 0.0
            },
            "age_groups": {
                "young_child": (5, 10),
                "pre_teen": (11, 13),
                "teenager": (14, 17),
                "young_adult": (18, 21)
            },
            "immediate_action_triggers": [
                ThreatType.SEXUAL_CONTENT,
                ThreatType.VIOLENT_CONTENT,
                ThreatType.MANIPULATION
            ]
        }
    
    def analyze_message(self, message: SuspiciousMessage) -> List[ActionDecision]:
        """
        Main analysis method that determines appropriate actions
        
        Args:
            message: The suspicious message to analyze
            
        Returns:
            List of ActionDecision objects representing recommended actions
        """
        self.logger.info(f"Analyzing message {message.message_id}")
        
        decisions = []
        
        # Assess overall risk level
        risk_score = self._calculate_risk_score(message)
        
        # Determine primary actions based on threat type and severity
        primary_actions = self._determine_primary_actions(message, risk_score)
        decisions.extend(primary_actions)
        
        # Determine communication actions
        communication_actions = self._determine_communication_actions(message, risk_score)
        decisions.extend(communication_actions)
        
        # Determine educational actions
        educational_actions = self._determine_educational_actions(message)
        decisions.extend(educational_actions)
        
        # Check for escalation needs
        escalation_actions = self._check_escalation_needs(message, risk_score)
        decisions.extend(escalation_actions)
        
        self.logger.info(f"Generated {len(decisions)} action decisions for message {message.message_id}")
        return decisions
    
    def _calculate_risk_score(self, message: SuspiciousMessage) -> float:
        """Calculate overall risk score based on multiple factors"""
        base_score = 0.0
        
        # Severity contribution (40% of score)
        severity_weights = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.75,
            SeverityLevel.MEDIUM: 0.5,
            SeverityLevel.LOW: 0.25
        }
        base_score += severity_weights[message.severity] * 0.4
        
        # Threat type contribution (30% of score)
        threat_weights = {
            ThreatType.SEXUAL_CONTENT: 1.0,
            ThreatType.VIOLENT_CONTENT: 0.9,
            ThreatType.MANIPULATION: 0.85,
            ThreatType.BULLYING: 0.7,
            ThreatType.HARASSMENT: 0.7,
            ThreatType.SCAM: 0.6,
            ThreatType.PHISHING: 0.6,
            ThreatType.INAPPROPRIATE_REQUEST: 0.5,
            ThreatType.STRANGER_CONTACT: 0.4,
            ThreatType.OTHER: 0.3
        }
        base_score += threat_weights.get(message.threat_type, 0.3) * 0.3
        
        # Child age factor (15% of score) - younger children get higher risk
        age_factor = max(0, (18 - message.child_profile.age) / 18)
        base_score += age_factor * 0.15
        
        # Previous incidents factor (10% of score)
        incident_factor = min(1.0, message.child_profile.previous_incidents / 5)
        base_score += incident_factor * 0.1
        
        # Sender history factor (5% of score)
        if message.metadata.sender_history.get('previous_reports', 0) > 0:
            base_score += 0.05
        
        return min(1.0, base_score)
    
    def _determine_primary_actions(self, message: SuspiciousMessage, risk_score: float) -> List[ActionDecision]:
        """Determine primary protective actions"""
        actions = []
        
        # Critical/High risk - immediate blocking
        if risk_score >= 0.8 or message.threat_type in self.config["immediate_action_triggers"]:
            # Generate LLM-enhanced reasoning if available
            reasoning = self._generate_enhanced_reasoning(
                message, "block_sender", risk_score,
                f"High risk score ({risk_score:.2f}) or critical threat type requires immediate sender blocking"
            )
            
            actions.append(ActionDecision(
                action_type=ActionType.BLOCK_SENDER,
                priority=ActionPriority.IMMEDIATE,
                reasoning=reasoning,
                confidence=0.9,
                target_audience=["system"],
                estimated_impact="Prevents further contact from potentially dangerous sender"
            ))
        
        # Medium-High risk - warning to sender
        elif risk_score >= 0.5:
            reasoning = self._generate_enhanced_reasoning(
                message, "warn_sender", risk_score,
                f"Medium-high risk score ({risk_score:.2f}) warrants sender warning"
            )
            
            actions.append(ActionDecision(
                action_type=ActionType.WARN_SENDER,
                priority=ActionPriority.HIGH,
                reasoning=reasoning,
                confidence=0.8,
                target_audience=["sender"],
                estimated_impact="May deter inappropriate behavior and document warning"
            ))
        
        return actions
    
    def _determine_communication_actions(self, message: SuspiciousMessage, risk_score: float) -> List[ActionDecision]:
        """Determine communication actions for parents and children"""
        actions = []
        
        # Always notify parent for high-risk situations
        if risk_score >= 0.6:
            actions.append(ActionDecision(
                action_type=ActionType.NOTIFY_PARENT,
                priority=ActionPriority.IMMEDIATE if risk_score >= 0.8 else ActionPriority.HIGH,
                reasoning=f"High risk score ({risk_score:.2f}) requires immediate parental notification",
                confidence=0.95,
                target_audience=["parent"],
                estimated_impact="Ensures parent awareness and enables protective measures"
            ))
        
        # Notify child based on age and situation
        if message.child_profile.age >= 10:  # Age-appropriate notification
            priority = ActionPriority.HIGH if risk_score >= 0.7 else ActionPriority.MEDIUM
            actions.append(ActionDecision(
                action_type=ActionType.NOTIFY_CHILD,
                priority=priority,
                reasoning=f"Child is old enough ({message.child_profile.age}) to receive age-appropriate notification",
                confidence=0.8,
                target_audience=["child"],
                estimated_impact="Increases child's awareness and safety knowledge"
            ))
        
        return actions
    
    def _determine_educational_actions(self, message: SuspiciousMessage) -> List[ActionDecision]:
        """Determine educational actions based on threat type and child profile"""
        actions = []
        
        # Educational content for child (age-appropriate)
        if message.child_profile.age >= 8:
            actions.append(ActionDecision(
                action_type=ActionType.EDUCATE_CHILD,
                priority=ActionPriority.MEDIUM,
                reasoning=f"Educational intervention appropriate for {message.threat_type.value} threat",
                confidence=0.85,
                target_audience=["child"],
                estimated_impact="Builds long-term safety awareness and resilience"
            ))
        
        # Provide resources to parents
        actions.append(ActionDecision(
            action_type=ActionType.PROVIDE_RESOURCES,
            priority=ActionPriority.MEDIUM,
            reasoning="Parents benefit from resources on digital safety and communication strategies",
            confidence=0.9,
            target_audience=["parent"],
            estimated_impact="Empowers parents with knowledge and tools for ongoing protection"
        ))
        
        return actions
    
    def _check_escalation_needs(self, message: SuspiciousMessage, risk_score: float) -> List[ActionDecision]:
        """Check if situation requires escalation to authorities"""
        actions = []
        
        # Escalate for severe threats or repeated incidents
        escalation_triggers = [
            risk_score >= 0.9,
            message.threat_type in [ThreatType.SEXUAL_CONTENT, ThreatType.VIOLENT_CONTENT],
            message.child_profile.previous_incidents >= 3,
            message.metadata.sender_history.get('previous_reports', 0) >= 2
        ]
        
        if any(escalation_triggers):
            actions.append(ActionDecision(
                action_type=ActionType.ESCALATE_TO_AUTHORITIES,
                priority=ActionPriority.HIGH,
                reasoning="Situation meets criteria for law enforcement involvement",
                confidence=0.8,
                target_audience=["authorities"],
                estimated_impact="Ensures proper investigation and legal protection"
            ))
        
        # Schedule follow-up for ongoing monitoring
        if risk_score >= 0.4:
            actions.append(ActionDecision(
                action_type=ActionType.SCHEDULE_FOLLOWUP,
                priority=ActionPriority.LOW,
                reasoning="Situation requires ongoing monitoring and follow-up",
                confidence=0.7,
                target_audience=["system"],
                estimated_impact="Ensures continued safety monitoring and support"
            ))
        
        return actions
    
    def _generate_enhanced_reasoning(self, message: SuspiciousMessage, 
                                   action_type: str, risk_score: float, 
                                   fallback_reasoning: str) -> str:
        """Generate enhanced reasoning using LLM if available"""
        
        if not self.use_llm or not self.llm_client:
            return fallback_reasoning
        
        try:
            enhanced_reasoning = self.llm_client.generate_decision_reasoning(
                message_content=message.content,
                threat_type=message.threat_type.value,
                severity=message.severity.value,
                child_age=message.child_profile.age,
                context={
                    "risk_score": risk_score,
                    "action_type": action_type,
                    "sender_type": message.metadata.sender_type,
                    "platform": message.metadata.platform,
                    "previous_incidents": message.child_profile.previous_incidents,
                    "message_frequency": message.metadata.message_frequency
                }
            )
            
            # Combine LLM reasoning with fallback for completeness
            return f"{enhanced_reasoning}\n\nTechnical Assessment: {fallback_reasoning}"
            
        except Exception as e:
            self.logger.warning(f"Failed to generate enhanced reasoning: {str(e)}. Using fallback.")
            return fallback_reasoning
    
    def get_age_group(self, age: int) -> str:
        """Determine age group for tailored responses"""
        for group, (min_age, max_age) in self.config["age_groups"].items():
            if min_age <= age <= max_age:
                return group
        return "young_adult"
