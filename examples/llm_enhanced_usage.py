"""
LLM-Enhanced AI Agent System Example
Demonstrates the BlackBox LLM integration for enhanced decision-making and communication
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
from agents.ai_agent import AIAgent, AgentManager
from utils.blackbox_client import BlackBoxClient


def load_sample_message(message_id: str = "msg_001") -> SuspiciousMessage:
    """Load a sample message from the data file"""
    
    # Load sample data
    data_file = Path(__file__).parent.parent / "data" / "sample_messages.json"
    with open(data_file, 'r') as f:
        sample_data = json.load(f)
    
    # Find the requested message
    message_data = next((msg for msg in sample_data if msg["message_id"] == message_id), None)
    if not message_data:
        raise ValueError(f"Message {message_id} not found in sample data")
    
    # Create objects from data
    child_profile = ChildProfile(
        child_id=message_data["child_profile"]["child_id"],
        age=message_data["child_profile"]["age"],
        name=message_data["child_profile"]["name"],
        grade_level=message_data["child_profile"]["grade_level"],
        previous_incidents=message_data["child_profile"]["previous_incidents"],
        parental_notification_preferences=message_data["child_profile"]["parental_notification_preferences"]
    )
    
    metadata = MessageMetadata(
        sender_id=message_data["metadata"]["sender_id"],
        sender_type=message_data["metadata"]["sender_type"],
        platform=message_data["metadata"]["platform"],
        timestamp=datetime.fromisoformat(message_data["metadata"]["timestamp"].replace('Z', '+00:00')),
        message_frequency=message_data["metadata"]["message_frequency"],
        sender_history=message_data["metadata"]["sender_history"],
        confidence_score=message_data["metadata"]["confidence_score"]
    )
    
    message = SuspiciousMessage(
        message_id=message_data["message_id"],
        content=message_data["content"],
        threat_type=ThreatType(message_data["threat_type"]),
        severity=SeverityLevel(message_data["severity"]),
        child_profile=child_profile,
        metadata=metadata,
        context=message_data.get("context", {})
    )
    
    return message


def test_blackbox_client():
    """Test the BlackBox client directly"""
    
    print("=== Testing BlackBox LLM Client ===\n")
    
    try:
        client = BlackBoxClient()
        print("✓ BlackBox client initialized successfully")
        
        # Test decision reasoning generation
        print("\n1. Testing Decision Reasoning Generation...")
        reasoning = client.generate_decision_reasoning(
            message_content="Hey, you're really cute. Want to meet up somewhere private?",
            threat_type="inappropriate_request",
            severity="high",
            child_age=12,
            context={"sender_type": "stranger", "platform": "social_media"}
        )
        print(f"Generated reasoning:\n{reasoning}\n")
        
        # Test parent message generation
        print("2. Testing Parent Message Generation...")
        parent_msg = client.generate_parent_message(
            child_name="Emma",
            threat_type="inappropriate_request",
            severity="high",
            action_taken="Sender has been blocked",
            tone="urgent"
        )
        print(f"Parent message subject: {parent_msg['subject']}")
        print(f"Parent message preview: {parent_msg['message'][:200]}...\n")
        
        # Test child message generation
        print("3. Testing Child Message Generation...")
        child_msg = client.generate_child_message(
            child_name="Emma",
            child_age=12,
            threat_type="inappropriate_request",
            tone="supportive"
        )
        print(f"Child message subject: {child_msg['subject']}")
        print(f"Child message preview: {child_msg['message'][:200]}...\n")
        
        # Test sender warning generation
        print("4. Testing Sender Warning Generation...")
        sender_msg = client.generate_sender_warning(
            threat_type="inappropriate_request",
            platform="social_media"
        )
        print(f"Sender warning subject: {sender_msg['subject']}")
        print(f"Sender warning preview: {sender_msg['message'][:200]}...\n")
        
        return True
        
    except Exception as e:
        print(f"✗ BlackBox client test failed: {str(e)}")
        return False


def demonstrate_llm_enhanced_processing():
    """Demonstrate LLM-enhanced message processing"""
    
    print("=== LLM-Enhanced AI Agent Processing ===\n")
    
    # Load configuration
    config_file = Path(__file__).parent.parent / "config" / "agent_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Initialize AI Agent with LLM enabled
    print("1. Initializing LLM-Enhanced AI Agent...")
    agent_llm = AIAgent(config, use_llm=True)
    print("   ✓ LLM-Enhanced AI Agent initialized\n")
    
    # Initialize AI Agent without LLM for comparison
    print("2. Initializing Standard AI Agent (no LLM)...")
    agent_standard = AIAgent(config, use_llm=False)
    print("   ✓ Standard AI Agent initialized\n")
    
    # Load a sample message
    print("3. Loading sample message...")
    message = load_sample_message("msg_001")  # Inappropriate request
    print(f"   ✓ Loaded message: {message.message_id}")
    print(f"   - Content: \"{message.content}\"")
    print(f"   - Child: {message.child_profile.name} (age {message.child_profile.age})\n")
    
    # Process with LLM-enhanced agent
    print("4. Processing with LLM-Enhanced Agent...")
    try:
        action_plan_llm = agent_llm.process_suspicious_message(message)
        print("   ✓ LLM-enhanced processing completed\n")
        
        print("   LLM-Enhanced Results:")
        print("   " + "="*40)
        
        # Show enhanced reasoning
        for i, decision in enumerate(action_plan_llm.decisions, 1):
            print(f"   Decision {i}: {decision.action_type.value}")
            print(f"   Enhanced Reasoning:")
            print(f"   {decision.reasoning[:300]}...")
            print()
        
        # Show enhanced communications
        print("   Enhanced Communications:")
        for i, comm in enumerate(action_plan_llm.communications, 1):
            print(f"   {i}. To {comm.recipient_type.title()}:")
            print(f"      Subject: {comm.subject}")
            print(f"      Message: {comm.message[:150]}...")
            print()
            
    except Exception as e:
        print(f"   ✗ LLM processing failed: {str(e)}")
        action_plan_llm = None
    
    # Process with standard agent for comparison
    print("5. Processing with Standard Agent (for comparison)...")
    action_plan_standard = agent_standard.process_suspicious_message(message)
    print("   ✓ Standard processing completed\n")
    
    print("   Standard Results:")
    print("   " + "="*40)
    
    # Show standard reasoning
    for i, decision in enumerate(action_plan_standard.decisions, 1):
        print(f"   Decision {i}: {decision.action_type.value}")
        print(f"   Standard Reasoning: {decision.reasoning}")
        print()
    
    # Compare results
    if action_plan_llm:
        print("6. Comparison Summary:")
        print("   " + "="*30)
        print(f"   LLM Decisions: {len(action_plan_llm.decisions)}")
        print(f"   Standard Decisions: {len(action_plan_standard.decisions)}")
        print(f"   LLM Communications: {len(action_plan_llm.communications)}")
        print(f"   Standard Communications: {len(action_plan_standard.communications)}")
        
        # Show reasoning length comparison
        llm_reasoning_length = sum(len(d.reasoning) for d in action_plan_llm.decisions)
        standard_reasoning_length = sum(len(d.reasoning) for d in action_plan_standard.decisions)
        
        print(f"   LLM Reasoning Detail: {llm_reasoning_length} characters")
        print(f"   Standard Reasoning Detail: {standard_reasoning_length} characters")
        print(f"   Enhancement Factor: {llm_reasoning_length / standard_reasoning_length:.1f}x more detailed")


def demonstrate_different_scenarios_with_llm():
    """Demonstrate LLM enhancement across different threat scenarios"""
    
    print("\n=== LLM Enhancement Across Different Scenarios ===\n")
    
    agent = AIAgent(use_llm=True)
    
    scenarios = [
        ("msg_002", "Cyberbullying (Critical)"),
        ("msg_003", "Sexual Content (Critical)"),
        ("msg_004", "Scam Attempt (Medium)"),
        ("msg_005", "Manipulation (High)")
    ]
    
    for msg_id, scenario_name in scenarios:
        print(f"Scenario: {scenario_name}")
        print("-" * 50)
        
        try:
            message = load_sample_message(msg_id)
            action_plan = agent.process_suspicious_message(message)
            
            print(f"Child: {message.child_profile.name} (age {message.child_profile.age})")
            print(f"Threat: {message.threat_type.value} | Severity: {message.severity.value}")
            print(f"Actions Generated: {len(action_plan.decisions)}")
            
            # Show first decision's enhanced reasoning
            if action_plan.decisions:
                first_decision = action_plan.decisions[0]
                print(f"Primary Action: {first_decision.action_type.value}")
                print(f"LLM Reasoning Preview: {first_decision.reasoning[:200]}...")
            
            # Show communication personalization
            parent_comms = [c for c in action_plan.communications if c.recipient_type == "parent"]
            if parent_comms:
                print(f"Parent Communication: {parent_comms[0].subject}")
            
            print()
            
        except Exception as e:
            print(f"Error processing {scenario_name}: {str(e)}\n")


def demonstrate_fallback_behavior():
    """Demonstrate fallback behavior when LLM is unavailable"""
    
    print("=== Fallback Behavior Demo ===\n")
    
    print("1. Testing with invalid API key (should fallback to templates)...")
    
    # Temporarily set invalid API key
    import os
    original_key = os.environ.get('BLACKBOX_API_KEY')
    os.environ['BLACKBOX_API_KEY'] = 'invalid_key'
    
    try:
        agent = AIAgent(use_llm=True)  # Will try LLM but fallback to templates
        message = load_sample_message("msg_001")
        action_plan = agent.process_suspicious_message(message)
        
        print("   ✓ Fallback successful - system continued to work")
        print(f"   Generated {len(action_plan.decisions)} decisions")
        print(f"   Generated {len(action_plan.communications)} communications")
        
    except Exception as e:
        print(f"   ✗ Fallback failed: {str(e)}")
    
    finally:
        # Restore original API key
        if original_key:
            os.environ['BLACKBOX_API_KEY'] = original_key
        else:
            os.environ.pop('BLACKBOX_API_KEY', None)
    
    print("\n2. Testing with LLM explicitly disabled...")
    
    try:
        agent = AIAgent(use_llm=False)
        message = load_sample_message("msg_001")
        action_plan = agent.process_suspicious_message(message)
        
        print("   ✓ Template-only mode successful")
        print(f"   Generated {len(action_plan.decisions)} decisions")
        print(f"   Generated {len(action_plan.communications)} communications")
        
    except Exception as e:
        print(f"   ✗ Template-only mode failed: {str(e)}")


if __name__ == "__main__":
    try:
        # Test BlackBox client first
        if test_blackbox_client():
            print("\n" + "="*60 + "\n")
            demonstrate_llm_enhanced_processing()
            
            print("\n" + "="*60 + "\n")
            demonstrate_different_scenarios_with_llm()
            
            print("\n" + "="*60 + "\n")
            demonstrate_fallback_behavior()
        else:
            print("\nSkipping LLM demos due to client initialization failure.")
            print("Please check your BLACKBOX_API_KEY in the .env file.")
        
    except Exception as e:
        print(f"Error running LLM demo: {str(e)}")
        import traceback
        traceback.print_exc()
