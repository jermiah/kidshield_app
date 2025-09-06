"""Cross-Modal Agent for analyzing text and image combinations"""

import json
import base64
import aiohttp
from typing import List, Dict, Any, Optional
from .base_agent import AIAgent
from ..models import InputMessage, AgentResult, ThreatCategory, ContentType
from ..config import config

class CrossModalAgent(AIAgent):
    """Agent for analyzing text-image combinations using multimodal AI"""
    
    def __init__(self):
        super().__init__(
            name="CrossModalAgent",
            api_key=config.model.blackbox_api_key,
            confidence_threshold=config.model.cross_modal_confidence
        )
        self.base_url = config.model.blackbox_base_url
    
    def can_process(self, message: InputMessage) -> bool:
        """Check if this agent can process the message"""
        return message.content_type == ContentType.MULTIMODAL
    
    async def analyze(self, message: InputMessage) -> AgentResult:
        """Analyze text-image combinations for harmful patterns"""
        if message.content_type != ContentType.MULTIMODAL:
            return self._create_result(
                confidence=1.0,
                risk_score=0.0,
                threats=[],
                explanation="No multimodal content to analyze",
                processing_time=0.0
            )
        
        try:
            # Perform cross-modal analysis
            ai_result = await self._cross_modal_analysis(message)
            
            return self._create_result(
                confidence=ai_result['confidence'],
                risk_score=ai_result['risk_score'],
                threats=ai_result['threats'],
                explanation=ai_result['explanation'],
                processing_time=0.0,
                metadata={
                    'analysis_type': 'cross_modal',
                    'text_length': len(message.text) if message.text else 0,
                    'has_image': bool(message.image_data or message.image_path)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Cross-modal analysis failed: {str(e)}")
            return self._create_result(
                confidence=0.3,
                risk_score=0.5,
                threats=[],
                explanation=f"Cross-modal analysis failed: {str(e)}",
                processing_time=0.0
            )
    
    async def _cross_modal_analysis(self, message: InputMessage) -> Dict[str, Any]:
        """Perform cross-modal analysis using Blackbox AI"""
        try:
            # Prepare image data if available
            image_base64 = None
            if message.image_data:
                image_base64 = base64.b64encode(message.image_data).decode('utf-8')
            elif message.image_path:
                with open(message.image_path, 'rb') as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            text_content = message.text or ""
            
            prompt = f"""
            Analyze this text and image combination for harmful content that targets children.
            Pay special attention to:
            
            1. HARMFUL MEMES: Innocent-looking images with harmful text (racist slurs, hate speech)
            2. PREDATORY CONTENT: Harmless photos with predatory captions or grooming language
            3. HIDDEN THREATS: Text that gives harmful context to otherwise safe images
            4. MANIPULATION: Content designed to manipulate or deceive children
            5. INAPPROPRIATE COMBINATIONS: Safe elements that become harmful when combined
            
            Text: "{text_content}"
            
            Look for these threat categories:
            - PROFANITY: Vulgar language combined with images
            - HATE_SPEECH: Discriminatory content in text-image pairs
            - GROOMING: Predatory language with images designed to build trust
            - PREDATORY: Content designed to manipulate or exploit children
            - NSFW: Sexual content in text-image combinations
            - VIOLENCE: Violent themes across text and image
            - NONE: Safe content
            
            Respond with a JSON object:
            {{
                "risk_score": float between 0.0 and 1.0,
                "threats": list of detected threat categories,
                "confidence": float between 0.0 and 1.0,
                "explanation": detailed explanation of cross-modal analysis,
                "context_analysis": explanation of how text and image interact
            }}
            """
            
            # Prepare message content
            message_content = [{"type": "text", "text": prompt}]
            
            if image_base64:
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
                message_content.append(image_content)
            
            payload = {
                "messages": [{"role": "user", "content": message_content}],
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
                                try:
                                    threat_lower = threat_str.lower()
                                    if threat_lower == 'profanity':
                                        threats.append(ThreatCategory.PROFANITY)
                                    elif threat_lower == 'hate_speech':
                                        threats.append(ThreatCategory.HATE_SPEECH)
                                    elif threat_lower == 'grooming':
                                        threats.append(ThreatCategory.GROOMING)
                                    elif threat_lower == 'predatory':
                                        threats.append(ThreatCategory.PREDATORY)
                                    elif threat_lower == 'nsfw':
                                        threats.append(ThreatCategory.NSFW)
                                    elif threat_lower == 'violence':
                                        threats.append(ThreatCategory.VIOLENCE)
                                except ValueError:
                                    continue
                            
                            explanation = ai_result.get('explanation', 'Cross-modal analysis completed')
                            context_analysis = ai_result.get('context_analysis', '')
                            if context_analysis:
                                explanation += f" Context: {context_analysis}"
                            
                            return {
                                'risk_score': float(ai_result.get('risk_score', 0.0)),
                                'threats': threats,
                                'confidence': float(ai_result.get('confidence', 0.5)),
                                'explanation': explanation
                            }
                        except json.JSONDecodeError:
                            self.logger.warning("Failed to parse cross-modal AI response as JSON")
                            return self._fallback_cross_modal_result()
                    else:
                        self.logger.error(f"Cross-modal AI API request failed with status {response.status}")
                        return self._fallback_cross_modal_result()
                        
        except Exception as e:
            self.logger.error(f"Cross-modal AI analysis failed: {str(e)}")
            return self._fallback_cross_modal_result()
    
    def _fallback_cross_modal_result(self) -> Dict[str, Any]:
        """Fallback result when cross-modal analysis fails"""
        return {
            'risk_score': 0.5,
            'threats': [],
            'confidence': 0.3,
            'explanation': 'Cross-modal AI analysis unavailable, using conservative estimate'
        }
    
    def _basic_cross_modal_check(self, message: InputMessage) -> Dict[str, Any]:
        """Basic heuristic checks for text-image combinations"""
        risk_score = 0.0
        threats = []
        explanation = "Basic cross-modal check completed"
        
        if message.text and (message.image_data or message.image_path):
            text_lower = message.text.lower()
            
            # Check for suspicious combinations
            suspicious_phrases = [
                'secret', 'don\'t tell', 'between us', 'our little',
                'special friend', 'just for you', 'private message'
            ]
            
            for phrase in suspicious_phrases:
                if phrase in text_lower:
                    risk_score += 0.3
                    threats.append(ThreatCategory.GROOMING)
                    explanation += f" Detected suspicious phrase: '{phrase}'"
                    break
            
            # Check for meme-like patterns (short text with image)
            if len(message.text.strip()) < 50 and any(word in text_lower for word in ['lol', 'meme', 'funny', 'joke']):
                risk_score += 0.1
                explanation += " Detected potential meme content"
        
        return {
            'risk_score': min(risk_score, 1.0),
            'threats': threats,
            'confidence': 0.6,
            'explanation': explanation
        }
