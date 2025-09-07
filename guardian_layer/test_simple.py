#!/usr/bin/env python3
"""Simple configuration and structure test for Guardian Layer"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_env_file():
    """Test .env file and API key"""
    print("🔧 Testing .env File...")
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print("✅ .env file exists")
        
        # Read the .env file
        with open(env_path, 'r') as f:
            content = f.read()
            
        if 'BLACKBOX_API_KEY=' in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('BLACKBOX_API_KEY='):
                    api_key = line.split('=', 1)[1]
                    if api_key and api_key != 'your_blackbox_api_key_here':
                        print(f"✅ API key configured: {api_key[:15]}...")
                        return api_key
                    else:
                        print("❌ API key placeholder not replaced")
                        return None
        else:
            print("❌ BLACKBOX_API_KEY not found in .env file")
            return None
    else:
        print("❌ .env file not found")
        return None

def test_config_loading():
    """Test configuration module"""
    print("\n⚙️ Testing Configuration Loading...")
    
    try:
        from config import config
        print("✅ Config module imported successfully")
        
        # Test API key loading
        api_key = config.model.blackbox_api_key
        if api_key and api_key != "ADD A KEY HERE":
            print(f"✅ API key loaded into config: {api_key[:15]}...")
        else:
            print("❌ API key not properly loaded into config")
            
        # Test other configuration values
        print(f"✅ Text confidence threshold: {config.model.text_model_confidence}")
        print(f"✅ Log level: {config.pipeline.log_level}")
        print(f"✅ Base URL: {config.model.blackbox_base_url}")
        
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_models():
    """Test models import and creation"""
    print("\n📊 Testing Data Models...")
    
    try:
        from models import InputMessage, AgentResult, ThreatCategory, ContentType, RiskLevel
        print("✅ Models imported successfully")
        
        # Test InputMessage creation
        msg = InputMessage(
            message_id="test_123",
            text="Hello world",
            user_id="test_user"
        )
        print(f"✅ InputMessage created: ID={msg.message_id}, Type={msg.content_type}")
        
        # Test AgentResult creation
        result = AgentResult(
            agent_name="TestAgent",
            confidence=0.9,
            risk_score=0.1,
            threats_detected=[ThreatCategory.NONE],
            explanation="Test result",
            processing_time=0.1
        )
        print(f"✅ AgentResult created: Agent={result.agent_name}, Risk={result.risk_score}")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_schemas():
    """Test schema imports"""
    print("\n📋 Testing Schema Definitions...")
    
    try:
        from schemas.guardian_schemas import GuardianRequest, GuardianResponse, RiskCategory
        print("✅ Guardian schemas imported successfully")
        
        # Test GuardianRequest creation
        request = GuardianRequest(
            text="Hello world",
            user_id="test_user"
        )
        print(f"✅ GuardianRequest created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Schemas test failed: {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    print("\n📁 Testing File Structure...")
    
    base_dir = os.path.dirname(__file__)
    required_files = {
        'config.py': 'Configuration module',
        'models.py': 'Data models',
        'guardian_layer.py': 'Main guardian class',
        '.env': 'Environment variables',
        'agents/text_classifier.py': 'Text classifier agent',
        'agents/image_classifier.py': 'Image classifier agent',
        'schemas/guardian_schemas.py': 'Guardian schemas'
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (MISSING)")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🧪 Guardian Layer Configuration & Structure Test")
    print("=" * 55)
    
    # Test file structure
    files_ok = test_file_structure()
    
    # Test .env file
    env_key = test_env_file()
    env_ok = env_key is not None
    
    # Test configuration loading
    config_ok = test_config_loading()
    
    # Test models
    models_ok = test_models()
    
    # Test schemas
    schemas_ok = test_schemas()
    
    print("\n" + "=" * 55)
    print("📋 Test Summary:")
    print(f"   File Structure:    {'✅' if files_ok else '❌'}")
    print(f"   Environment File:  {'✅' if env_ok else '❌'}")
    print(f"   Configuration:     {'✅' if config_ok else '❌'}")
    print(f"   Data Models:       {'✅' if models_ok else '❌'}")
    print(f"   Schema Definitions:{'✅' if schemas_ok else '❌'}")
    
    overall_score = sum([files_ok, env_ok, config_ok, models_ok, schemas_ok])
    print(f"\n📊 Overall Score: {overall_score}/5")
    
    if overall_score == 5:
        print("\n🎉 Guardian Layer is properly configured!")
        print("   ✅ All core components are working")
        print("   ✅ API key is loaded from .env file")
        print("   ✅ Models and schemas are functional")
        print("\n📝 Next steps:")
        print("   → Test API connectivity to Blackbox AI")
        print("   → Run integration tests with real data")
    elif overall_score >= 3:
        print("\n⚠️ Guardian Layer is mostly working with some issues.")
        if not env_ok:
            print("   → Fix API key in .env file")
        if not config_ok:
            print("   → Fix configuration loading")
    else:
        print("\n❌ Guardian Layer has significant issues.")
        print("   → Fix missing files and configuration")

if __name__ == "__main__":
    main()
