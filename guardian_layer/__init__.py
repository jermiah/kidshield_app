"""
Guardian App - AI-Powered Child Safety Pipeline

A comprehensive multi-agent system for protecting children from harmful online content.
Uses progressive filtering with lightweight to heavyweight AI agents that only activate when needed.
"""

from .main import GuardianApp
from .pipeline_orchestrator import GuardianPipeline
from .models import InputMessage, PipelineResult, RiskLevel, ThreatCategory
from .config import config

__version__ = "1.0.0"
__author__ = "Guardian App Team"
__description__ = "AI-Powered Child Safety Pipeline"

__all__ = [
    'GuardianApp',
    'GuardianPipeline', 
    'InputMessage',
    'PipelineResult',
    'RiskLevel',
    'ThreatCategory',
    'config'
]
