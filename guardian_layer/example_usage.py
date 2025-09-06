"""
Example usage of the Guardian App Pipeline
Demonstrates how to use the system for different types of content analysis
"""

import asyncio
import json
from guardian_app import GuardianApp

async def run_examples():
    """Run comprehensive examples of the Guardian App"""
    
    print("🛡️ Guardian App - Child Safety Pipeline Demo")
    print("=" * 50)
    
    # Initialize the Guardian App
    app = GuardianApp()
    
    # Check system status
    print("\n📊 System Status:")
    status = app.get_status()
    print(f"Status: {status['status']}")
    print(f"API Configured: {status['config']['api_configured']}")
    print(f"Education Enabled: {status['config']['education_enabled']}")
    
    # Test cases for different types of content
    test_cases = [
        {
            "name": "Safe Content",
            "text": "Hello! How was your day at school? I hope you learned something fun!",
            "expected": "SAFE"
        },
        {
            "name": "Mild Profanity",
            "text": "This damn homework is really hard!",
            "expected": "LOW"
        },
        {
            "name": "Grooming Attempt",
            "text": "You're such a special kid. This will be our little secret, don't tell your parents about our conversation.",
            "expected": "HIGH"
        },
        {
            "name": "Self-Harm Content",
            "text": "I'm so sad, I want to hurt myself. Life isn't worth living anymore.",
            "expected": "HIGH"
        },
        {
            "name": "Hate Speech",
            "text": "I hate all people from that country. They should all go away.",
            "expected": "MEDIUM/HIGH"
        },
        {
            "name": "Cyberbullying",
            "text": "You're so ugly and stupid. Nobody likes you. Kill yourself.",
            "expected": "HIGH"
        },
        {
            "name": "Educational Content",
            "text": "Did you know that photosynthesis is how plants make their own food using sunlight?",
            "expected": "SAFE"
        }
    ]
    
    print("\n🧪 Running Test Cases:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Input: \"{test_case['text']}\"")
        print(f"Expected Risk: {test_case['expected']}")
        
        try:
            # Process the message
            result = await app.process_text_message(test_case['text'])
            
            # Display results
            print(f"✅ Actual Risk: {result['risk_level'].upper()}")
            print(f"🚫 Blocked: {result['blocked']}")
            print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
            
            if result['threats_detected']:
                threats = ', '.join(result['threats_detected'])
                print(f"⚠️  Threats: {threats}")
            
            print(f"🤖 Decision: {result['decision']}")
            
            # Show educational messages
            if result['child_message']:
                print(f"👶 Child Message: \"{result['child_message']}\"")
            
            if result['parent_message'] and len(result['parent_message']) < 200:
                print(f"👨‍👩‍👧‍👦 Parent Message: \"{result['parent_message'][:100]}...\"")
            
            # Show agent breakdown
            print("🔍 Agent Analysis:")
            for agent_result in result['agent_results']:
                if agent_result['risk_score'] > 0.1:  # Only show agents that detected something
                    print(f"   - {agent_result['agent_name']}: Risk {agent_result['risk_score']:.2f}, "
                          f"Confidence {agent_result['confidence']:.2f}")
                    if agent_result['threats']:
                        print(f"     Threats: {', '.join(agent_result['threats'])}")
            
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
        
        print("-" * 30)

async def demonstrate_multimodal():
    """Demonstrate multimodal analysis (would need actual image files)"""
    print("\n🖼️ Multimodal Analysis Demo:")
    print("Note: This demo would require actual image files to test properly.")
    print("Example usage:")
    print("""
    app = GuardianApp()
    result = await app.process_multimodal_message(
        text="Check out this funny meme!",
        image_path="path/to/image.jpg"
    )
    """)

def show_configuration():
    """Show current configuration"""
    print("\n⚙️ Current Configuration:")
    from guardian_app.config import config
    
    print(f"API Key Configured: {'Yes' if config.model.blackbox_api_key else 'No'}")
    print(f"Low Risk Threshold: {config.model.low_risk_threshold}")
    print(f"Medium Risk Threshold: {config.model.medium_risk_threshold}")
    print(f"High Risk Threshold: {config.model.high_risk_threshold}")
    print(f"Logging Enabled: {config.pipeline.enable_logging}")
    print(f"Education Enabled: {config.pipeline.child_education_enabled}")
    print(f"Parent Notifications: {config.pipeline.parent_notification_enabled}")

async def main():
    """Main demo function"""
    try:
        # Show configuration
        show_configuration()
        
        # Run text analysis examples
        await run_examples()
        
        # Show multimodal demo info
        await demonstrate_multimodal()
        
        print("\n✅ Demo completed successfully!")
        print("\nTo integrate into your application:")
        print("1. Import: from guardian_app import GuardianApp")
        print("2. Initialize: app = GuardianApp()")
        print("3. Process: result = await app.process_text_message(text)")
        print("4. Handle result based on risk_level and blocked status")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
