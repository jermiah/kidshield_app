#!/usr/bin/env python3
"""Simple API test for Guardian Layer"""

import os
import sys
import asyncio
import aiohttp
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_env_loading():
    """Test environment variable loading"""
    print("🔧 Testing Environment Variables...")
    
    try:
        from config import config
        print("✅ Config module loaded successfully")
        
        # Check API key
        api_key = config.model.blackbox_api_key
        if api_key and api_key != "ADD A KEY HERE" and api_key != "your_blackbox_api_key_here":
            print(f"✅ Valid API Key loaded: {api_key[:15]}...")
            return api_key
        else:
            print("❌ API Key not properly configured in .env file")
            print(f"   Current value: {api_key}")
            return None
            
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return None

async def test_blackbox_api(api_key):
    """Test direct Blackbox API connection"""
    print("\n🌐 Testing Blackbox AI API Connection...")
    
    if not api_key:
        print("❌ No valid API key to test")
        return False
    
    try:
        prompt = """
        Analyze this text for child safety: "Hello, how are you today?"
        
        Respond with JSON:
        {"risk_score": 0.0, "threats": [], "confidence": 1.0, "explanation": "Safe greeting"}
        """
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "blackboxai/openai/gpt-4",
            "temperature": 0.1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.blackbox.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"✅ API connection successful")
                    print(f"✅ Response received: {content[:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ API request failed with status {response.status}")
                    print(f"   Error: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ API request timed out")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and imports"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'config.py',
        'models.py', 
        'guardian_layer.py',
        'agents/text_classifier.py',
        'agents/image_classifier.py',
        'schemas/guardian_schemas.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_basic_imports():
    """Test basic imports without relative imports"""
    print("\n📦 Testing Basic Imports...")
    
    try:
        # Test config
        from config import config
        print("✅ Config import successful")
        
        # Test models
        from models import InputMessage, ThreatCategory, ContentType
        print("✅ Models import successful")
        
        # Test schemas
        from schemas.guardian_schemas import GuardianRequest, GuardianResponse
        print("✅ Schemas import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Guardian Layer API & Configuration Test")
    print("=" * 50)
    
    # Test file structure
    files_ok = test_file_structure()
    
    # Test basic imports
    imports_ok = test_basic_imports()
    
    # Test environment loading
    api_key = test_env_loading()
    env_ok = api_key is not None
    
    # Test API connection
    if api_key:
        api_ok = await test_blackbox_api(api_key)
    else:
        api_ok = False
        print("\n🌐 Skipping API test (no valid API key)")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   File Structure: {'✅' if files_ok else '❌'}")
    print(f"   Basic Imports:  {'✅' if imports_ok else '❌'}")
    print(f"   Environment:    {'✅' if env_ok else '❌'}")
    print(f"   API Connection: {'✅' if api_ok else '❌'}")
    
    if files_ok and imports_ok and env_ok and api_ok:
        print("\n🎉 Guardian Layer core functionality is working!")
        print("   The API key is properly loaded and Blackbox AI is accessible.")
    elif files_ok and imports_ok and env_ok:
        print("\n⚠️ Guardian Layer is mostly working, but API connection failed.")
        print("   Check your API key or internet connection.")
    else:
        print("\n❌ Guardian Layer has configuration issues.")
        
        if not env_ok:
            print("   → Update your .env file with a valid BLACKBOX_API_KEY")
        if not imports_ok:
            print("   → Fix import/dependency issues")
        if not files_ok:
            print("   → Missing required files")

if __name__ == "__main__":
    asyncio.run(main())
