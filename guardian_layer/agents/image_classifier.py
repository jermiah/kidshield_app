"""Image Classifier Agent for detecting harmful visual content"""

import json
import base64
import aiohttp
from typing import List, Dict, Any, Optional
from PIL import Image
import io
from .base_agent import AIAgent
from ..models import InputMessage, AgentResult, ThreatCategory, ContentType
from ..config import config

class ImageClassifierAgent(AIAgent):
    """Agent for classifying image content using Blackbox AI vision capabilities"""
    
    def __init__(self):
        super().__init__(
            name="ImageClassifier",
            api_key=config.model.blackbox_api_key,
            confidence_threshold=config.model.image_model_confidence
        )
        self.base_url = config.model.blackbox_base_url
        self.max_image_size = (1024, 1024)  # Resize large images
    
    def can_process(self, message: InputMessage) -> bool:
        """Check if this agent can process the message"""
        return message.content_type in [ContentType.IMAGE, ContentType.MULTIMODAL]
    
    async def analyze(self, message: InputMessage) -> AgentResult:
        """Analyze image content for harmful visual patterns"""
        if not message.image_data and not message.image_path:
            return self._create_result(
                confidence=1.0,
                risk_score=0.0,
                threats=[],
                explanation="No image content to analyze",
                processing_time=0.0
            )
        
        try:
            # Load and preprocess image
            image_data = await self._load_and_preprocess_image(message)
            if not image_data:
                return self._create_result(
                    confidence=0.5,
                    risk_score=0.3,
                    threats=[],
                    explanation="Failed to load or process image",
                    processing_time=0.0
                )
            
            # Perform AI-based image analysis
            ai_result = await self._ai_image_analysis(image_data)
            
            return self._create_result(
                confidence=ai_result['confidence'],
                risk_score=ai_result['risk_score'],
                threats=ai_result['threats'],
                explanation=ai_result['explanation'],
                processing_time=0.0,
                metadata={
                    'image_processed': True,
                    'analysis_method': 'ai_vision'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {str(e)}")
            return self._create_result(
                confidence=0.3,
                risk_score=0.5,
                threats=[],
                explanation=f"Image analysis failed: {str(e)}",
                processing_time=0.0
            )
    
    async def _load_and_preprocess_image(self, message: InputMessage) -> Optional[bytes]:
        """Load and preprocess image data"""
        try:
            # Get image data
            if message.image_data:
                image_bytes = message.image_data
            elif message.image_path:
                with open(message.image_path, 'rb') as f:
                    image_bytes = f.read()
            else:
                return None
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=85)
            return output_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to preprocess image: {str(e)}")
            return None
    
    async def _ai_image_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """Perform AI-based image analysis using Blackbox AI vision"""
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """
            Analyze this image for harmful content that would be inappropriate for children. 
            Look for these categories:
            - NSFW: Nudity, sexual content, or suggestive material
            - VIOLENCE: Gore, weapons, fighting, or violent imagery  
            - WEAPONS: Guns, knives, or other dangerous weapons
            - NONE: Safe, appropriate content
            
            Respond with a JSON object containing:
            - risk_score: float between 0.0 and 1.0 (0.0 = completely safe, 1.0 = extremely harmful)
            - threats: list of detected threat categories from above
            - confidence: float between 0.0 and 1.0 indicating analysis confidence
            - explanation: brief description of what was detected
            
            Example response:
            {"risk_score": 0.8, "threats": ["NSFW"], "confidence": 0.9, "explanation": "Image contains nudity"}
            """
            
            payload = {
                "messages": [
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "model": "blackbox",
                "temperature": config.model.reasoning_model_temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self._prepare_api_headers(),
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                        
                        try:
                            # Parse JSON response
                            ai_result = json.loads(content)
                            
                            # Convert threat strings to ThreatCategory enums
                            threats = []
                            for threat_str in ai_result.get('threats', []):
                                threat_lower = threat_str.lower()
                                if threat_lower == 'nsfw':
                                    threats.append(ThreatCategory.NSFW)
                                elif threat_lower == 'violence':
                                    threats.append(ThreatCategory.VIOLENCE)
                                elif threat_lower == 'weapons':
                                    threats.append(ThreatCategory.WEAPONS)
                            
                            return {
                                'risk_score': float(ai_result.get('risk_score', 0.0)),
                                'threats': threats,
                                'confidence': float(ai_result.get('confidence', 0.5)),
                                'explanation': ai_result.get('explanation', 'AI image analysis completed')
                            }
                        except json.JSONDecodeError:
                            self.logger.warning("Failed to parse AI image response as JSON")
                            return self._fallback_image_result()
                    else:
                        self.logger.error(f"AI image API request failed with status {response.status}")
                        return self._fallback_image_result()
                        
        except Exception as e:
            self.logger.error(f"AI image analysis failed: {str(e)}")
            return self._fallback_image_result()
    
    def _fallback_image_result(self) -> Dict[str, Any]:
        """Fallback result when AI image analysis fails"""
        return {
            'risk_score': 0.5,
            'threats': [],
            'confidence': 0.3,
            'explanation': 'AI image analysis unavailable, using conservative estimate'
        }
    
    def _basic_image_checks(self, image_data: bytes) -> Dict[str, Any]:
        """Perform basic image validation checks"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Basic checks
            width, height = image.size
            file_size = len(image_data)
            
            # Very basic heuristics (not reliable for actual content detection)
            risk_score = 0.0
            threats = []
            explanation = "Basic image validation passed"
            
            # Check for suspicious dimensions (very wide/tall images sometimes used for inappropriate content)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 3.0:
                risk_score += 0.1
                explanation += ". Unusual aspect ratio detected"
            
            # Check file size (very large images might contain hidden content)
            if file_size > 5 * 1024 * 1024:  # 5MB
                risk_score += 0.1
                explanation += ". Large file size detected"
            
            return {
                'risk_score': min(risk_score, 1.0),
                'threats': threats,
                'confidence': 0.6,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'risk_score': 0.3,
                'threats': [],
                'confidence': 0.4,
                'explanation': f"Basic image check failed: {str(e)}"
            }
