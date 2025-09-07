"""Reasoning Agent for deep contextual analysis using heavyweight LLM"""

import json
import base64
import aiohttp
from typing import List, Dict, Any, Optional
from .base_agent import AIAgent
from ..models import InputMessage, AgentResult, ThreatCategory, ContentType
from ..config import config

class ReasoningAgent(AIAgent):
    """Heavy-duty reasoning agent using advanced LLM for complex threat detection"""
    
    def __init__(self):
        super().__init__(
            name="ReasoningAgent",
            api_key=config.model.blackbox_api_key,
            confidence_threshold=0.8  # High confidence threshold for final decisions
        )
        self.base_url = config.model.blackbox_base_url

        # NEW: pick enum for sexual solicitation; fallback to NSFW if not present
        try:
            self.SEX_SOL = ThreatCategory.SEXUAL_SOLICITATION
        except AttributeError:
            self.SEX_SOL = ThreatCategory.NSFW
    
    def can_process(self, message: InputMessage) -> bool:
        """This agent can process any type of content"""
        return True
    
    async def analyze(self, message: InputMessage) -> AgentResult:
        """Perform deep contextual analysis of the content"""
        try:
            # Perform comprehensive reasoning analysis
            ai_result = await self._reasoning_analysis(message)
            
            return self._create_result(
                confidence=ai_result['confidence'],
                risk_score=ai_result['risk_score'],
                threats=ai_result['threats'],
                explanation=ai_result['explanation'],
                processing_time=0.0,
                metadata={
                    'analysis_type': 'deep_reasoning',
                    'context_considered': True,
                    'severity_level': ai_result.get('severity_level', 'unknown'),
                    'recommended_action': ai_result.get('recommended_action', 'review')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Reasoning analysis failed: {str(e)}")
            return self._create_result(
                confidence=0.4,
                risk_score=0.6,  # Conservative high estimate for safety
                threats=[],
                explanation=f"Deep reasoning analysis failed: {str(e)}",
                processing_time=0.0
            )
    
    async def _reasoning_analysis(self, message: InputMessage) -> Dict[str, Any]:
        """Perform deep reasoning analysis using advanced LLM"""
        try:
            # Prepare comprehensive prompt
            prompt = self._build_reasoning_prompt(message)
            
            # Prepare message content
            message_content = [{"type": "text", "text": prompt}]
            
            # Add image if available
            if message.image_data or message.image_path:
                image_base64 = None
                if message.image_data:
                    image_base64 = base64.b64encode(message.image_data).decode('utf-8')
                elif message.image_path:
                    with open(message.image_path, 'rb') as f:
                        image_data = f.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                
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
                "temperature": config.model.reasoning_model_temperature,
                "max_tokens": 1000
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
                            threats = self._parse_threats(ai_result.get('threats', []))
                            
                            return {
                                'risk_score': float(ai_result.get('risk_score', 0.0)),
                                'threats': threats,
                                'confidence': float(ai_result.get('confidence', 0.5)),
                                'explanation': ai_result.get('explanation', 'Deep reasoning analysis completed'),
                                'severity_level': ai_result.get('severity_level', 'unknown'),
                                'recommended_action': ai_result.get('recommended_action', 'review')
                            }
                        except json.JSONDecodeError:
                            self.logger.warning("Failed to parse reasoning AI response as JSON")
                            return self._fallback_reasoning_result()
                    else:
                        self.logger.error(f"Reasoning AI API request failed with status {response.status}")
                        return self._fallback_reasoning_result()
                        
        except Exception as e:
            self.logger.error(f"Reasoning AI analysis failed: {str(e)}")
            return self._fallback_reasoning_result()
    
    def _build_reasoning_prompt(self, message: InputMessage) -> str:
        """Build comprehensive reasoning prompt"""
        text_content = message.text or ""
        has_image = bool(message.image_data or message.image_path)
        
        prompt = f"""
        You are an expert child safety analyst. Perform a deep, contextual analysis of this content to determine if it poses any risk to children.

        CONTENT TO ANALYZE:
        Text: "{text_content}"
        Has Image: {has_image}

        ANALYSIS FRAMEWORK:
        
        1. CONTEXTUAL UNDERSTANDING:
           - What is the overall tone and intent?
           - Are there hidden meanings or coded language?
           - Does this content try to build inappropriate relationships?
           
        2. GROOMING PATTERN DETECTION:
           - Trust-building language ("you're special", "our secret")
           - Isolation tactics ("don't tell parents")
           - Boundary testing ("just between us")
           - Gift offering or special treatment promises
           
        3. PSYCHOLOGICAL MANIPULATION:
           - Emotional manipulation tactics
           - Attempts to normalize inappropriate behavior
           - Creating dependency or fear
           
        4. THREAT CATEGORIES TO ASSESS:
           - PROFANITY: Inappropriate language
           - HATE_SPEECH: Discriminatory or hateful content
           - GROOMING: Predatory behavior targeting minors
           - SELF_HARM: Content promoting self-injury or suicide
           - SEXUAL_SOLICITATION: Requests for sexual content or images ("send nudes", "dick pic")
           - NSFW: General adult sexual content (non-solicitation)
           - VIOLENCE: Violent or threatening content
           - WEAPONS: Dangerous weapons or violence promotion
           - PREDATORY: General predatory behavior
           - CSAM: Child sexual abuse material indicators
           
        5. SEVERITY ASSESSMENT:
           - LOW_RISK: Mildly inappropriate but not dangerous
           - MEDIUM_RISK: Concerning content requiring parent notification
           - HIGH_RISK: Immediate threat requiring intervention
           - CRITICAL: Extremely dangerous, potential legal issues
           
        6. RECOMMENDED ACTIONS:
           - ALLOW: Content is safe
           - EDUCATE: Allow with educational message
           - WARN: Show warning to child and notify parents
           - BLOCK: Block content and alert parents immediately
           - ESCALATE: Block and consider legal/authority notification

        Respond with a JSON object:
        {{
            "risk_score": float between 0.0 and 1.0,
            "threats": list of detected threat categories,
            "confidence": float between 0.0 and 1.0,
            "explanation": detailed explanation of analysis and reasoning,
            "severity_level": one of LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL,
            "recommended_action": one of ALLOW, EDUCATE, WARN, BLOCK, ESCALATE,
            "reasoning_details": {{
                "context_analysis": "analysis of context and intent",
                "pattern_detection": "grooming or manipulation patterns found",
                "risk_factors": ["list", "of", "specific", "risk", "factors"],
                "protective_factors": ["list", "of", "mitigating", "factors"]
            }}
        }}
        """
        
        return prompt
    
    def _parse_threats(self, threat_strings: List[str]) -> List[ThreatCategory]:
        """Parse threat strings into ThreatCategory enums"""
        threats: List[ThreatCategory] = []
        for threat_str in threat_strings:
            try:
                threat_lower = (threat_str or "").strip().lower()
                if threat_lower == 'profanity':
                    threats.append(ThreatCategory.PROFANITY)
                elif threat_lower == 'hate_speech' or threat_lower == 'hate':
                    threats.append(ThreatCategory.HATE_SPEECH)
                elif threat_lower == 'grooming':
                    threats.append(ThreatCategory.GROOMING)
                elif threat_lower == 'self_harm':
                    threats.append(ThreatCategory.SELF_HARM)
                elif threat_lower == 'nsfw':
                    threats.append(ThreatCategory.NSFW)
                elif threat_lower == 'violence':
                    threats.append(ThreatCategory.VIOLENCE)
                elif threat_lower == 'weapons':
                    threats.append(ThreatCategory.WEAPONS)
                elif threat_lower == 'predatory':
                    threats.append(ThreatCategory.PREDATORY)
                elif threat_lower == 'csam':
                    threats.append(ThreatCategory.CSAM)
                elif threat_lower == 'sexual_solicitation':
                    # NEW: map to SEXUAL_SOLICITATION if it exists, else to NSFW
                    threats.append(ThreatCategory.SEXUAL_SOLICITATION)
            except ValueError:
                continue
        return threats
    
    def _fallback_reasoning_result(self) -> Dict[str, Any]:
        """Fallback result when reasoning analysis fails"""
        return {
            'risk_score': 0.6,  # Conservative estimate
            'threats': [],
            'confidence': 0.4,
            'explanation': 'Deep reasoning analysis unavailable, using conservative safety estimate',
            'severity_level': 'MEDIUM_RISK',
            'recommended_action': 'WARN'
        }
