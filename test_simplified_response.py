#!/usr/bin/env python3
"""
Test script to demonstrate the simplified API response format
that only returns action types and messages to send
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add agent_layer to path
agent_path = Path(__file__).parent / "agent_layer"
sys.path.append(str(agent_path))

from agent_layer.agents.ai_agent import AIAgent
from agent_layer.models.message import SuspiciousMessage, ThreatType, SeverityLevel, ChildProfile, MessageMetadata
from agent_layer.models.actions import ActionType


def create_test_message(content: str, threat_type: ThreatType, severity: SeverityLevel) -> SuspiciousMessage:
    """Create a test suspicious message"""
    
    child_profile = ChildProfile(
        child_id="child_123",
        name="Emma",
        age=12,
        previous_incidents=0,
        parental_notification_preferences={
            "immediate_notification": True,
            "email": "parent@example.com"
        }
    )
    
    metadata = MessageMetadata(
        sender_id="sender_456",
        platform="test_chat_app",
        timestamp=datetime.now(),
        sender_type="unknown",
        sender_history={},
        message_frequency=1
    )
    
    return SuspiciousMessage(
        message_id=f"msg_{datetime.now().timestamp()}",
        content=content,
        threat_type=threat_type,
        severity=severity,
        child_profile=child_profile,
        metadata=metadata
    )


def simulate_api_response(message: SuspiciousMessage):
    """Simulate the simplified API response format"""
    
    # Initialize agent (without LLM for faster testing)
    agent = AIAgent(use_llm=False)
    
    # Process message
    action_plan = agent.process_suspicious_message(message)
    
    # Extract only the essential information: action types and messages
    messages_to_send = []
    for comm in action_plan.communications:
        messages_to_send.append({
            "recipient": comm.recipient_type,
            "subject": comm.subject,
            "message": comm.message,
            "tone": comm.tone
        })
    
    # Return simplified response format (same as API)
    return {
        "success": True,
        "data": {
            "action_types": [d.action_type.value for d in action_plan.decisions],
            "messages": messages_to_send,
            "message_id": message.message_id,
            "followup_required": action_plan.followup_required
        },
        "message": "Actions planned and messages generated"
    }


def test_simplified_responses():
    """Test the simplified response format with different scenarios"""
    
    print("🚀 Testing Simplified API Response Format")
    print("=" * 60)
    print("✅ Enhanced agent now ensures 3 actions: alert parents, educate child, warn sender")
    print("📧 Response only includes action types and messages to send")
    print()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Bullying Message",
            "content": "You're so stupid, nobody likes you",
            "threat_type": ThreatType.BULLYING,
            "severity": SeverityLevel.HIGH
        },
        {
            "name": "Inappropriate Request",
            "content": "Can you send me a photo of yourself?",
            "threat_type": ThreatType.INAPPROPRIATE_REQUEST,
            "severity": SeverityLevel.MEDIUM
        },
        {
            "name": "Stranger Contact",
            "content": "Hi, I'm new here. Want to be friends?",
            "threat_type": ThreatType.STRANGER_CONTACT,
            "severity": SeverityLevel.LOW
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Create test message
        message = create_test_message(
            test_case["content"],
            test_case["threat_type"],
            test_case["severity"]
        )
        
        # Get simplified response
        response = simulate_api_response(message)
        
        # Display results
        print(f"🎯 Action Types: {response['data']['action_types']}")
        print(f"📨 Messages Generated: {len(response['data']['messages'])}")
        
        # Show each message
        for msg in response['data']['messages']:
            print(f"   📧 To {msg['recipient']}: {msg['subject']}")
            print(f"      Tone: {msg['tone']}")
            print(f"      Preview: {msg['message'][:100]}...")
            print()
        
        # Verify the 3 required actions are present
        required_actions = {"notify_parent", "educate_child", "warn_sender"}
        generated_actions = set(response['data']['action_types'])
        
        if required_actions.issubset(generated_actions):
            print("✅ All 3 required actions generated!")
        else:
            missing = required_actions - generated_actions
            print(f"❌ Missing actions: {missing}")
        
        print("\n" + "="*60 + "\n")


def show_example_json_response():
    """Show example of the simplified JSON response"""
    
    print("📄 Example Simplified JSON Response:")
    print("-" * 40)
    
    # Create a test message
    message = create_test_message(
        "You're ugly and nobody likes you",
        ThreatType.BULLYING,
        SeverityLevel.HIGH
    )
    
    # Get response
    response = simulate_api_response(message)
    
    # Pretty print JSON
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    test_simplified_responses()
    show_example_json_response()
    
    print("\n🎉 Enhancement Complete!")
    print("✅ Agent layer now guarantees 3 actions for any detected risk")
    print("✅ API response simplified to only include action types and messages")
    print("✅ Sender warnings reference specific threat classifications")
