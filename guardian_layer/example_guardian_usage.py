"""Example usage of the Guardian Layer API"""

import asyncio
import json
import base64
from guardian_app.guardian_layer import guardian_layer
from guardian_app.schemas.guardian_schemas import GuardianRequest

async def test_text_analysis():
    """Test text content analysis"""
    print("=== Text Analysis Examples ===\n")
    
    test_cases = [
        {
            "text": "Hello, how are you today?",
            "description": "Safe message"
        },
        {
            "text": "You're so special, don't tell your parents about our conversation",
            "description": "Potential grooming attempt"
        },
        {
            "text": "I hate all people from that country, they should all disappear",
            "description": "Hate speech"
        },
        {
            "text": "I want to hurt myself, life is not worth living",
            "description": "Self-harm content"
        },
        {
            "text": "This is a damn good movie, but the violence is intense",
            "description": "Mild profanity with violence mention"
        },
        {
            "text": "Send me your private photos, I'll keep them secret",
            "description": "Sexual/predatory content"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['description']}")
        print(f"Text: '{case['text']}'")
        
        request = GuardianRequest(text=case['text'])
        result = await guardian_layer.process_request(request)
        
        print(f"Status: {result.status.value}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
        if result.results.text_risk:
            print("Text Risks:")
            for risk in result.results.text_risk:
                print(f"  - {risk.category}: {risk.score:.2f}")
        else:
            print("No text risks detected")
        
        print("-" * 50)

async def test_multimodal_analysis():
    """Test multimodal content analysis"""
    print("\n=== Multimodal Analysis Example ===\n")
    
    # Create a simple test case with text and placeholder image
    request = GuardianRequest(
        text="Check out this funny meme!",
        image="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="  # 1x1 transparent PNG
    )
    
    result = await guardian_layer.process_request(request)
    
    print("Multimodal Analysis Result:")
    print(f"Input ID: {result.input_id}")
    print(f"Status: {result.status.value}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    
    if result.results.text_risk:
        print("Text Risks:")
        for risk in result.results.text_risk:
            print(f"  - {risk.category}: {risk.score:.2f}")
    
    if result.results.image_risk:
        print("Image Risks:")
        for risk in result.results.image_risk:
            print(f"  - {risk.category}: {risk.score:.2f}")
    
    print("-" * 50)

async def test_api_response_format():
    """Test the structured API response format"""
    print("\n=== API Response Format Example ===\n")
    
    request = GuardianRequest(
        text="You're so beautiful, let's meet in private",
        user_id="test_user_123"
    )
    
    result = await guardian_layer.process_request(request)
    
    # Convert to dict to show the exact API response format
    response_dict = {
        "input_id": result.input_id,
        "results": {
            "text_risk": [
                {"category": risk.category, "score": risk.score} 
                for risk in result.results.text_risk
            ],
            "image_risk": [
                {"category": risk.category, "score": risk.score} 
                for risk in result.results.image_risk
            ]
        },
        "status": result.status.value,
        "timestamp": result.timestamp.isoformat(),
        "processing_time": result.processing_time
    }
    
    print("Structured API Response:")
    print(json.dumps(response_dict, indent=2))
    print("-" * 50)

async def test_guardian_status():
    """Test guardian layer status"""
    print("\n=== Guardian Layer Status ===\n")
    
    status = guardian_layer.get_status()
    print("Guardian Layer Status:")
    print(json.dumps(status, indent=2))
    print("-" * 50)

async def main():
    """Run all test examples"""
    print("Guardian Layer API - Example Usage")
    print("=" * 50)
    
    try:
        await test_guardian_status()
        await test_text_analysis()
        await test_multimodal_analysis()
        await test_api_response_format()
        
        print("\n✅ All tests completed successfully!")
        print("\nTo run the API server:")
        print("python guardian_app/run_api.py")
        print("\nAPI will be available at:")
        print("- Main endpoint: POST http://localhost:8000/guardian/check")
        print("- Documentation: http://localhost:8000/docs")
        print("- Health check: http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
