"""Main application entry point for the Guardian App"""

import asyncio
import sys
from typing import Optional
from .pipeline_orchestrator import GuardianPipeline
from .models import InputMessage
from .utils import generate_message_id, logger
from .config import config

class GuardianApp:
    """Main Guardian App class"""
    
    def __init__(self):
        self.pipeline = GuardianPipeline()
        self.logger = logger
    
    async def process_text_message(self, text: str, user_id: Optional[str] = None) -> dict:
        """
        Process a text message through the guardian pipeline
        
        Args:
            text: The text message to analyze
            user_id: Optional user identifier
            
        Returns:
            Dictionary with processing results
        """
        message = InputMessage(
            message_id=generate_message_id(),
            text=text,
            user_id=user_id
        )
        
        self.logger.info(f"Processing text message: {message.message_id}")
        result = await self.pipeline.process_message(message)
        
        return self._format_result(result)
    
    async def process_image_message(self, image_path: str, user_id: Optional[str] = None) -> dict:
        """
        Process an image message through the guardian pipeline
        
        Args:
            image_path: Path to the image file
            user_id: Optional user identifier
            
        Returns:
            Dictionary with processing results
        """
        message = InputMessage(
            message_id=generate_message_id(),
            image_path=image_path,
            user_id=user_id
        )
        
        self.logger.info(f"Processing image message: {message.message_id}")
        result = await self.pipeline.process_message(message)
        
        return self._format_result(result)
    
    async def process_multimodal_message(
        self, 
        text: str, 
        image_path: str, 
        user_id: Optional[str] = None
    ) -> dict:
        """
        Process a multimodal message (text + image) through the guardian pipeline
        
        Args:
            text: The text content
            image_path: Path to the image file
            user_id: Optional user identifier
            
        Returns:
            Dictionary with processing results
        """
        message = InputMessage(
            message_id=generate_message_id(),
            text=text,
            image_path=image_path,
            user_id=user_id
        )
        
        self.logger.info(f"Processing multimodal message: {message.message_id}")
        result = await self.pipeline.process_message(message)
        
        return self._format_result(result)
    
    def _format_result(self, result) -> dict:
        """Format pipeline result for API response"""
        return {
            'message_id': result.message_id,
            'risk_level': result.risk_level.value,
            'risk_score': result.overall_risk_score,
            'threats_detected': [threat.value for threat in result.threats_detected],
            'blocked': result.blocked,
            'decision': result.decision,
            'child_message': result.child_message,
            'parent_message': result.parent_message,
            'processing_time': result.processing_time,
            'timestamp': result.timestamp.isoformat(),
            'agent_results': [
                {
                    'agent_name': agent_result.agent_name,
                    'risk_score': agent_result.risk_score,
                    'confidence': agent_result.confidence,
                    'threats': [threat.value for threat in agent_result.threats_detected],
                    'explanation': agent_result.explanation
                }
                for agent_result in result.agent_results
            ]
        }
    
    def get_status(self) -> dict:
        """Get application status"""
        return {
            'status': 'running',
            'pipeline_status': self.pipeline.get_pipeline_status(),
            'config': {
                'api_configured': bool(config.model.blackbox_api_key),
                'logging_enabled': config.pipeline.enable_logging,
                'education_enabled': config.pipeline.child_education_enabled
            }
        }

# Example usage functions
async def example_text_analysis():
    """Example of analyzing text content"""
    app = GuardianApp()
    
    # Test cases
    test_messages = [
        "Hello, how are you today?",  # Safe message
        "You're so special, don't tell your parents about our conversation",  # Grooming attempt
        "I hate all people from that country",  # Hate speech
        "I want to hurt myself",  # Self-harm
        "This is a damn good movie!"  # Mild profanity
    ]
    
    print("=== Text Analysis Examples ===")
    for i, text in enumerate(test_messages, 1):
        print(f"\nTest {i}: '{text}'")
        result = await app.process_text_message(text)
        print(f"Risk Level: {result['risk_level']}")
        print(f"Blocked: {result['blocked']}")
        print(f"Decision: {result['decision']}")
        print(f"Child Message: {result['child_message']}")
        if result['threats_detected']:
            print(f"Threats: {', '.join(result['threats_detected'])}")

async def example_multimodal_analysis():
    """Example of analyzing text + image content"""
    app = GuardianApp()
    
    print("\n=== Multimodal Analysis Example ===")
    # This would require an actual image file
    # result = await app.process_multimodal_message(
    #     text="Check out this funny meme!",
    #     image_path="path/to/image.jpg"
    # )
    print("Multimodal analysis requires actual image files to test.")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            asyncio.run(example_text_analysis())
        elif command == "status":
            app = GuardianApp()
            status = app.get_status()
            print("Guardian App Status:")
            print(f"Status: {status['status']}")
            print(f"API Configured: {status['config']['api_configured']}")
            print(f"Current Stage: {status['pipeline_status']['current_stage']}")
        else:
            print("Available commands: test, status")
    else:
        print("Guardian App - Child Safety Pipeline")
        print("Usage: python -m guardian_app.main [command]")
        print("Commands:")
        print("  test   - Run example analysis")
        print("  status - Show application status")

if __name__ == "__main__":
    main()
