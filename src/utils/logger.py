"""
Logging utilities for AI agent system
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO, 
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file to log to
        
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class AuditLogger:
    """
    Specialized logger for audit trails and decision tracking
    """
    
    def __init__(self, log_file: str = "audit.log"):
        self.logger = setup_logger("AuditLogger", logging.INFO, log_file)
    
    def log_decision(self, message_id: str, decision_data: dict):
        """Log a decision made by the AI agent"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "decision",
            "message_id": message_id,
            "data": decision_data
        }
        self.logger.info(f"DECISION: {audit_entry}")
    
    def log_communication(self, message_id: str, communication_data: dict):
        """Log a communication sent by the system"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "communication",
            "message_id": message_id,
            "data": communication_data
        }
        self.logger.info(f"COMMUNICATION: {audit_entry}")
    
    def log_action_execution(self, message_id: str, action_data: dict):
        """Log the execution of an action"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "action_execution",
            "message_id": message_id,
            "data": action_data
        }
        self.logger.info(f"ACTION: {audit_entry}")
    
    def log_error(self, message_id: str, error_data: dict):
        """Log an error that occurred during processing"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "error",
            "message_id": message_id,
            "data": error_data
        }
        self.logger.error(f"ERROR: {audit_entry}")
