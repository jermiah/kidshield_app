"""Guardian Layer - Simplified 3-step pipeline: Input → Guardrail Models → Structured Output"""

import time
import asyncio
from typing import Optional, List
from .schemas.guardian_schemas import (
    GuardianRequest, 
    GuardianResponse, 
    RiskResult, 
    RiskCategory,
    GuardianStatus,
    generate_input_id,
    determine_status,
    STANDARD_TEXT_CATEGORIES,
    STANDARD_IMAGE_CATEGORIES
)
from .models import InputMessage, ThreatCategory
from .agents.text_classifier import TextClassifierAgent
from .agents.image_classifier import ImageClassifierAgent
from .utils import logger

class GuardianLayer:
    """Simplified Guardian Layer for 3-step processing"""
    
    def __init__(self):
        self.logger = logger
        self.text_classifier = TextClassifierAgent()
        self.image_classifier = ImageClassifierAgent()
        
        # Threat category to standard category mapping
        self.threat_to_text_category = {
    ThreatCategory.PROFANITY: "profanity",
    ThreatCategory.HATE_SPEECH: "hate_speech",
    ThreatCategory.GROOMING: "grooming",
    ThreatCategory.SELF_HARM: "self_harm",
    ThreatCategory.VIOLENCE: "violence",
    ThreatCategory.PREDATORY: "predatory",
    ThreatCategory.CSAM: "csam",  # <- recommend using "csam" explicitly
    ThreatCategory.NSFW: "sexual",  # optional: keep “sexual” as general adult/NSFW
    # ✅ add this:
    ThreatCategory.SEXUAL_SOLICITATION: "sexual_solicitation",
}
        
        self.threat_to_image_category = {
            ThreatCategory.NSFW: "nudity",
            ThreatCategory.VIOLENCE: "violence",
            ThreatCategory.WEAPONS: "weapons", 
            ThreatCategory.SELF_HARM: "self_harm",
            ThreatCategory.CSAM: "inappropriate"
        }
    
    async def process_request(self, request: GuardianRequest) -> GuardianResponse:
        """
        Process guardian request through 3-step pipeline
        
        Args:
            request: Guardian request with text/image content
            
        Returns:
            Structured guardian response
        """
        start_time = time.time()
        input_id = generate_input_id()
        
        try:
            self.logger.info(f"Processing guardian request {input_id}")
            
            # Step 1: Input Layer - Convert to InputMessage
            message = self._create_input_message(request, input_id)
            
            # Step 2: Guardrail Models - Run classifiers
            text_risks = await self._analyze_text(message)
            image_risks = await self._analyze_image(message)
            
            # Step 3: Structured Output - Format response
            results = RiskResult(
                text_risk=text_risks,
                image_risk=image_risks
            )
            
            status = determine_status(text_risks, image_risks)
            processing_time = time.time() - start_time
            
            response = GuardianResponse(
                input_id=input_id,
                results=results,
                status=status,
                processing_time=processing_time
            )
            
            self.logger.info(
                f"Guardian request {input_id} completed: status={status.value}, "
                f"text_risks={len(text_risks)}, image_risks={len(image_risks)}, "
                f"processing_time={processing_time:.2f}s"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Guardian request {input_id} failed: {str(e)}")
            processing_time = time.time() - start_time
            
            # Return error response
            return GuardianResponse(
                input_id=input_id,
                results=RiskResult(),
                status=GuardianStatus.ERROR,
                processing_time=processing_time
            )
    
    def _create_input_message(self, request: GuardianRequest, input_id: str) -> InputMessage:
        """Convert GuardianRequest to InputMessage"""
        # Handle base64 image if provided
        image_data = None
        if request.image:
            try:
                import base64
                image_data = base64.b64decode(request.image)
            except Exception as e:
                self.logger.warning(f"Failed to decode base64 image: {str(e)}")
        
        return InputMessage(
            message_id=input_id,
            text=request.text,
            image_data=image_data,
            user_id=request.user_id
        )
    
    async def _analyze_text(self, message: InputMessage) -> List[RiskCategory]:
        """Analyze text content and return structured risk categories"""
        if not self.text_classifier.can_process(message):
            return []
        
        try:
            result = await self.text_classifier.process(message)
            if not result:
                return []
            
            # Convert threats to standard categories
            risk_categories = []
            
            # Add detected threats with their risk scores
            for threat in result.threats_detected:
                if threat in self.threat_to_text_category:
                    category = self.threat_to_text_category[threat]
                    risk_categories.append(RiskCategory(
                        category=category,
                        score=result.risk_score
                    ))
            
            # If no specific threats but has risk score, add general categories
            if not risk_categories and result.risk_score > 0.1:
                # Distribute risk score across likely categories based on confidence
                if result.risk_score > 0.5:
                    risk_categories.append(RiskCategory(
                        category="inappropriate",
                        score=result.risk_score
                    ))
            
            return risk_categories
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {str(e)}")
            return []
    
    async def _analyze_image(self, message: InputMessage) -> List[RiskCategory]:
        """Analyze image content and return structured risk categories"""
        if not self.image_classifier.can_process(message):
            return []
        
        try:
            result = await self.image_classifier.process(message)
            if not result:
                return []
            
            # Convert threats to standard categories
            risk_categories = []
            
            # Add detected threats with their risk scores
            for threat in result.threats_detected:
                if threat in self.threat_to_image_category:
                    category = self.threat_to_image_category[threat]
                    risk_categories.append(RiskCategory(
                        category=category,
                        score=result.risk_score
                    ))
            
            # If no specific threats but has risk score, add general categories
            if not risk_categories and result.risk_score > 0.1:
                if result.risk_score > 0.5:
                    risk_categories.append(RiskCategory(
                        category="inappropriate",
                        score=result.risk_score
                    ))
            
            return risk_categories
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {str(e)}")
            return []
    
    def get_status(self) -> dict:
        """Get guardian layer status"""
        return {
            "status": "ready",
            "classifiers": {
                "text_classifier": self.text_classifier is not None,
                "image_classifier": self.image_classifier is not None
            },
            "supported_categories": {
                "text": STANDARD_TEXT_CATEGORIES,
                "image": STANDARD_IMAGE_CATEGORIES
            }
        }

# Global guardian layer instance
guardian_layer = GuardianLayer()
