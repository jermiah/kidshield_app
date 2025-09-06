"""
Guardian Layer Integration Module

Converts Guardian Layer structured outputs to KidShield App input format
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import Guardian Layer schemas
import sys
from pathlib import Path

# Add guardian layer to path for imports
guardian_path = Path(__file__).parent.parent.parent / "guardian_layer"
if str(guardian_path) not in sys.path:
    sys.path.append(str(guardian_path))

# Try to import Guardian schemas, with fallback
try:
    from schemas.guardian_schemas import GuardianResponse, RiskCategory, GuardianStatus
    GUARDIAN_AVAILABLE = True
except ImportError:
    # Create placeholder types for when guardian layer is not available
    GUARDIAN_AVAILABLE = False
    GuardianResponse = type('GuardianResponse', (), {})
    RiskCategory = type('RiskCategory', (), {})
    GuardianStatus = type('GuardianStatus', (), {})

# Import KidShield models
try:
    from ..models.message import (
        SuspiciousMessage, ChildProfile, MessageMetadata, 
        ThreatType, SeverityLevel
    )
    from ..utils.logger import setup_logger
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.append(str(src_path))
    
    from models.message import (
        SuspiciousMessage, ChildProfile, MessageMetadata, 
        ThreatType, SeverityLevel
    )
    from utils.logger import setup_logger


class GuardianIntegration:
    """
    Integration class for converting Guardian Layer outputs to KidShield inputs
    """
    
    def __init__(self):
        self.logger = setup_logger("GuardianIntegration")
        
        # Mapping from Guardian categories to KidShield threat types
        self.category_mapping = {
            # Text categories
            "bullying": ThreatType.BULLYING,
            "sexual": ThreatType.SEXUAL_CONTENT,
            "grooming": ThreatType.MANIPULATION,
            "predatory": ThreatType.MANIPULATION,
            "self_harm": ThreatType.OTHER,  # Could be mapped to a new type
            "hate_speech": ThreatType.HARASSMENT,
            "violence": ThreatType.VIOLENT_CONTENT,
            "profanity": ThreatType.OTHER,
            
            # Image categories
            "nudity": ThreatType.SEXUAL_CONTENT,
            "weapons": ThreatType.VIOLENT_CONTENT,
            "inappropriate": ThreatType.OTHER
        }
        
        # Severity mapping based on risk scores
        self.severity_thresholds = {
            0.9: SeverityLevel.CRITICAL,
            0.7: SeverityLevel.HIGH,
            0.4: SeverityLevel.MEDIUM,
            0.0: SeverityLevel.LOW
        }
    
    def convert_guardian_response(
        self, 
        guardian_response: Union[Dict[str, Any], Any],
        original_content: str,
        child_profile: Optional[ChildProfile] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> SuspiciousMessage:
        """
        Convert Guardian Layer response to KidShield SuspiciousMessage
        
        Args:
            guardian_response: Guardian layer structured output
            original_content: Original message content that was analyzed
            child_profile: Child profile information (if available)
            additional_metadata: Additional metadata for the message
            
        Returns:
            SuspiciousMessage object ready for KidShield processing
        """
        
        # Handle both dict and GuardianResponse object
        if isinstance(guardian_response, dict):
            response_data = guardian_response
        else:
            response_data = {
                "input_id": guardian_response.input_id,
                "results": {
                    "text_risk": [{"category": r.category, "score": r.score} for r in guardian_response.results.text_risk],
                    "image_risk": [{"category": r.category, "score": r.score} for r in guardian_response.results.image_risk]
                },
                "status": guardian_response.status.value,
                "timestamp": guardian_response.timestamp.isoformat(),
                "processing_time": guardian_response.processing_time
            }
        
        try:
            # Extract risk data
            text_risks = response_data.get("results", {}).get("text_risk", [])
            image_risks = response_data.get("results", {}).get("image_risk", [])
            all_risks = text_risks + image_risks
            
            # Determine primary threat type and severity
            threat_type, severity = self._determine_threat_and_severity(all_risks)
            
            # Create child profile if not provided
            if child_profile is None:
                child_profile = self._create_default_child_profile()
            
            # Create metadata
            metadata = self._create_message_metadata(response_data, additional_metadata)
            
            # Create context with Guardian analysis details
            context = self._create_context(response_data, all_risks)
            
            # Create SuspiciousMessage
            suspicious_message = SuspiciousMessage(
                message_id=response_data.get("input_id", f"guardian_{datetime.now().timestamp()}"),
                content=original_content,
                threat_type=threat_type,
                severity=severity,
                child_profile=child_profile,
                metadata=metadata,
                context=context
            )
            
            self.logger.info(f"Successfully converted Guardian response to SuspiciousMessage: {suspicious_message.message_id}")
            return suspicious_message
            
        except Exception as e:
            self.logger.error(f"Failed to convert Guardian response: {str(e)}")
            raise ValueError(f"Guardian response conversion failed: {str(e)}")
    
    def _determine_threat_and_severity(self, risks: List[Dict[str, Any]]) -> tuple[ThreatType, SeverityLevel]:
        """Determine primary threat type and severity from risk categories"""
        
        if not risks:
            return ThreatType.OTHER, SeverityLevel.LOW
        
        # Find highest scoring risk
        highest_risk = max(risks, key=lambda x: x.get("score", 0))
        highest_score = highest_risk.get("score", 0)
        
        # Map category to threat type
        category = highest_risk.get("category", "other")
        threat_type = self.category_mapping.get(category, ThreatType.OTHER)
        
        # Determine severity based on score
        severity = SeverityLevel.LOW
        for threshold, level in sorted(self.severity_thresholds.items(), reverse=True):
            if highest_score >= threshold:
                severity = level
                break
        
        self.logger.debug(f"Determined threat: {threat_type.value}, severity: {severity.value} (score: {highest_score})")
        return threat_type, severity
    
    def _create_default_child_profile(self) -> ChildProfile:
        """Create a default child profile when none is provided"""
        return ChildProfile(
            child_id="unknown_child",
            age=12,  # Default age
            name="Unknown Child",
            grade_level="Unknown",
            previous_incidents=0,
            parental_notification_preferences={
                "immediate_notification": True,
                "daily_summary": False,
                "weekly_summary": True
            }
        )
    
    def _create_message_metadata(
        self, 
        guardian_data: Dict[str, Any], 
        additional_metadata: Optional[Dict[str, Any]]
    ) -> MessageMetadata:
        """Create MessageMetadata from Guardian response and additional data"""
        
        # Extract timestamp
        timestamp_str = guardian_data.get("timestamp")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Create metadata with defaults and additional data
        base_metadata = {
            "sender_id": "unknown_sender",
            "sender_type": "unknown",
            "platform": "unknown",
            "message_frequency": 1,
            "sender_history": {},
            "confidence_score": 0.5
        }
        
        # Update with additional metadata if provided
        if additional_metadata:
            base_metadata.update(additional_metadata)
        
        # Calculate confidence score from Guardian processing
        processing_time = guardian_data.get("processing_time", 0)
        status = guardian_data.get("status", "safe")
        
        # Adjust confidence based on Guardian analysis
        if status == "flagged":
            base_metadata["confidence_score"] = min(0.9, base_metadata["confidence_score"] + 0.3)
        
        return MessageMetadata(
            sender_id=base_metadata["sender_id"],
            sender_type=base_metadata["sender_type"],
            platform=base_metadata["platform"],
            timestamp=timestamp,
            message_frequency=base_metadata["message_frequency"],
            sender_history=base_metadata["sender_history"],
            confidence_score=base_metadata["confidence_score"]
        )
    
    def _create_context(self, guardian_data: Dict[str, Any], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create context dictionary with Guardian analysis details"""
        
        return {
            "guardian_analysis": {
                "input_id": guardian_data.get("input_id"),
                "status": guardian_data.get("status"),
                "processing_time": guardian_data.get("processing_time"),
                "risk_categories": risks,
                "analysis_timestamp": guardian_data.get("timestamp")
            },
            "risk_breakdown": {
                "text_risks": guardian_data.get("results", {}).get("text_risk", []),
                "image_risks": guardian_data.get("results", {}).get("image_risk", []),
                "total_risks": len(risks),
                "max_risk_score": max([r.get("score", 0) for r in risks]) if risks else 0
            },
            "integration_metadata": {
                "converted_at": datetime.now().isoformat(),
                "integration_version": "1.0.0"
            }
        }
    
    def batch_convert(
        self, 
        guardian_responses: List[Union[Dict[str, Any], Any]],
        original_contents: List[str],
        child_profiles: Optional[List[ChildProfile]] = None,
        additional_metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[SuspiciousMessage]:
        """
        Convert multiple Guardian responses to SuspiciousMessages
        
        Args:
            guardian_responses: List of Guardian responses
            original_contents: List of original message contents
            child_profiles: Optional list of child profiles
            additional_metadata_list: Optional list of additional metadata
            
        Returns:
            List of SuspiciousMessage objects
        """
        
        if len(guardian_responses) != len(original_contents):
            raise ValueError("Number of Guardian responses must match number of original contents")
        
        results = []
        
        for i, (response, content) in enumerate(zip(guardian_responses, original_contents)):
            try:
                child_profile = child_profiles[i] if child_profiles and i < len(child_profiles) else None
                additional_metadata = additional_metadata_list[i] if additional_metadata_list and i < len(additional_metadata_list) else None
                
                suspicious_message = self.convert_guardian_response(
                    response, content, child_profile, additional_metadata
                )
                results.append(suspicious_message)
                
            except Exception as e:
                self.logger.error(f"Failed to convert Guardian response {i}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully converted {len(results)}/{len(guardian_responses)} Guardian responses")
        return results
    
    def validate_guardian_response(self, guardian_response: Union[Dict[str, Any], Any]) -> bool:
        """Validate that Guardian response has required fields"""
        
        try:
            if isinstance(guardian_response, dict):
                required_fields = ["input_id", "results", "status"]
                return all(field in guardian_response for field in required_fields)
            else:
                # Assume it's a GuardianResponse object with proper validation
                return hasattr(guardian_response, 'input_id') and hasattr(guardian_response, 'results')
        except:
            return False
    
    def get_risk_summary(self, guardian_response: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """Get a summary of risks from Guardian response"""
        
        if isinstance(guardian_response, dict):
            response_data = guardian_response
        else:
            response_data = {
                "results": {
                    "text_risk": [{"category": r.category, "score": r.score} for r in guardian_response.results.text_risk],
                    "image_risk": [{"category": r.category, "score": r.score} for r in guardian_response.results.image_risk]
                }
            }
        
        text_risks = response_data.get("results", {}).get("text_risk", [])
        image_risks = response_data.get("results", {}).get("image_risk", [])
        all_risks = text_risks + image_risks
        
        if not all_risks:
            return {"total_risks": 0, "max_score": 0, "categories": []}
        
        return {
            "total_risks": len(all_risks),
            "max_score": max([r.get("score", 0) for r in all_risks]),
            "categories": [r.get("category") for r in all_risks],
            "text_risk_count": len(text_risks),
            "image_risk_count": len(image_risks)
        }


# Convenience function for direct conversion
def convert_guardian_to_kidshield(
    guardian_response: Union[Dict[str, Any], Any],
    original_content: str,
    child_profile: Optional[ChildProfile] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> SuspiciousMessage:
    """
    Convenience function to convert Guardian response to KidShield format
    
    Args:
        guardian_response: Guardian layer structured output
        original_content: Original message content
        child_profile: Optional child profile
        additional_metadata: Optional additional metadata
        
    Returns:
        SuspiciousMessage ready for KidShield processing
    """
    
    integration = GuardianIntegration()
    return integration.convert_guardian_response(
        guardian_response, original_content, child_profile, additional_metadata
    )
