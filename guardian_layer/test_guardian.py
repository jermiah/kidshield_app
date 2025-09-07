#!/usr/bin/env python3
"""Simple test script to verify Guardian Layer functionality"""

import os
import sys
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports and API key loading
def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    
    try:
        from config import config
        print("✅ Config loaded successfully")
        
        # Check API key
        api_key = config.model.blackbox_api_key
        if api_key and api_key != "ADD A KEY HERE" and len(api_key) > 10:
            print(f"✅ API Key loaded: {api_key[:10]}...")
        else:
            print("❌ API Key not properly loaded")
            
        # Check other settings
        print(f"✅ Log level: {config.pipeline.log_level}")
        print(f"✅ Text confidence threshold: {config.model.text_model_confidence}")
        
        return True
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False

def test_models():
    """Test model imports"""
    print("\n📊 Testing Models...")
    
    try:
        from models import InputMessage, AgentResult, ThreatCategory, ContentType
        print("✅ Models imported successfully")
        
        # Test creating a simple message
        msg = InputMessage(
            message_id="test_123",
            text="Hello world"
        )
        print(f"✅ Created InputMessage: {msg.text}")
        print(f"✅ Content type detected: {msg.content_type}")
        
        return True
    except Exception as e:
        print(f"❌ Models failed: {e}")
        return False

def test_guardian_layer():
    """Test Guardian Layer"""
    print("\n🛡️ Testing Guardian Layer...")
    
    try:
        from guardian_layer import GuardianLayer
        guardian = GuardianLayer()
        print("✅ Guardian Layer initialized successfully")
        
        return guardian
    except Exception as e:
        print(f"❌ Guardian Layer failed: {e}")
        return None

async def test_analysis():
    """Test actual analysis"""
    print("\n🔍 Testing Analysis...")
    
    try:
        from guardian_layer import GuardianLayer
        from schemas.guardian_schemas import GuardianRequest
        
        guardian = GuardianLayer()
        
        # Test safe text
        request = GuardianRequest(
            text="Hello, how are you today?",
            user_id="test_user"
        )
        
        result = await guardian.analyze(request)
        print(f"✅ Analysis completed")
        print(f"   Risk Score: {result.risk_score}")
        print(f"   Status: {result.status}")
        print(f"   Categories: {[cat.category for cat in result.categories]}")
        
        return True
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Guardian Layer Health Check")
    print("=" * 40)
    
    # Test configuration
    config_ok = test_config()
    
    # Test models
    models_ok = test_models()
    
    # Test guardian layer
    guardian = test_guardian_layer()
    
    # Test analysis if everything else works
    if config_ok and models_ok and guardian:
        analysis_ok = await test_analysis()
    else:
        analysis_ok = False
    
    print("\n" + "=" * 40)
    print("📋 Summary:")
    print(f"   Config: {'✅' if config_ok else '❌'}")
    print(f"   Models: {'✅' if models_ok else '❌'}")
    print(f"   Guardian: {'✅' if guardian else '❌'}")
    print(f"   Analysis: {'✅' if analysis_ok else '❌'}")
    
    if config_ok and models_ok and guardian and analysis_ok:
        print("\n🎉 Guardian Layer is working properly!")
    else:
        print("\n⚠️ Guardian Layer has issues that need to be fixed.")

if __name__ == "__main__":
    asyncio.run(main())
