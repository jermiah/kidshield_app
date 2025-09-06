"""
Unit tests for the AI Agent
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
from models.actions import ActionType
from agents.ai_agent import AIAgent, AgentManager


class TestAIAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = AIAgent()
        
        # Create a sample message
        self.child_profile = ChildProfile(
            child_id="test_child_123",
            age=12,
            name="Test Child",
            grade_level="7th",
            previous_incidents=0
        )
        
        self.metadata = MessageMetadata(
            sender_id="test_sender_456",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=1,
            sender_history={},
            confidence_score=0.8
        )
        
        self.sample_message = SuspiciousMessage(
            message_id="test_001",
            content="Test suspicious content",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.MEDIUM,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
    
    def test_message_validation_valid(self):
        """Test validation of valid message"""
        result = self.agent.validate_message(self.sample_message)
        self.assertTrue(result)
    
    def test_message_validation_invalid(self):
        """Test validation of invalid message"""
        # Create message with missing required field
        invalid_message = SuspiciousMessage(
            message_id="",  # Empty message ID
            content="Test content",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.MEDIUM,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        result = self.agent.validate_message(invalid_message)
        self.assertFalse(result)
    
    def test_process_suspicious_message(self):
        """Test processing of suspicious message"""
        action_plan = self.agent.process_suspicious_message(self.sample_message)
        
        # Should return an ActionPlan
        self.assertIsNotNone(action_plan)
        self.assertEqual(action_plan.message_id, self.sample_message.message_id)
        
        # Should have decisions
        self.assertGreater(len(action_plan.decisions), 0)
        
        # Should have communications
        self.assertGreater(len(action_plan.communications), 0)
        
        # Should have timeline
        self.assertGreater(len(action_plan.timeline), 0)
    
    def test_action_timeline_creation(self):
        """Test creation of action timeline"""
        action_plan = self.agent.process_suspicious_message(self.sample_message)
        
        # Timeline should have entries
        self.assertGreater(len(action_plan.timeline), 0)
        
        # All timeline entries should be datetime objects
        for timestamp in action_plan.timeline.values():
            self.assertIsInstance(timestamp, datetime)
    
    def test_followup_determination(self):
        """Test follow-up determination logic"""
        
        # Test high-severity message (should require follow-up)
        high_severity_message = SuspiciousMessage(
            message_id="high_severity_test",
            content="High severity content",
            threat_type=ThreatType.SEXUAL_CONTENT,
            severity=SeverityLevel.CRITICAL,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        action_plan = self.agent.process_suspicious_message(high_severity_message)
        self.assertTrue(action_plan.followup_required)
        self.assertIsNotNone(action_plan.followup_date)
    
    def test_action_summary_generation(self):
        """Test action summary generation"""
        action_plan = self.agent.process_suspicious_message(self.sample_message)
        summary = self.agent.get_action_summary(action_plan)
        
        # Should contain expected fields
        expected_fields = [
            'message_id', 'total_actions', 'immediate_actions',
            'communications_generated', 'recipients', 'followup_required',
            'action_types', 'average_confidence', 'created_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, summary)
        
        # Values should be reasonable
        self.assertEqual(summary['message_id'], self.sample_message.message_id)
        self.assertGreaterEqual(summary['total_actions'], 0)
        self.assertGreaterEqual(summary['communications_generated'], 0)
        self.assertGreaterEqual(summary['average_confidence'], 0.0)
        self.assertLessEqual(summary['average_confidence'], 1.0)
    
    def test_agent_statistics(self):
        """Test agent statistics retrieval"""
        stats = self.agent.get_statistics()
        
        # Should contain expected fields
        expected_fields = ['agent_status', 'last_processed', 'components']
        for field in expected_fields:
            self.assertIn(field, stats)
        
        # Status should be active
        self.assertEqual(stats['agent_status'], 'active')


class TestAgentManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = AgentManager()
        
        # Create sample messages
        self.messages = []
        for i in range(3):
            child_profile = ChildProfile(
                child_id=f"child_{i}",
                age=10 + i,
                name=f"Child {i}",
                previous_incidents=0
            )
            
            metadata = MessageMetadata(
                sender_id=f"sender_{i}",
                sender_type="stranger",
                platform="social_media",
                timestamp=datetime.now(),
                message_frequency=1,
                sender_history={},
                confidence_score=0.7 + i * 0.1
            )
            
            message = SuspiciousMessage(
                message_id=f"msg_{i}",
                content=f"Test message {i}",
                threat_type=ThreatType.BULLYING,
                severity=SeverityLevel.MEDIUM,
                child_profile=child_profile,
                metadata=metadata
            )
            
            self.messages.append(message)
    
    def test_get_default_agent(self):
        """Test getting default agent"""
        agent = self.manager.get_agent()
        self.assertIsInstance(agent, AIAgent)
    
    def test_get_specific_agent(self):
        """Test getting specific agent"""
        agent = self.manager.get_agent("default")
        self.assertIsInstance(agent, AIAgent)
    
    def test_batch_processing(self):
        """Test batch processing of messages"""
        action_plans = self.manager.process_message_batch(self.messages)
        
        # Should process all valid messages
        self.assertEqual(len(action_plans), len(self.messages))
        
        # Each action plan should be valid
        for plan in action_plans:
            self.assertIsNotNone(plan.message_id)
            self.assertGreater(len(plan.decisions), 0)
    
    def test_batch_processing_with_invalid_message(self):
        """Test batch processing with some invalid messages"""
        
        # Add an invalid message
        invalid_message = SuspiciousMessage(
            message_id="",  # Invalid empty ID
            content="Invalid message",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.MEDIUM,
            child_profile=self.messages[0].child_profile,
            metadata=self.messages[0].metadata
        )
        
        mixed_messages = self.messages + [invalid_message]
        action_plans = self.manager.process_message_batch(mixed_messages)
        
        # Should only process valid messages
        self.assertEqual(len(action_plans), len(self.messages))
    
    def test_system_status(self):
        """Test system status retrieval"""
        status = self.manager.get_system_status()
        
        expected_fields = ['active_agents', 'system_status', 'timestamp']
        for field in expected_fields:
            self.assertIn(field, status)
        
        self.assertGreater(status['active_agents'], 0)
        self.assertEqual(status['system_status'], 'operational')


if __name__ == '__main__':
    unittest.main()
