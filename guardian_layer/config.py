"""Configuration settings for the Guardian App Pipeline"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    blackbox_api_key: str = "sk-FHB-1qkNAyIN7i8DLJAddg"
    blackbox_base_url: str = "https://www.blackbox.ai/api/chat"
    
    # OpenAI configuration for structured outputs
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    use_structured_outputs: bool = True
    
    # Risk thresholds
    low_risk_threshold: float = 0.3
    medium_risk_threshold: float = 0.6
    high_risk_threshold: float = 0.8
    
    # Model settings
    text_model_confidence: float = 0.7
    image_model_confidence: float = 0.75
    cross_modal_confidence: float = 0.8
    reasoning_model_temperature: float = 0.1

@dataclass
class PipelineConfig:
    """Configuration for pipeline behavior"""
    enable_logging: bool = True
    log_level: str = "INFO"
    max_message_length: int = 5000
    max_image_size_mb: int = 10
    
    # Education settings
    child_education_enabled: bool = True
    parent_notification_enabled: bool = True
    
    # Feedback loop
    store_flagged_samples: bool = True
    anonymize_data: bool = True

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.model = ModelConfig()
        self.pipeline = PipelineConfig()
        
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        blackbox_key = os.getenv('BLACKBOX_API_KEY')
        if blackbox_key:
            config.model.blackbox_api_key = blackbox_key
            
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            config.model.openai_api_key = openai_key
            
        log_level = os.getenv('LOG_LEVEL')
        if log_level:
            config.pipeline.log_level = log_level
            
        return config

# Global configuration instance
config = Config.from_env()
