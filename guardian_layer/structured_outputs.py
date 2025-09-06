"""OpenAI Structured Outputs integration for Guardian Layer"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

from .schemas.guardian_schemas import RiskCategory, GuardianStatus
from .config import config
from .utils import logger

class TextRiskAnalysis(BaseModel):
    """Structured output schema for text risk analysis"""
    categories: List[RiskCategory]
    overall_risk_score: float
    explanation: str

class ImageRiskAnalysis(BaseModel):
    """Structured output schema for image risk analysis"""
    categories: List[RiskCategory]
    overall_risk_score: float
    explanation: str

class StructuredOutputClient:
    """Client for OpenAI structured outputs"""
    
    def __init__(self):
        self.client = None
        self.enabled = config.model.use_structured_outputs
        
        if self.enabled and config.model.openai_api_key:
            try:
                self.client = OpenAI(
                    api_key=config.model.openai_api_key,
                    base_url=config.model.openai_base_url
                )
                logger.info("OpenAI structured outputs client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.enabled = False
        else:
            logger.info("OpenAI structured outputs disabled or no API key provided")
    
    async def analyze_text_structured(self, text: str) -> Optional[TextRiskAnalysis]:
        """Analyze text using OpenAI structured outputs"""
        if not self.enabled or not self.client:
            return None
        
        try:
            prompt = f"""
            Analyze the following text for safety risks and inappropriate content.
            
            Text: "{text}"
            
            Evaluate for these categories:
            - bullying: Content that harasses, intimidates, or threatens others
            - sexual: Sexual content inappropriate for minors
            - self_harm: Content promoting self-injury or suicide
            - hate_speech: Content targeting individuals/groups with hatred
            - violence: Content depicting or promoting violence
            - profanity: Inappropriate language or swearing
            - grooming: Content that could be predatory behavior toward minors
            - predatory: Content showing predatory behavior
            
            For each relevant category, provide a confidence score between 0.0 and 1.0.
            Only include categories with scores > 0.1.
            Provide an overall risk score and brief explanation.
            """
            
            response = self.client.beta.chat.completions.parse(
                model=config.model.openai_model,
                messages=[
                    {"role": "system", "content": "You are a content safety analyzer. Analyze content for risks and provide structured output."},
                    {"role": "user", "content": prompt}
                ],
                response_format=TextRiskAnalysis,
                temperature=0.1
            )
            
            return response.choices[0].message.parsed
            
        except Exception as e:
            logger.error(f"OpenAI text analysis failed: {str(e)}")
            return None
    
    async def analyze_image_structured(self, image_data: bytes) -> Optional[ImageRiskAnalysis]:
        """Analyze image using OpenAI structured outputs"""
        if not self.enabled or not self.client:
            return None
        
        try:
            import base64
            
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """
            Analyze this image for safety risks and inappropriate content.
            
            Evaluate for these categories:
            - nudity: Sexual or nude content inappropriate for minors
            - violence: Violent imagery or weapons
            - weapons: Weapons or dangerous objects
            - self_harm: Content related to self-injury
            - inappropriate: Other inappropriate content for children
            
            For each relevant category, provide a confidence score between 0.0 and 1.0.
            Only include categories with scores > 0.1.
            Provide an overall risk score and brief explanation.
            """
            
            response = self.client.beta.chat.completions.parse(
                model=config.model.openai_model,
                messages=[
                    {"role": "system", "content": "You are a content safety analyzer. Analyze images for risks and provide structured output."},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                response_format=ImageRiskAnalysis,
                temperature=0.1
            )
            
            return response.choices[0].message.parsed
            
        except Exception as e:
            logger.error(f"OpenAI image analysis failed: {str(e)}")
            return None

# Global structured output client
structured_client = StructuredOutputClient()
