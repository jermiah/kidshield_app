"""
Basic usage example for the AI Agent System
Demonstrates how to process suspicious messages and generate action plans
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel
from agents.ai_agent import AIAgent, AgentManager


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


def demonstrate_basic_processing():
    """Demonstrate basic message processing"""
    
    print("=== AI Agent System - Basic Usage Demo ===\n")
    
    # Load configuration
    config_file = Path(__file__).parent.parent / "config" / "agent_config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Initialize AI Agent
    print("1. Initializing AI Agent...")
    agent = AIAgent(config)
    print("   ✓ AI Agent initialized successfully\n")
    
    # Load and process a sample message
    print("2. Loading sample suspicious message...")
    message = load_sample_message("msg_001")  # Inappropriate request to 12-year-old
    print(f"   ✓ Loaded message: {message.message_id}")
    print(f"   - Threat Type: {message.threat_type.value}")
    print(f"   - Severity: {message.severity.value}")
    print(f"   - Child: {message.child_profile.name} (age {message.child_profile.age})")
    print(f"   - Content: \"{message.content[:50]}...\"\n")
    
    # Validate message
    print("3. Validating message...")
    if agent.validate_message(message):
        print("   ✓ Message validation passed\n")
    else:
        print("   ✗ Message validation failed\n")
        return
    
    # Process the message
    print("4. Processing suspicious message...")
    action_plan = agent.process_suspicious_message(message)
    print(f"   ✓ Action plan created with {len(action_plan.decisions)} decisions\n")
    
    # Display results
    print("5. Action Plan Results:")
    print("   " + "="*50)
    
    print(f"   Message ID: {action_plan.message_id}")
    print(f"   Created: {action_plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Follow-up Required: {action_plan.followup_required}")
    if action_plan.followup_date:
        print(f"   Follow-up Date: {action_plan.followup_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("   Decisions Made:")
    for i, decision in enumerate(action_plan.decisions, 1):
        print(f"   {i}. {decision.action_type.value.replace('_', ' ').title()}")
        print(f"      Priority: {decision.priority.value}")
        print(f"      Confidence: {decision.confidence:.2f}")
        print(f"      Target: {', '.join(decision.target_audience)}")
        print(f"      Reasoning: {decision.reasoning}")
        print()
    
    print("   Communications Generated:")
    for i, comm in enumerate(action_plan.communications, 1):
        print(f"   {i}. To: {comm.recipient_type.title()}")
        print(f"      Subject: {comm.subject}")
        print(f"      Tone: {comm.tone}")
        print(f"      Message Preview: \"{comm.message[:100]}...\"")
        if comm.additional_resources:
            print(f"      Resources: {len(comm.additional_resources)} attached")
        print()
    
    # Get summary
    summary = agent.get_action_summary(action_plan)
    print("   Summary Statistics:")
    print(f"   - Total Actions: {summary['total_actions']}")
    print(f"   - Immediate Actions: {summary['immediate_actions']}")
    print(f"   - Communications: {summary['communications_generated']}")
    print(f"   - Recipients: {', '.join(summary['recipients'])}")
    print(f"   - Average Confidence: {summary['average_confidence']:.2f}")
    print()


def demonstrate_batch_processing():
    """Demonstrate processing multiple messages"""
    
    print("=== Batch Processing Demo ===\n")
    
    # Initialize Agent Manager
    manager = AgentManager()
    
    # Load multiple sample messages
    print("1. Loading multiple sample messages...")
    messages = []
    for msg_id in ["msg_001", "msg_002", "msg_003"]:
        message = load_sample_message(msg_id)
        messages.append(message)
    
    print(f"   ✓ Loaded {len(messages)} messages\n")
    
    # Process batch
    print("2. Processing message batch...")
    action_plans = manager.process_message_batch(messages)
    print(f"   ✓ Processed {len(action_plans)} messages successfully\n")
    
    # Display batch summary
    print("3. Batch Processing Summary:")
    print("   " + "="*40)
    
    total_decisions = sum(len(plan.decisions) for plan in action_plans)
    total_communications = sum(len(plan.communications) for plan in action_plans)
    
    print(f"   Messages Processed: {len(action_plans)}")
    print(f"   Total Decisions: {total_decisions}")
    print(f"   Total Communications: {total_communications}")
    print(f"   Average Decisions per Message: {total_decisions/len(action_plans):.1f}")
    print()
    
    # Show individual results
    for plan in action_plans:
        message = next(m for m in messages if m.message_id == plan.message_id)
        print(f"   {plan.message_id} ({message.threat_type.value}):")
        print(f"   - Decisions: {len(plan.decisions)}")
        print(f"   - Communications: {len(plan.communications)}")
        print(f"   - Follow-up: {'Yes' if plan.followup_required else 'No'}")
        print()


def demonstrate_different_scenarios():
    """Demonstrate handling different threat scenarios"""
    
    print("=== Different Threat Scenarios Demo ===\n")
    
    agent = AIAgent()
    
    scenarios = [
        ("msg_001", "Inappropriate Request"),
        ("msg_002", "Cyberbullying"),
        ("msg_003", "Sexual Content"),
        ("msg_004", "Scam Attempt"),
        ("msg_005", "Manipulation"),
        ("msg_006", "Harassment")
    ]
    
    for msg_id, scenario_name in scenarios:
        print(f"Scenario: {scenario_name}")
        print("-" * 30)
        
        message = load_sample_message(msg_id)
        action_plan = agent.process_suspicious_message(message)
        
        print(f"Child: {message.child_profile.name} (age {message.child_profile.age})")
        print(f"Severity: {message.severity.value}")
        print(f"Actions: {len(action_plan.decisions)}")
        
        # Show primary actions
        primary_actions = [d.action_type.value for d in action_plan.decisions]
        print(f"Primary Actions: {', '.join(primary_actions)}")
        
        # Show communication targets
        comm_targets = list(set(c.recipient_type for c in action_plan.communications))
        print(f"Communications to: {', '.join(comm_targets)}")
        print()


if __name__ == "__main__":
    try:
        demonstrate_basic_processing()
        print("\n" + "="*60 + "\n")
        demonstrate_batch_processing()
        print("\n" + "="*60 + "\n")
        demonstrate_different_scenarios()
        
    except Exception as e:
        print(f"Error running demo: {str(e)}")
        import traceback
        traceback.print_exc()
