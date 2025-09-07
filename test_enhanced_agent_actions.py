#!/usr/bin/env python3
"""
Test script to verify that the enhanced agent layer always generates
the 3 required actions: alert parents, educate child, and warn sender
"""

import sys
from pathlib import Path
from datetime import datetime

# Add agent_layer to path
agent_path = Path(__file__).parent / "agent_layer"
sys.path.append(str(agent_path))

from agent_layer.agents.ai_agent import AIAgent
from agent_layer.models.message import SuspiciousMessage, ThreatType, SeverityLevel, ChildProfile, MessageMetadata
from agent_layer.models.actions import ActionType


def create_test_message(threat_type: ThreatType, severity: SeverityLevel, child_age: int = 12) -> SuspiciousMessage:
    """Create a test suspicious message"""
    
    child_profile = ChildProfile(
        child_id="test_child_001",
        name="Test Child",
        age=child_age,
        previous_incidents=0,
        parental_notification_preferences={
            "immediate_notification": True,
            "email": "parent@example.com"
        }
    )
    
    metadata = MessageMetadata(
        sender_id="test_sender_001",
        platform="test_platform",
        timestamp=datetime.now(),
        sender_type="unknown",
        sender_history={},
        message_frequency=1
    )
    
    return SuspiciousMessage(
        message_id=f"test_msg_{datetime.now().timestamp()}",
        content="This is a test suspicious message",
        threat_type=threat_type,
        severity=severity,
        child_profile=child_profile,
        metadata=metadata
    )


def test_required_actions():
    """Test that the agent always generates the 3 required actions when risks are detected"""
    
    print("🧪 Testing Enhanced Agent Layer - Required Actions")
    print("=" * 60)
    
    # Initialize agent (without LLM for faster testing)
    agent = AIAgent(use_llm=False)
    
    # Test scenarios with different threat types and severities
    test_scenarios = [
        (ThreatType.BULLYING, SeverityLevel.MEDIUM),
        (ThreatType.SEXUAL_CONTENT, SeverityLevel.HIGH),
        (ThreatType.STRANGER_CONTACT, SeverityLevel.LOW),
        (ThreatType.INAPPROPRIATE_REQUEST, SeverityLevel.CRITICAL),
        (ThreatType.HARASSMENT, SeverityLevel.HIGH)
    ]
    
    required_actions = {
        ActionType.NOTIFY_PARENT,
        ActionType.EDUCATE_CHILD,
        ActionType.WARN_SENDER
    }
    
    all_tests_passed = True
    
    for i, (threat_type, severity) in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {threat_type.value} - {severity.value}")
        print("-" * 40)
        
        # Create test message
        message = create_test_message(threat_type, severity)
        
        # Process message
        try:
            action_plan = agent.process_suspicious_message(message)
            
            # Check if all required actions are present
            generated_actions = {decision.action_type for decision in action_plan.decisions}
            
            print(f"Generated actions: {[action.value for action in generated_actions]}")
            
            # Verify all required actions are present
            missing_actions = required_actions - generated_actions
            
            if missing_actions:
                print(f"❌ FAILED: Missing required actions: {[action.value for action in missing_actions]}")
                all_tests_passed = False
            else:
                print("✅ PASSED: All required actions generated")
                
                # Show action details
                for decision in action_plan.decisions:
                    if decision.action_type in required_actions:
                        print(f"   • {decision.action_type.value}: {decision.priority.value} priority")
            
            # Check communications
            communications = action_plan.communications
            comm_types = {comm.recipient_type for comm in communications}
            print(f"Communications generated for: {list(comm_types)}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Agent always generates required actions.")
    else:
        print("❌ SOME TESTS FAILED! Check the implementation.")
    
    return all_tests_passed


def test_sender_warning_content():
    """Test that sender warnings reference threat classification"""
    
    print("\n🔍 Testing Sender Warning Content")
    print("=" * 60)
    
    agent = AIAgent(use_llm=False)
    message = create_test_message(ThreatType.BULLYING, SeverityLevel.HIGH)
    
    try:
        action_plan = agent.process_suspicious_message(message)
        
        # Find sender communication
        sender_comms = [comm for comm in action_plan.communications if comm.recipient_type == "sender"]
        
        if sender_comms:
            sender_comm = sender_comms[0]
            print(f"📧 Sender Warning Subject: {sender_comm.subject}")
            print(f"📝 Message Preview: {sender_comm.message[:200]}...")
            
            # Check if threat classification is referenced
            threat_name = message.threat_type.value.replace('_', ' ').title()
            if threat_name.lower() in sender_comm.message.lower() or threat_name.lower() in sender_comm.subject.lower():
                print("✅ Threat classification referenced in warning")
            else:
                print("❌ Threat classification NOT found in warning")
                
            # Check if severity is referenced
            if message.severity.value.lower() in sender_comm.message.lower() or message.severity.value.lower() in sender_comm.subject.lower():
                print("✅ Severity level referenced in warning")
            else:
                print("❌ Severity level NOT found in warning")
        else:
            print("❌ No sender communication generated")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("🚀 Enhanced Agent Layer Testing")
    print("Testing that agent always generates 3 required actions:")
    print("1. Alert parents (notify_parent)")
    print("2. Educate child (educate_child)")
    print("3. Warn sender (warn_sender)")
    
    # Run tests
    success = test_required_actions()
    test_sender_warning_content()
    
    if success:
        print("\n🎯 Enhancement successful! Agent layer now ensures all 3 required actions.")
    else:
        print("\n⚠️  Enhancement needs review. Check the implementation.")
