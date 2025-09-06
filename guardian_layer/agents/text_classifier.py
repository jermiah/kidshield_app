"""Text Classifier Agent for detecting harmful text content"""

import json
import aiohttp
from typing import List, Dict, Any
from .base_agent import AIAgent
from ..models import InputMessage, AgentResult, ThreatCategory, ContentType
from ..config import config

class TextClassifierAgent(AIAgent):
    """Agent for classifying text content using Blackbox AI"""
    
    def __init__(self):
        super().__init__(
            name="TextClassifier",
            api_key=config.model.blackbox_api_key,
            confidence_threshold=config.model.text_model_confidence
        )
        self.base_url = config.model.blackbox_base_url
        
        # Keywords for different threat categories
        self.threat_keywords = {
            ThreatCategory.PROFANITY: [
                'fuck', 'shit', 'damn', 'bitch', 'ass', 'hell', 'crap'
            ],
            ThreatCategory.HATE_SPEECH: [
                'hate', 'racist', 'nazi', 'kill yourself', 'die', 'murder'
            ],
            ThreatCategory.GROOMING: [
                'secret', 'don\'t tell', 'special friend', 'our little secret',
                'meet me', 'come over', 'alone', 'private'
            ],
            ThreatCategory.SELF_HARM: [
                'kill myself', 'suicide', 'cut myself', 'hurt myself',
                'end it all', 'not worth living'
            ]
        }
    
    def can_process(self, message: InputMessage) -> bool:
        """Check if this agent can process the message"""
        return message.content_type in [ContentType.TEXT, ContentType.MULTIMODAL]
    
    async def analyze(self, message: InputMessage) -> AgentResult:
        """Analyze text content for harmful patterns"""
        if not message.text:
            return self._create_result(
                confidence=1.0,
                risk_score=0.0,
                threats=[],
                explanation="No text content to analyze",
                processing_time=0.0
            )
        
        # First, do quick keyword-based detection
        keyword_result = self._keyword_analysis(message.text)
        
        # If high risk detected by keywords, escalate to AI analysis
        if keyword_result['risk_score'] > 0.3:
            ai_result = await self._ai_analysis(message.text)
            # Combine results
            combined_risk = max(keyword_result['risk_score'], ai_result['risk_score'])
            combined_threats = list(set(keyword_result['threats'] + ai_result['threats']))
            combined_confidence = min(keyword_result['confidence'], ai_result['confidence'])
            explanation = f"Keyword analysis: {keyword_result['explanation']}. AI analysis: {ai_result['explanation']}"
        else:
            combined_risk = keyword_result['risk_score']
            combined_threats = keyword_result['threats']
            combined_confidence = keyword_result['confidence']
            explanation = keyword_result['explanation']
        
        return self._create_result(
            confidence=combined_confidence,
            risk_score=combined_risk,
            threats=combined_threats,
            explanation=explanation,
            processing_time=0.0,
            metadata={
                'text_length': len(message.text),
                'keyword_matches': keyword_result.get('matches', [])
            }
        )
    
    def _keyword_analysis(self, text: str) -> Dict[str, Any]:
        """Perform quick keyword-based analysis"""
        text_lower = text.lower()
        detected_threats = []
        matches = []
        risk_score = 0.0
        
        for threat_category, keywords in self.threat_keywords.items():
            category_matches = []
            for keyword in keywords:
                if keyword in text_lower:
                    category_matches.append(keyword)
                    matches.append(keyword)
            
            if category_matches:
                detected_threats.append(threat_category)
                # Increase risk based on number of matches and category severity
                category_risk = len(category_matches) * 0.2
                if threat_category in [ThreatCategory.GROOMING, ThreatCategory.SELF_HARM]:
                    category_risk *= 2  # Higher weight for serious threats
                risk_score += category_risk
        
        risk_score = min(risk_score, 1.0)  # Cap at 1.0
        
        explanation = f"Keyword analysis detected {len(matches)} concerning terms"
        if matches:
            explanation += f": {', '.join(matches[:3])}"
            if len(matches) > 3:
                explanation += f" and {len(matches) - 3} more"
        
        return {
            'risk_score': risk_score,
            'threats': detected_threats,
            'confidence': 0.8 if matches else 0.9,
            'explanation': explanation,
            'matches': matches
        }
    
    async def _ai_analysis(self, text: str) -> Dict[str, Any]:
        """Perform AI-based analysis using Blackbox AI"""
        try:
            prompt = f"""
            Analyze the following text for harmful content. Classify it into these categories:
            - PROFANITY: Contains swear words or vulgar language
            - HATE_SPEECH: Contains discriminatory or hateful language
            - GROOMING: Contains predatory language targeting minors
            - SELF_HARM: Contains references to self-harm or suicide
            - NONE: Safe content
            
            Text to analyze: "{text}"
            
            Respond with a JSON object containing:
            - risk_score: float between 0.0 and 1.0
            - threats: list of detected threat categories
            - confidence: float between 0.0 and 1.0
            - explanation: brief explanation of the analysis
            
            Example response:
            {{"risk_score": 0.7, "threats": ["PROFANITY"], "confidence": 0.9, "explanation": "Contains multiple profane words"}}
            """
            
            payload = {
                "messages": [{"role": "user", "content": prompt}],
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
                                    threats.append(ThreatCategory(threat_str.lower()))
                                except ValueError:
                                    continue
                            
                            return {
                                'risk_score': float(ai_result.get('risk_score', 0.0)),
                                'threats': threats,
                                'confidence': float(ai_result.get('confidence', 0.5)),
                                'explanation': ai_result.get('explanation', 'AI analysis completed')
                            }
                        except json.JSONDecodeError:
                            self.logger.warning("Failed to parse AI response as JSON")
                            return self._fallback_ai_result()
                    else:
                        self.logger.error(f"AI API request failed with status {response.status}")
                        return self._fallback_ai_result()
                        
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return self._fallback_ai_result()
    
    def _fallback_ai_result(self) -> Dict[str, Any]:
        """Fallback result when AI analysis fails"""
        return {
            'risk_score': 0.5,
            'threats': [],
            'confidence': 0.3,
            'explanation': 'AI analysis unavailable, using conservative estimate'
        }
