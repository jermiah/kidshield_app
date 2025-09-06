"""Utility functions for the Guardian App Pipeline"""

import time
import logging
import hashlib
import json
from typing import Any, Dict, Optional
from functools import wraps
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging for the application"""
    logger = logging.getLogger("guardian_app")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Add timing info to result if it's a dict
        if isinstance(result, dict):
            result['processing_time'] = end_time - start_time
        
        return result
    return wrapper

def anonymize_text(text: str, preserve_length: bool = True) -> str:
    """Anonymize text while preserving structure for analysis"""
    if not text:
        return text
    
    # Create a hash of the text
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
    
    if preserve_length:
        # Replace with asterisks but keep structure
        anonymized = ''.join('*' if c.isalnum() else c for c in text)
        return f"[ANON_{text_hash}] {anonymized}"
    else:
        return f"[ANONYMIZED_TEXT_{text_hash}]"

def sanitize_for_logging(data: Any) -> Any:
    """Sanitize data for safe logging (remove sensitive info)"""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key.lower() in ['api_key', 'token', 'password', 'secret']:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_for_logging(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]
    elif isinstance(data, str) and len(data) > 100:
        # Truncate long strings
        return data[:100] + "..."
    else:
        return data

def validate_image_size(image_data: bytes, max_size_mb: int = 10) -> bool:
    """Validate image size"""
    if not image_data:
        return False
    
    size_mb = len(image_data) / (1024 * 1024)
    return size_mb <= max_size_mb

def generate_message_id() -> str:
    """Generate a unique message ID"""
    timestamp = datetime.now().isoformat()
    hash_input = f"{timestamp}_{time.time()}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:12]

def calculate_weighted_risk_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted average risk score from multiple agents"""
    if not scores or not weights:
        return 0.0
    
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for agent, score in scores.items():
        weight = weights.get(agent, 1.0)
        total_weighted_score += score * weight
        total_weight += weight
    
    return total_weighted_score / total_weight if total_weight > 0 else 0.0

def format_threats_for_display(threats: list) -> str:
    """Format threat categories for human-readable display"""
    if not threats:
        return "No threats detected"
    
    threat_names = [threat.value.replace('_', ' ').title() for threat in threats]
    
    if len(threat_names) == 1:
        return threat_names[0]
    elif len(threat_names) == 2:
        return f"{threat_names[0]} and {threat_names[1]}"
    else:
        return f"{', '.join(threat_names[:-1])}, and {threat_names[-1]}"

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 100, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limits"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a new API call"""
        self.calls.append(time.time())

# Global logger instance
logger = setup_logging()
