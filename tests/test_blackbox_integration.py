"""
Unit tests for BlackBox LLM integration
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
from utils.blackbox_client import BlackBoxClient
from decision_engine.decision_engine import DecisionEngine
from communication.message_generator import MessageGenerator
from agents.ai_agent import AIAgent


class TestBlackBoxClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the API key to avoid requiring real credentials in tests
        self.api_key_patcher = patch.dict('os.environ', {'BLACKBOX_API_KEY': 'test_key'})
        self.api_key_patcher.start()
        
    def tearDown(self):
        """Clean up after tests"""
        self.api_key_patcher.stop()
    
    @patch('requests.post')
    def test_decision_reasoning_generation(self, mock_post):
        """Test decision reasoning generation"""
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is a high-risk situation requiring immediate action due to inappropriate contact with a minor.'
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = BlackBoxClient()
        
        reasoning = client.generate_decision_reasoning(
            message_content="Inappropriate message",
            threat_type="inappropriate_request",
            severity="high",
            child_age=12,
            context={"sender_type": "stranger"}
        )
        
        self.assertIsInstance(reasoning, str)
        self.assertGreater(len(reasoning), 0)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_parent_message_generation(self, mock_post):
        """Test parent message generation"""
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Subject: Safety Alert for Emma\n\nDear Parent, we detected an inappropriate request incident involving Emma...'
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = BlackBoxClient()
        
        result = client.generate_parent_message(
            child_name="Emma",
            threat_type="inappropriate_request",
            severity="high",
            action_taken="Sender blocked",
            tone="urgent"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)
        self.assertIn('message', result)
    
    @patch('requests.post')
    def test_child_message_generation(self, mock_post):
        """Test child message generation"""
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Subject: Hi Emma, let\'s talk about staying safe\n\nHi Emma, we want to help keep you safe online...'
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = BlackBoxClient()
        
        result = client.generate_child_message(
            child_name="Emma",
            child_age=12,
            threat_type="inappropriate_request",
            tone="supportive"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)
        self.assertIn('message', result)
    
    @patch('requests.post')
    def test_sender_warning_generation(self, mock_post):
        """Test sender warning generation"""
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Subject: Warning: Policy Violation\n\nYour recent communication violates our community guidelines...'
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = BlackBoxClient()
        
        result = client.generate_sender_warning(
            threat_type="inappropriate_request",
            platform="social_media"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)
        self.assertIn('message', result)
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key"""
        
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                BlackBoxClient()
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        
        # Mock API error
        mock_post.side_effect = Exception("API Error")
        
        client = BlackBoxClient()
        
        with self.assertRaises(Exception):
            client.generate_decision_reasoning(
                message_content="Test",
                threat_type="test",
                severity="medium",
                child_age=12,
                context={}
            )


class TestLLMIntegratedDecisionEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key_patcher = patch.dict('os.environ', {'BLACKBOX_API_KEY': 'test_key'})
        self.api_key_patcher.start()
        
        # Create sample message
        self.child_profile = ChildProfile(
            child_id="test_child",
            age=12,
            name="Test Child",
            previous_incidents=0
        )
        
        self.metadata = MessageMetadata(
            sender_id="test_sender",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=1,
            sender_history={},
            confidence_score=0.8
        )
        
        self.message = SuspiciousMessage(
            message_id="test_001",
            content="Test message",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.HIGH,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
    
    def tearDown(self):
        """Clean up after tests"""
        self.api_key_patcher.stop()
    
    def test_decision_engine_with_llm_enabled(self):
        """Test decision engine with LLM enabled"""
        
        with patch('src.utils.blackbox_client.BlackBoxClient') as mock_client_class:
            mock_client = Mock()
            mock_client.generate_decision_reasoning.return_value = "Enhanced LLM reasoning"
            mock_client_class.return_value = mock_client
            
            engine = DecisionEngine(use_llm=True)
            decisions = engine.analyze_message(self.message)
            
            self.assertGreater(len(decisions), 0)
            # Check that LLM reasoning was used
            self.assertTrue(any("Enhanced LLM reasoning" in d.reasoning for d in decisions))
    
    def test_decision_engine_with_llm_disabled(self):
        """Test decision engine with LLM disabled"""
        
        engine = DecisionEngine(use_llm=False)
        decisions = engine.analyze_message(self.message)
        
        self.assertGreater(len(decisions), 0)
        # Should use fallback reasoning
        self.assertTrue(all("Enhanced LLM reasoning" not in d.reasoning for d in decisions))
    
    def test_decision_engine_llm_fallback(self):
        """Test decision engine fallback when LLM fails"""
        
        with patch('src.utils.blackbox_client.BlackBoxClient') as mock_client_class:
            mock_client = Mock()
            mock_client.generate_decision_reasoning.side_effect = Exception("LLM Error")
            mock_client_class.return_value = mock_client
            
            engine = DecisionEngine(use_llm=True)
            decisions = engine.analyze_message(self.message)
            
            # Should still generate decisions using fallback
            self.assertGreater(len(decisions), 0)


class TestLLMIntegratedMessageGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key_patcher = patch.dict('os.environ', {'BLACKBOX_API_KEY': 'test_key'})
        self.api_key_patcher.start()
        
        # Create sample message and decision
        self.child_profile = ChildProfile(
            child_id="test_child",
            age=12,
            name="Test Child",
            previous_incidents=0
        )
        
        self.metadata = MessageMetadata(
            sender_id="test_sender",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=1,
            sender_history={},
            confidence_score=0.8
        )
        
        self.message = SuspiciousMessage(
            message_id="test_001",
            content="Test message",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.HIGH,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
    
    def tearDown(self):
        """Clean up after tests"""
        self.api_key_patcher.stop()
    
    def test_message_generator_with_llm_enabled(self):
        """Test message generator with LLM enabled"""
        
        with patch('src.utils.blackbox_client.BlackBoxClient') as mock_client_class:
            mock_client = Mock()
            mock_client.generate_parent_message.return_value = {
                "subject": "LLM Generated Subject",
                "message": "LLM Generated Message"
            }
            mock_client_class.return_value = mock_client
            
            generator = MessageGenerator(use_llm=True)
            
            # Create a mock decision
            from models.actions import ActionDecision, ActionType, ActionPriority
            decision = ActionDecision(
                action_type=ActionType.NOTIFY_PARENT,
                priority=ActionPriority.HIGH,
                reasoning="Test reasoning",
                confidence=0.8,
                target_audience=["parent"],
                estimated_impact="Test impact"
            )
            
            comm = generator._generate_parent_communication(self.message, decision)
            
            self.assertEqual(comm.subject, "LLM Generated Subject")
            self.assertEqual(comm.message, "LLM Generated Message")
    
    def test_message_generator_with_llm_disabled(self):
        """Test message generator with LLM disabled"""
        
        generator = MessageGenerator(use_llm=False)
        
        # Create a mock decision
        from models.actions import ActionDecision, ActionType, ActionPriority
        decision = ActionDecision(
            action_type=ActionType.NOTIFY_PARENT,
            priority=ActionPriority.HIGH,
            reasoning="Test reasoning",
            confidence=0.8,
            target_audience=["parent"],
            estimated_impact="Test impact"
        )
        
        comm = generator._generate_parent_communication(self.message, decision)
        
        # Should use template-based generation
        self.assertIsNotNone(comm.subject)
        self.assertIsNotNone(comm.message)
        self.assertNotEqual(comm.subject, "LLM Generated Subject")


class TestLLMIntegratedAIAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key_patcher = patch.dict('os.environ', {'BLACKBOX_API_KEY': 'test_key'})
        self.api_key_patcher.start()
        
        # Create sample message
        self.child_profile = ChildProfile(
            child_id="test_child",
            age=12,
            name="Test Child",
            previous_incidents=0
        )
        
        self.metadata = MessageMetadata(
            sender_id="test_sender",
            sender_type="stranger",
            platform="social_media",
            timestamp=datetime.now(),
            message_frequency=1,
            sender_history={},
            confidence_score=0.8
        )
        
        self.message = SuspiciousMessage(
            message_id="test_001",
            content="Test message",
            threat_type=ThreatType.BULLYING,
            severity=SeverityLevel.HIGH,
            child_profile=self.child_profile,
            metadata=self.metadata
        )
    
    def tearDown(self):
        """Clean up after tests"""
        self.api_key_patcher.stop()
    
    def test_ai_agent_with_llm_enabled(self):
        """Test AI agent with LLM enabled"""
        
        with patch('src.utils.blackbox_client.BlackBoxClient'):
            agent = AIAgent(use_llm=True)
            
            self.assertTrue(agent.use_llm)
            self.assertTrue(agent.decision_engine.use_llm)
            self.assertTrue(agent.message_generator.use_llm)
    
    def test_ai_agent_with_llm_disabled(self):
        """Test AI agent with LLM disabled"""
        
        agent = AIAgent(use_llm=False)
        
        self.assertFalse(agent.use_llm)
        self.assertFalse(agent.decision_engine.use_llm)
        self.assertFalse(agent.message_generator.use_llm)
    
    def test_ai_agent_processing_with_llm(self):
        """Test full message processing with LLM integration"""
        
        with patch('src.utils.blackbox_client.BlackBoxClient') as mock_client_class:
            mock_client = Mock()
            mock_client.generate_decision_reasoning.return_value = "LLM reasoning"
            mock_client.generate_parent_message.return_value = {
                "subject": "LLM Subject",
                "message": "LLM Message"
            }
            mock_client_class.return_value = mock_client
            
            agent = AIAgent(use_llm=True)
            action_plan = agent.process_suspicious_message(self.message)
            
            # Should generate action plan successfully
            self.assertIsNotNone(action_plan)
            self.assertGreater(len(action_plan.decisions), 0)
            self.assertGreater(len(action_plan.communications), 0)


if __name__ == '__main__':
    unittest.main()
