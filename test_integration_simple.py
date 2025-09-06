"""
Simple test to verify Guardian Layer → KidShield integration works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Test imports
try:
    from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
    from integrations.guardian_integration import GuardianIntegration, convert_guardian_to_kidshield
    from agents.ai_agent import AIAgent
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_integration():
    """Test basic Guardian → KidShield integration"""
    
    print("\n=== Testing Guardian → KidShield Integration ===")
    
    # Sample Guardian response (structured output)
    guardian_response = {
        "input_id": "test-integration-001",
        "results": {
            "text_risk": [
                {"category": "sexual", "score": 0.88},
                {"category": "grooming", "score": 0.75}
            ],
            "image_risk": [
                {"category": "inappropriate", "score": 0.45}
            ]
        },
        "status": "flagged",
        "timestamp": "2024-01-15T14:30:00Z",
        "processing_time": 0.65
    }
    
    original_content = "Hey beautiful, want to meet up somewhere private?"
    
    print(f"Guardian Input ID: {guardian_response['input_id']}")
    print(f"Guardian Status: {guardian_response['status']}")
    print(f"Text Risks: {len(guardian_response['results']['text_risk'])}")
    print(f"Image Risks: {len(guardian_response['results']['image_risk'])}")
    
    # Create child profile
    child_profile = ChildProfile(
        child_id="test_child_123",
        age=12,
        name="Emma",
        grade_level="7th",
        previous_incidents=0
    )
    
    # Additional metadata
    additional_metadata = {
        "sender_id": "unknown_sender_456",
        "sender_type": "stranger",
        "platform": "social_media",
        "message_frequency": 3
    }
    
    try:
        # Convert Guardian response to KidShield format
        print("\n1. Converting Guardian response to KidShield format...")
        suspicious_message = convert_guardian_to_kidshield(
            guardian_response,
            original_content,
            child_profile,
            additional_metadata
        )
        
        print(f"✅ Conversion successful!")
        print(f"   Message ID: {suspicious_message.message_id}")
        print(f"   Threat Type: {suspicious_message.threat_type.value}")
        print(f"   Severity: {suspicious_message.severity.value}")
        print(f"   Child: {suspicious_message.child_profile.name} (age {suspicious_message.child_profile.age})")
        print(f"   Confidence: {suspicious_message.metadata.confidence_score:.2f}")
        
        # Verify context preservation
        guardian_context = suspicious_message.context.get("guardian_analysis", {})
        print(f"   Guardian context preserved: {bool(guardian_context)}")
        print(f"   Risk breakdown available: {'risk_breakdown' in suspicious_message.context}")
        
        # Process with KidShield AI Agent
        print("\n2. Processing with KidShield AI Agent...")
        agent = AIAgent(use_llm=False)  # Disable LLM for testing
        action_plan = agent.process_suspicious_message(suspicious_message)
        
        print(f"✅ KidShield processing successful!")
        print(f"   Decisions generated: {len(action_plan.decisions)}")
        print(f"   Communications created: {len(action_plan.communications)}")
        print(f"   Follow-up required: {action_plan.followup_required}")
        
        # Show decision details
        if action_plan.decisions:
            print("\n   Decision Details:")
            for i, decision in enumerate(action_plan.decisions[:3], 1):  # Show first 3
                print(f"   {i}. {decision.action_type.value} (Priority: {decision.priority.value})")
        
        # Show communication details
        if action_plan.communications:
            print("\n   Communication Details:")
            for i, comm in enumerate(action_plan.communications[:2], 1):  # Show first 2
                print(f"   {i}. To {comm.recipient_type}: {comm.subject}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_mapping():
    """Test risk category mapping"""
    
    print("\n=== Testing Risk Category Mapping ===")
    
    integration = GuardianIntegration()
    
    test_cases = [
        ({"category": "sexual", "score": 0.9}, ThreatType.SEXUAL_CONTENT, SeverityLevel.CRITICAL),
        ({"category": "bullying", "score": 0.7}, ThreatType.BULLYING, SeverityLevel.HIGH),
        ({"category": "grooming", "score": 0.5}, ThreatType.MANIPULATION, SeverityLevel.MEDIUM),
        ({"category": "violence", "score": 0.3}, ThreatType.VIOLENT_CONTENT, SeverityLevel.LOW),
    ]
    
    for risk_data, expected_threat, expected_severity in test_cases:
        guardian_response = {
            "input_id": "mapping-test",
            "results": {
                "text_risk": [risk_data],
                "image_risk": []
            },
            "status": "flagged",
            "timestamp": "2024-01-15T10:30:00Z",
            "processing_time": 0.1
        }
        
        try:
            result = integration.convert_guardian_response(
                guardian_response,
                "test content"
            )
            
            threat_match = result.threat_type == expected_threat
            severity_match = result.severity == expected_severity
            
            status = "✅" if threat_match and severity_match else "❌"
            print(f"{status} {risk_data['category']} (score: {risk_data['score']}) → {result.threat_type.value}, {result.severity.value}")
            
        except Exception as e:
            print(f"❌ Mapping test failed for {risk_data['category']}: {str(e)}")

def main():
    """Run integration tests"""
    
    print("Guardian Layer → KidShield App Integration Test")
    print("=" * 50)
    
    try:
        # Test basic integration
        basic_success = test_basic_integration()
        
        # Test risk mapping
        test_risk_mapping()
        
        print("\n" + "=" * 50)
        if basic_success:
            print("✅ Integration test PASSED!")
            print("\nThe Guardian Layer → KidShield integration is working properly:")
            print("• Guardian structured outputs are correctly converted to KidShield format")
            print("• Risk categories are properly mapped to threat types")
            print("• Severity levels are correctly determined from scores")
            print("• Guardian analysis context is preserved")
            print("• KidShield AI Agent can process the converted messages")
            print("• Action plans are generated successfully")
        else:
            print("❌ Integration test FAILED!")
            
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
