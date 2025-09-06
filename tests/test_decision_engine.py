"""
Unit tests for the Decision Engine
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
from models.actions import ActionType, ActionPriority
from decision_engine.decision_engine import DecisionEngine


class TestDecisionEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.decision_engine = DecisionEngine()
        
        # Create a sample child profile
        self.child_profile = ChildProfile(
            child_id="test_child_123",
            age=12,
            name="Test Child",
            grade_level="7th",
            previous_incidents=0
        )
        
        # Create sample metadata
        self.metadata = MessageMetadata(
            sender_id="test_sender_456",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=1,
            sender_history={},
            confidence_score=0.8
        )
    
    def test_high_risk_sexual_content(self):
        """Test decision making for high-risk sexual content"""
        message = SuspiciousMessage(
            message_id="test_001",
            content="Inappropriate sexual content",
            threat_type=ThreatType.SEXUAL_CONTENT,
            severity=SeverityLevel.CRITICAL,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        decisions = self.decision_engine.analyze_message(message)
        
        # Should have multiple decisions
        self.assertGreater(len(decisions), 0)
        
        # Should include blocking sender
        action_types = [d.action_type for d in decisions]
        self.assertIn(ActionType.BLOCK_SENDER, action_types)
        
        # Should notify parent immediately
        self.assertIn(ActionType.NOTIFY_PARENT, action_types)
        
        # Should escalate to authorities
        self.assertIn(ActionType.ESCALATE_TO_AUTHORITIES, action_types)
    
    def test_medium_risk_bullying(self):
        """Test decision making for medium-risk bullying"""
        message = SuspiciousMessage(
            message_id="test_002",
            content="You're stupid and nobody likes you",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.MEDIUM,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        decisions = self.decision_engine.analyze_message(message)
        
        action_types = [d.action_type for d in decisions]
        
        # Should warn sender for medium risk
        self.assertIn(ActionType.WARN_SENDER, action_types)
        
        # Should notify parent
        self.assertIn(ActionType.NOTIFY_PARENT, action_types)
        
        # Should provide education
        self.assertIn(ActionType.EDUCATE_CHILD, action_types)
    
    def test_age_appropriate_responses(self):
        """Test that responses are age-appropriate"""
        
        # Test with young child (8 years old)
        young_child = ChildProfile(
            child_id="young_child",
            age=8,
            name="Young Child",
            previous_incidents=0
        )
        
        message_young = SuspiciousMessage(
            message_id="test_young",
            content="Stranger contact",
            threat_type=ThreatType.STRANGER_CONTACT,
            severity=SeverityLevel.MEDIUM,
            child_profile=young_child,
            metadata=self.metadata
        )
        
        decisions_young = self.decision_engine.analyze_message(message_young)
        
        # Test with teenager (16 years old)
        teen_child = ChildProfile(
            child_id="teen_child",
            age=16,
            name="Teen Child",
            previous_incidents=0
        )
        
        message_teen = SuspiciousMessage(
            message_id="test_teen",
            content="Stranger contact",
            threat_type=ThreatType.STRANGER_CONTACT,
            severity=SeverityLevel.MEDIUM,
            child_profile=teen_child,
            metadata=self.metadata
        )
        
        decisions_teen = self.decision_engine.analyze_message(message_teen)
        
        # Both should have decisions, but may differ in approach
        self.assertGreater(len(decisions_young), 0)
        self.assertGreater(len(decisions_teen), 0)
    
    def test_risk_score_calculation(self):
        """Test risk score calculation"""
        
        # High severity, high-risk threat type
        high_risk_message = SuspiciousMessage(
            message_id="high_risk",
            content="High risk content",
            threat_type=ThreatType.SEXUAL_CONTENT,
            severity=SeverityLevel.CRITICAL,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        high_risk_score = self.decision_engine._calculate_risk_score(high_risk_message)
        
        # Low severity, low-risk threat type
        low_risk_message = SuspiciousMessage(
            message_id="low_risk",
            content="Low risk content",
            threat_type=ThreatType.OTHER,
            severity=SeverityLevel.LOW,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        low_risk_score = self.decision_engine._calculate_risk_score(low_risk_message)
        
        # High risk should have higher score
        self.assertGreater(high_risk_score, low_risk_score)
        
        # Scores should be between 0 and 1
        self.assertGreaterEqual(high_risk_score, 0.0)
        self.assertLessEqual(high_risk_score, 1.0)
        self.assertGreaterEqual(low_risk_score, 0.0)
        self.assertLessEqual(low_risk_score, 1.0)
    
    def test_repeat_offender_handling(self):
        """Test handling of repeat offenders"""
        
        # Create metadata with repeat offender history
        repeat_metadata = MessageMetadata(
            sender_id="repeat_sender",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=5,
            sender_history={"previous_reports": 3},
            confidence_score=0.8
        )
        
        message = SuspiciousMessage(
            message_id="repeat_test",
            content="Repeat offense",
            threat_type=ThreatType.HARASSMENT,
            severity=SeverityLevel.MEDIUM,
            child_profile=self.child_profile,
            metadata=repeat_metadata
        )
        
        decisions = self.decision_engine.analyze_message(message)
        action_types = [d.action_type for d in decisions]
        
        # Should escalate due to repeat offenses
        self.assertIn(ActionType.ESCALATE_TO_AUTHORITIES, action_types)
    
    def test_decision_confidence_levels(self):
        """Test that decisions have appropriate confidence levels"""
        
        message = SuspiciousMessage(
            message_id="confidence_test",
            content="Test message",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.HIGH,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
        
        decisions = self.decision_engine.analyze_message(message)
        
        # All decisions should have confidence between 0 and 1
        for decision in decisions:
            self.assertGreaterEqual(decision.confidence, 0.0)
            self.assertLessEqual(decision.confidence, 1.0)
    
    def test_age_group_classification(self):
        """Test age group classification"""
        
        # Test different ages
        test_cases = [
            (7, "young_child"),
            (12, "pre_teen"),
            (15, "teenager"),
            (19, "young_adult")
        ]
        
        for age, expected_group in test_cases:
            group = self.decision_engine.get_age_group(age)
            self.assertEqual(group, expected_group)


if __name__ == '__main__':
    unittest.main()
