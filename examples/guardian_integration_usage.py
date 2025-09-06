"""
Guardian Layer → KidShield App Integration Example

Demonstrates how to use the Guardian Layer output as input to KidShield App
"""

import json
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from integrations.guardian_integration import GuardianIntegration, convert_guardian_to_kidshield
from models.message import ChildProfile
from agents.ai_agent import AIAgent


async def demonstrate_guardian_kidshield_integration():
    """Demonstrate the complete Guardian → KidShield integration workflow"""
    
    print("=== Guardian Layer → KidShield App Integration Demo ===\n")
    
    # Initialize components
    guardian_integration = GuardianIntegration()
    kidshield_agent = AIAgent(use_llm=True)
    
    print("1. Guardian Layer Analysis Results (Structured Output)")
    print("-" * 50)
    
    # Sample Guardian Layer structured output (what you would get from Guardian API)
    guardian_response = {
        "input_id": "guardian_analysis_001",
        "results": {
            "text_risk": [
                {"category": "sexual", "score": 0.88},
                {"category": "grooming", "score": 0.75},
                {"category": "predatory", "score": 0.82}
            ],
            "image_risk": [
                {"category": "inappropriate", "score": 0.45}
            ]
        },
        "status": "flagged",
        "timestamp": "2024-01-15T14:30:00Z",
        "processing_time": 0.65
    }
    
    original_message_content = "Hey beautiful, you look so mature for your age. Want to meet up somewhere private? Don't tell your parents about our conversation."
    
    print("Guardian Response:")
    print(json.dumps(guardian_response, indent=2))
    print(f"\nOriginal Message: \"{original_message_content}\"")
    
    print("\n2. Converting Guardian Output to KidShield Input")
    print("-" * 50)
    
    # Create child profile (this would typically come from your user database)
    child_profile = ChildProfile(
        child_id="child_emma_123",
        age=12,
        name="Emma",
        grade_level="7th",
        previous_incidents=0,
        parental_notification_preferences={
            "immediate_notification": True,
            "daily_summary": False,
            "weekly_summary": True
        }
    )
    
    # Additional metadata (from your platform/app)
    additional_metadata = {
        "sender_id": "unknown_user_456",
        "sender_type": "stranger",
        "platform": "social_media",
        "message_frequency": 3,
        "sender_history": {
            "previous_reports": 1,
            "account_age_days": 5
        }
    }
    
    # Convert Guardian response to KidShield format
    suspicious_message = guardian_integration.convert_guardian_response(
        guardian_response,
        original_message_content,
        child_profile,
        additional_metadata
    )
    
    print("✅ Conversion successful!")
    print(f"Message ID: {suspicious_message.message_id}")
    print(f"Threat Type: {suspicious_message.threat_type.value}")
    print(f"Severity: {suspicious_message.severity.value}")
    print(f"Child: {suspicious_message.child_profile.name} (age {suspicious_message.child_profile.age})")
    print(f"Confidence Score: {suspicious_message.metadata.confidence_score:.2f}")
    
    print("\n3. Processing with KidShield AI Agent")
    print("-" * 50)
    
    # Process the converted message with KidShield
    action_plan = kidshield_agent.process_suspicious_message(suspicious_message)
    
    print(f"✅ KidShield processing complete!")
    print(f"Generated {len(action_plan.decisions)} decisions")
    print(f"Created {len(action_plan.communications)} communications")
    print(f"Follow-up required: {action_plan.followup_required}")
    
    print("\n4. Action Plan Details")
    print("-" * 50)
    
    print("Decisions Made:")
    for i, decision in enumerate(action_plan.decisions, 1):
        print(f"  {i}. {decision.action_type.value.replace('_', ' ').title()}")
        print(f"     Priority: {decision.priority.value}")
        print(f"     Confidence: {decision.confidence:.2f}")
        print(f"     Reasoning: {decision.reasoning[:100]}...")
        print()
    
    print("Communications Generated:")
    for i, comm in enumerate(action_plan.communications, 1):
        print(f"  {i}. To: {comm.recipient_type.title()}")
        print(f"     Subject: {comm.subject}")
        print(f"     Tone: {comm.tone}")
        print(f"     Preview: \"{comm.message[:80]}...\"")
        print()
    
    print("5. Guardian Analysis Context (Preserved)")
    print("-" * 50)
    
    # Show how Guardian analysis details are preserved in context
    guardian_context = suspicious_message.context["guardian_analysis"]
    risk_breakdown = suspicious_message.context["risk_breakdown"]
    
    print("Guardian Analysis Details:")
    print(f"  Input ID: {guardian_context['input_id']}")
    print(f"  Status: {guardian_context['status']}")
    print(f"  Processing Time: {guardian_context['processing_time']}s")
    print(f"  Total Risk Categories: {risk_breakdown['total_risks']}")
    print(f"  Max Risk Score: {risk_breakdown['max_risk_score']}")
    print(f"  Text Risks: {risk_breakdown['text_risk_count']}")
    print(f"  Image Risks: {risk_breakdown['image_risk_count']}")


async def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple Guardian responses"""
    
    print("\n\n=== Batch Processing Demo ===\n")
    
    guardian_integration = GuardianIntegration()
    kidshield_agent = AIAgent(use_llm=True)
    
    # Multiple Guardian responses
    guardian_responses = [
        {
            "input_id": "batch_001",
            "results": {
                "text_risk": [{"category": "bullying", "score": 0.72}],
                "image_risk": []
            },
            "status": "flagged",
            "timestamp": "2024-01-15T15:00:00Z",
            "processing_time": 0.3
        },
        {
            "input_id": "batch_002",
            "results": {
                "text_risk": [{"category": "sexual", "score": 0.91}],
                "image_risk": [{"category": "nudity", "score": 0.85}]
            },
            "status": "flagged",
            "timestamp": "2024-01-15T15:01:00Z",
            "processing_time": 0.8
        },
        {
            "input_id": "batch_003",
            "results": {
                "text_risk": [{"category": "violence", "score": 0.65}],
                "image_risk": []
            },
            "status": "flagged",
            "timestamp": "2024-01-15T15:02:00Z",
            "processing_time": 0.4
        }
    ]
    
    original_contents = [
        "You're so stupid and ugly. Nobody likes you.",
        "Send me your private photos, I'll keep them secret.",
        "I'm going to hurt you if you don't do what I say."
    ]
    
    print(f"Processing {len(guardian_responses)} Guardian responses...")
    
    # Batch convert Guardian responses
    suspicious_messages = guardian_integration.batch_convert(
        guardian_responses,
        original_contents
    )
    
    print(f"✅ Converted {len(suspicious_messages)} messages")
    
    # Process each with KidShield
    action_plans = []
    for message in suspicious_messages:
        action_plan = kidshield_agent.process_suspicious_message(message)
        action_plans.append(action_plan)
    
    print(f"✅ Generated {len(action_plans)} action plans")
    
    # Summary
    print("\nBatch Processing Summary:")
    print("-" * 30)
    
    total_decisions = sum(len(plan.decisions) for plan in action_plans)
    total_communications = sum(len(plan.communications) for plan in action_plans)
    
    print(f"Total Messages: {len(suspicious_messages)}")
    print(f"Total Decisions: {total_decisions}")
    print(f"Total Communications: {total_communications}")
    print(f"Average Decisions per Message: {total_decisions/len(action_plans):.1f}")
    
    for i, (message, plan) in enumerate(zip(suspicious_messages, action_plans), 1):
        print(f"\nMessage {i} ({message.threat_type.value}):")
        print(f"  Severity: {message.severity.value}")
        print(f"  Decisions: {len(plan.decisions)}")
        print(f"  Communications: {len(plan.communications)}")


async def demonstrate_api_integration():
    """Demonstrate how this would work with Guardian API calls"""
    
    print("\n\n=== API Integration Example ===\n")
    
    print("This is how you would integrate with a live Guardian API:")
    print("-" * 50)
    
    # Example API integration code (pseudo-code)
    api_integration_example = '''
import requests
from integrations.guardian_integration import convert_guardian_to_kidshield
from agents.ai_agent import AIAgent

async def process_message_with_guardian_api(message_content, child_profile):
    """Complete workflow: Message → Guardian API → KidShield"""
    
    # 1. Send to Guardian API
    guardian_response = requests.post(
        "http://localhost:8000/guardian/check",
        json={
            "text": message_content,
            "user_id": child_profile.child_id
        }
    )
    
    guardian_data = guardian_response.json()["data"]
    
    # 2. Convert to KidShield format
    suspicious_message = convert_guardian_to_kidshield(
        guardian_data,
        message_content,
        child_profile
    )
    
    # 3. Process with KidShield
    agent = AIAgent(use_llm=True)
    action_plan = agent.process_suspicious_message(suspicious_message)
    
    return action_plan
'''
    
    print(api_integration_example)
    
    print("\nTo run Guardian API server:")
    print("cd guardian_layer && python run_api.py")
    print("\nAPI endpoints:")
    print("- POST /guardian/check - Main analysis endpoint")
    print("- GET /health - Health check")
    print("- GET /docs - API documentation")


def demonstrate_risk_mapping():
    """Show the risk category mapping between Guardian and KidShield"""
    
    print("\n\n=== Risk Category Mapping ===\n")
    
    integration = GuardianIntegration()
    
    print("Guardian Category → KidShield Threat Type")
    print("-" * 45)
    
    for guardian_cat, kidshield_threat in integration.category_mapping.items():
        print(f"{guardian_cat:15} → {kidshield_threat.value}")
    
    print("\nSeverity Score Mapping:")
    print("-" * 25)
    
    for threshold, severity in sorted(integration.severity_thresholds.items(), reverse=True):
        print(f"Score ≥ {threshold:3.1f} → {severity.value.upper()}")


async def main():
    """Run all integration examples"""
    
    try:
        await demonstrate_guardian_kidshield_integration()
        await demonstrate_batch_processing()
        await demonstrate_api_integration()
        demonstrate_risk_mapping()
        
        print("\n" + "="*60)
        print("✅ Guardian Layer → KidShield Integration Demo Complete!")
        print("="*60)
        
        print("\nNext Steps:")
        print("1. Start Guardian API: cd guardian_layer && python run_api.py")
        print("2. Test integration with live API calls")
        print("3. Integrate into your application workflow")
        print("4. Monitor and tune risk thresholds as needed")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
