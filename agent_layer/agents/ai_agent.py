"""
Main AI Agent for Suspicious Message Management
Coordinates decision-making and communication generation
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

from ..models.message import SuspiciousMessage
from ..models.actions import ActionPlan, ActionDecision, CommunicationContent
from ..decision_engine.decision_engine import DecisionEngine
from ..communication.message_generator import MessageGenerator
from ..utils.logger import setup_logger


class AIAgent:
    """
    Main AI Agent that processes suspicious messages and coordinates responses
    """
    
    def __init__(self, config: Dict[str, Any] = None, use_llm: bool = True):
        self.config = config or {}
        self.use_llm = use_llm
        self.logger = setup_logger("AIAgent")
        
        # Initialize components with LLM configuration
        self.decision_engine = DecisionEngine(
            self.config.get('decision_engine', {}), 
            use_llm=self.use_llm
        )
        self.message_generator = MessageGenerator(
            self.config.get('message_templates', {}), 
            use_llm=self.use_llm
        )
        
        self.logger.info(f"AI Agent initialized successfully (LLM: {'enabled' if self.use_llm else 'disabled'})")
    
    def process_suspicious_message(self, message: SuspiciousMessage) -> ActionPlan:
        """
        Main processing method for suspicious messages
        
        Args:
            message: The suspicious message to process
            
        Returns:
            ActionPlan containing all decisions and communications
        """
        self.logger.info(f"Processing suspicious message {message.message_id}")
        
        try:
            # Step 1: Analyze message and make decisions
            decisions = self.decision_engine.analyze_message(message)
            self.logger.info(f"Generated {len(decisions)} decisions for message {message.message_id}")
            
            # Step 2: Generate communications based on decisions
            communications = self.message_generator.generate_communications(message, decisions)
            self.logger.info(f"Generated {len(communications)} communications for message {message.message_id}")
            
            # Step 3: Create timeline for actions
            timeline = self._create_action_timeline(decisions)
            
            # Step 4: Determine follow-up requirements
            followup_required, followup_date = self._determine_followup(message, decisions)
            
            # Step 5: Create comprehensive action plan
            action_plan = ActionPlan(
                message_id=message.message_id,
                decisions=decisions,
                communications=communications,
                timeline=timeline,
                followup_required=followup_required,
                followup_date=followup_date
            )
            
            self.logger.info(f"Created action plan for message {message.message_id}")
            return action_plan
            
        except Exception as e:
            self.logger.error(f"Error processing message {message.message_id}: {str(e)}")
            raise
    
    def _create_action_timeline(self, decisions: List[ActionDecision]) -> Dict[str, datetime]:
        """Create timeline for executing actions based on priority"""
        timeline = {}
        now = datetime.now()
        
        for i, decision in enumerate(decisions):
            action_key = f"{decision.action_type.value}_{i}"
            
            if decision.priority.value == "immediate":
                timeline[action_key] = now
            elif decision.priority.value == "high":
                timeline[action_key] = now
            elif decision.priority.value == "medium":
                # Schedule within 1 hour
                timeline[action_key] = datetime.now().replace(
                    hour=min(23, now.hour + 1), minute=0, second=0, microsecond=0
                )
            else:  # low priority
                # Schedule within 24 hours
                timeline[action_key] = datetime.now().replace(
                    hour=9, minute=0, second=0, microsecond=0
                ) + (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days * 86400
        
        return timeline
    
    def _determine_followup(self, message: SuspiciousMessage, 
                          decisions: List[ActionDecision]) -> tuple[bool, datetime]:
        """Determine if follow-up is required and when"""
        
        # Check if any decision requires follow-up
        followup_actions = [d for d in decisions if d.action_type.value in [
            "schedule_followup", "educate_child", "provide_resources"
        ]]
        
        if not followup_actions:
            return False, None
        
        # Determine follow-up date based on severity and risk
        if message.severity.value in ["critical", "high"]:
            # Follow up in 3 days for high-risk situations
            followup_date = datetime.now().replace(
                hour=10, minute=0, second=0, microsecond=0
            ) + timedelta(days=3)
        else:
            # Follow up in 1 week for lower-risk situations
            followup_date = datetime.now().replace(
                hour=10, minute=0, second=0, microsecond=0
            ) + timedelta(weeks=1)
        
        return True, followup_date
    
    def get_action_summary(self, action_plan: ActionPlan) -> Dict[str, Any]:
        """Generate a summary of the action plan for reporting"""
        
        summary = {
            "message_id": action_plan.message_id,
            "total_actions": len(action_plan.decisions),
            "immediate_actions": len([d for d in action_plan.decisions 
                                    if d.priority.value == "immediate"]),
            "communications_generated": len(action_plan.communications),
            "recipients": list(set([c.recipient_type for c in action_plan.communications])),
            "followup_required": action_plan.followup_required,
            "followup_date": action_plan.followup_date.isoformat() if action_plan.followup_date else None,
            "action_types": [d.action_type.value for d in action_plan.decisions],
            "average_confidence": sum([d.confidence for d in action_plan.decisions]) / len(action_plan.decisions),
            "created_at": action_plan.created_at.isoformat()
        }
        
        return summary
    
    def validate_message(self, message: SuspiciousMessage) -> bool:
        """Validate that the message contains all required information"""
        
        required_fields = [
            message.message_id,
            message.content,
            message.threat_type,
            message.severity,
            message.child_profile,
            message.metadata
        ]
        
        if not all(required_fields):
            self.logger.error(f"Message {message.message_id} missing required fields")
            return False
        
        # Validate child profile
        if not all([
            message.child_profile.child_id,
            message.child_profile.age,
            message.child_profile.name
        ]):
            self.logger.error(f"Message {message.message_id} has incomplete child profile")
            return False
        
        # Validate metadata
        if not all([
            message.metadata.sender_id,
            message.metadata.platform,
            message.metadata.timestamp
        ]):
            self.logger.error(f"Message {message.message_id} has incomplete metadata")
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics for monitoring"""
        # This would typically connect to a database or metrics system
        return {
            "agent_status": "active",
            "last_processed": datetime.now().isoformat(),
            "components": {
                "decision_engine": "operational",
                "message_generator": "operational"
            }
        }


class AgentManager:
    """
    Manages multiple AI agents and coordinates their work
    """
    
    def __init__(self, config: Dict[str, Any] = None, use_llm: bool = True):
        self.config = config or {}
        self.use_llm = use_llm
        self.agents = {}
        self.logger = setup_logger("AgentManager")
        
        # Initialize default agent
        self.agents["default"] = AIAgent(self.config, use_llm=self.use_llm)
        
    def get_agent(self, agent_id: str = "default") -> AIAgent:
        """Get an agent by ID"""
        return self.agents.get(agent_id, self.agents["default"])
    
    def process_message_batch(self, messages: List[SuspiciousMessage]) -> List[ActionPlan]:
        """Process multiple messages efficiently"""
        action_plans = []
        
        for message in messages:
            try:
                agent = self.get_agent()
                if agent.validate_message(message):
                    plan = agent.process_suspicious_message(message)
                    action_plans.append(plan)
                else:
                    self.logger.warning(f"Skipping invalid message {message.message_id}")
            except Exception as e:
                self.logger.error(f"Error processing message {message.message_id}: {str(e)}")
                continue
        
        self.logger.info(f"Processed {len(action_plans)} messages successfully")
        return action_plans
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "active_agents": len(self.agents),
            "system_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
