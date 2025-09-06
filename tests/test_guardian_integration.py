"""
Unit tests for Guardian Layer integration
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from integrations.guardian_integration import GuardianIntegration, convert_guardian_to_kidshield
from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel


class TestGuardianIntegration(unittest.TestCase):
    """Test Guardian Layer integration functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.integration = GuardianIntegration()
        
        # Sample Guardian response
        self.sample_guardian_response = {
            "input_id": "test-uuid-123",
            "results": {
                "text_risk": [
                    {"category": "sexual", "score": 0.88},
                    {"category": "grooming", "score": 0.75},
                    {"category": "bullying", "score": 0.15}
                ],
                "image_risk": [
                    {"category": "nudity", "score": 0.91}
                ]
            },
            "status": "flagged",
            "timestamp": "2024-01-15T10:30:00Z",
            "processing_time": 0.45
        }
        
        self.sample_content = "Hey, you're really cute. Want to meet up somewhere private?"
        
        self.sample_child_profile = ChildProfile(
            child_id="child_123",
            age=12,
            name="Emma",
            grade_level="7th",
            previous_incidents=0
        )
    
    def test_convert_guardian_response_basic(self):
        """Test basic Guardian response conversion"""
        
        result = self.integration.convert_guardian_response(
            self.sample_guardian_response,
            self.sample_content,
            self.sample_child_profile
        )
        
        # Verify result is SuspiciousMessage
        self.assertIsInstance(result, SuspiciousMessage)
        
        # Verify basic fields
        self.assertEqual(result.message_id, "test-uuid-123")
        self.assertEqual(result.content, self.sample_content)
        self.assertEqual(result.child_profile, self.sample_child_profile)
        
        # Verify threat type mapping (highest score should be nudity -> sexual_content)
        self.assertEqual(result.threat_type, ThreatType.SEXUAL_CONTENT)
        
        # Verify severity mapping (0.91 score should be CRITICAL)
        self.assertEqual(result.severity, SeverityLevel.CRITICAL)
    
    def test_threat_type_mapping(self):
        """Test threat type mapping from Guardian categories"""
        
        test_cases = [
            ({"category": "bullying", "score": 0.8}, ThreatType.BULLYING),
            ({"category": "sexual", "score": 0.9}, ThreatType.SEXUAL_CONTENT),
            ({"category": "grooming", "score": 0.7}, ThreatType.MANIPULATION),
            ({"category": "hate_speech", "score": 0.6}, ThreatType.HARASSMENT),
            ({"category": "violence", "score": 0.8}, ThreatType.VIOLENT_CONTENT),
            ({"category": "nudity", "score": 0.9}, ThreatType.SEXUAL_CONTENT),
            ({"category": "weapons", "score": 0.7}, ThreatType.VIOLENT_CONTENT),
            ({"category": "unknown_category", "score": 0.5}, ThreatType.OTHER)
        ]
        
        for risk_data, expected_threat in test_cases:
            guardian_response = {
                "input_id": "test-id",
                "results": {
                    "text_risk": [risk_data],
                    "image_risk": []
                },
                "status": "flagged",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time": 0.1
            }
            
            result = self.integration.convert_guardian_response(
                guardian_response,
                "test content"
            )
            
            self.assertEqual(result.threat_type, expected_threat)
    
    def test_severity_mapping(self):
        """Test severity level mapping from Guardian scores"""
        
        test_cases = [
            (0.95, SeverityLevel.CRITICAL),
            (0.85, SeverityLevel.HIGH),
            (0.65, SeverityLevel.MEDIUM),
            (0.35, SeverityLevel.LOW),
            (0.05, SeverityLevel.LOW)
        ]
        
        for score, expected_severity in test_cases:
            guardian_response = {
                "input_id": "test-id",
                "results": {
                    "text_risk": [{"category": "bullying", "score": score}],
                    "image_risk": []
                },
                "status": "flagged",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time": 0.1
            }
            
            result = self.integration.convert_guardian_response(
                guardian_response,
                "test content"
            )
            
            self.assertEqual(result.severity, expected_severity)
    
    def test_context_creation(self):
        """Test context creation with Guardian analysis details"""
        
        result = self.integration.convert_guardian_response(
            self.sample_guardian_response,
            self.sample_content
        )
        
        # Verify context structure
        self.assertIn("guardian_analysis", result.context)
        self.assertIn("risk_breakdown", result.context)
        self.assertIn("integration_metadata", result.context)
        
        # Verify Guardian analysis details
        guardian_analysis = result.context["guardian_analysis"]
        self.assertEqual(guardian_analysis["input_id"], "test-uuid-123")
        self.assertEqual(guardian_analysis["status"], "flagged")
        self.assertEqual(guardian_analysis["processing_time"], 0.45)
        
        # Verify risk breakdown
        risk_breakdown = result.context["risk_breakdown"]
        self.assertEqual(len(risk_breakdown["text_risks"]), 3)
        self.assertEqual(len(risk_breakdown["image_risks"]), 1)
        self.assertEqual(risk_breakdown["total_risks"], 4)
        self.assertEqual(risk_breakdown["max_risk_score"], 0.91)
    
    def test_default_child_profile_creation(self):
        """Test default child profile creation when none provided"""
        
        result = self.integration.convert_guardian_response(
            self.sample_guardian_response,
            self.sample_content
        )
        
        # Verify default child profile
        self.assertEqual(result.child_profile.child_id, "unknown_child")
        self.assertEqual(result.child_profile.age, 12)
        self.assertEqual(result.child_profile.name, "Unknown Child")
        self.assertTrue(result.child_profile.parental_notification_preferences["immediate_notification"])
    
    def test_metadata_creation(self):
        """Test metadata creation from Guardian response"""
        
        additional_metadata = {
            "sender_id": "test_sender_123",
            "sender_type": "stranger",
            "platform": "social_media",
            "message_frequency": 3
        }
        
        result = self.integration.convert_guardian_response(
            self.sample_guardian_response,
            self.sample_content,
            additional_metadata=additional_metadata
        )
        
        # Verify metadata fields
        self.assertEqual(result.metadata.sender_id, "test_sender_123")
        self.assertEqual(result.metadata.sender_type, "stranger")
        self.assertEqual(result.metadata.platform, "social_media")
        self.assertEqual(result.metadata.message_frequency, 3)
        
        # Verify confidence score adjustment for flagged content
        self.assertGreater(result.metadata.confidence_score, 0.5)
    
    def test_batch_conversion(self):
        """Test batch conversion of multiple Guardian responses"""
        
        guardian_responses = [
            self.sample_guardian_response,
            {
                "input_id": "test-uuid-456",
                "results": {
                    "text_risk": [{"category": "bullying", "score": 0.6}],
                    "image_risk": []
                },
                "status": "flagged",
                "timestamp": "2024-01-15T11:00:00Z",
                "processing_time": 0.2
            }
        ]
        
        original_contents = [
            self.sample_content,
            "You're so stupid and ugly"
        ]
        
        results = self.integration.batch_convert(guardian_responses, original_contents)
        
        # Verify batch results
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], SuspiciousMessage)
        self.assertIsInstance(results[1], SuspiciousMessage)
        
        # Verify individual conversions
        self.assertEqual(results[0].message_id, "test-uuid-123")
        self.assertEqual(results[1].message_id, "test-uuid-456")
        self.assertEqual(results[1].threat_type, ThreatType.BULLYING)
    
    def test_validation(self):
        """Test Guardian response validation"""
        
        # Valid response
        valid_response = self.sample_guardian_response
        self.assertTrue(self.integration.validate_guardian_response(valid_response))
        
        # Invalid responses
        invalid_responses = [
            {},  # Empty dict
            {"input_id": "test"},  # Missing required fields
            {"results": {}},  # Missing input_id
            None  # None value
        ]
        
        for invalid_response in invalid_responses:
            self.assertFalse(self.integration.validate_guardian_response(invalid_response))
    
    def test_risk_summary(self):
        """Test risk summary generation"""
        
        summary = self.integration.get_risk_summary(self.sample_guardian_response)
        
        # Verify summary structure
        self.assertEqual(summary["total_risks"], 4)
        self.assertEqual(summary["max_score"], 0.91)
        self.assertEqual(summary["text_risk_count"], 3)
        self.assertEqual(summary["image_risk_count"], 1)
        self.assertIn("sexual", summary["categories"])
        self.assertIn("nudity", summary["categories"])
    
    def test_convenience_function(self):
        """Test convenience function for direct conversion"""
        
        result = convert_guardian_to_kidshield(
            self.sample_guardian_response,
            self.sample_content,
            self.sample_child_profile
        )
        
        # Verify result
        self.assertIsInstance(result, SuspiciousMessage)
        self.assertEqual(result.message_id, "test-uuid-123")
        self.assertEqual(result.content, self.sample_content)
        self.assertEqual(result.child_profile, self.sample_child_profile)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        
        # Test with malformed Guardian response
        malformed_response = {
            "input_id": "test",
            "results": "invalid_results_format"
        }
        
        with self.assertRaises(ValueError):
            self.integration.convert_guardian_response(
                malformed_response,
                self.sample_content
            )
    
    def test_empty_risks_handling(self):
        """Test handling of Guardian response with no risks"""
        
        empty_risk_response = {
            "input_id": "test-safe-123",
            "results": {
                "text_risk": [],
                "image_risk": []
            },
            "status": "safe",
            "timestamp": "2024-01-15T10:30:00Z",
            "processing_time": 0.1
        }
        
        result = self.integration.convert_guardian_response(
            empty_risk_response,
            "Hello, how are you?"
        )
        
        # Verify safe content handling
        self.assertEqual(result.threat_type, ThreatType.OTHER)
        self.assertEqual(result.severity, SeverityLevel.LOW)
        self.assertEqual(result.context["risk_breakdown"]["total_risks"], 0)


if __name__ == '__main__':
    unittest.main()
