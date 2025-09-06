"""Education Agent for generating child-friendly explanations and parent notifications"""

import json
import aiohttp
from typing import Dict, Any, List
from .base_agent import AIAgent
from ..models import InputMessage, AgentResult, ThreatCategory, RiskLevel, EducationContent
from ..config import config

class EducationAgent(AIAgent):
    """Agent for generating educational content and parent notifications"""
    
    def __init__(self):
        super().__init__(
            name="EducationAgent",
            api_key=config.model.blackbox_api_key,
            confidence_threshold=0.7
        )
        self.base_url = config.model.blackbox_base_url
    
    def can_process(self, message: InputMessage) -> bool:
        """This agent can process any content to generate educational responses"""
        return True
    
    async def analyze(self, message: InputMessage) -> AgentResult:
        """This agent doesn't analyze content, it generates educational responses"""
        return self._create_result(
            confidence=1.0,
            risk_score=0.0,
            threats=[],
            explanation="Education agent ready to generate content",
            processing_time=0.0
        )
    
    async def generate_education_content(
        self, 
        message: InputMessage, 
        risk_level: RiskLevel, 
        threats: List[ThreatCategory],
        overall_explanation: str
    ) -> EducationContent:
        """Generate educational content for children and parents"""
        try:
            # Generate child-friendly message
            child_message = await self._generate_child_message(message, risk_level, threats)
            
            # Generate parent notification
            parent_message = await self._generate_parent_message(message, risk_level, threats, overall_explanation)
            
            # Generate severity explanation
            severity_explanation = self._generate_severity_explanation(risk_level, threats)
            
            # Generate recommended actions
            recommended_actions = self._generate_recommended_actions(risk_level, threats)
            
            # Generate educational resources
            resources = self._generate_resources(threats)
            
            return EducationContent(
                child_message=child_message,
                parent_message=parent_message,
                severity_explanation=severity_explanation,
                recommended_actions=recommended_actions,
                resources=resources
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate education content: {str(e)}")
            return self._fallback_education_content(risk_level, threats)
    
    async def _generate_child_message(
        self, 
        message: InputMessage, 
        risk_level: RiskLevel, 
        threats: List[ThreatCategory]
    ) -> str:
        """Generate age-appropriate message for the child"""
        try:
            threat_descriptions = [threat.value.replace('_', ' ') for threat in threats]
            
            prompt = f"""
            Generate a gentle, age-appropriate message for a child (ages 8-16) explaining why certain content might not be safe.
            
            Risk Level: {risk_level.value}
            Detected Issues: {', '.join(threat_descriptions) if threat_descriptions else 'general safety concern'}
            
            Guidelines:
            - Use simple, clear language
            - Be supportive and non-scary
            - Focus on safety and kindness
            - Encourage talking to trusted adults
            - Don't repeat harmful content
            - Keep it brief (2-3 sentences max)
            
            Examples:
            - For profanity: "Some words in this message might hurt people's feelings. Let's choose kind words that make others feel good!"
            - For inappropriate content: "This content isn't quite right for you. It's always okay to talk to a grown-up you trust if you see something that makes you uncomfortable."
            
            Generate an appropriate message for this situation.
            """
            
            child_message = await self._make_education_api_request(prompt)
            return child_message or self._fallback_child_message(risk_level)
            
        except Exception as e:
            self.logger.error(f"Failed to generate child message: {str(e)}")
            return self._fallback_child_message(risk_level)
    
    async def _generate_parent_message(
        self, 
        message: InputMessage, 
        risk_level: RiskLevel, 
        threats: List[ThreatCategory],
        overall_explanation: str
    ) -> str:
        """Generate detailed message for parents"""
        try:
            threat_descriptions = [threat.value.replace('_', ' ') for threat in threats]
            content_summary = self._create_content_summary(message)
            
            prompt = f"""
            Generate a clear, informative message for parents about content their child encountered.
            
            Risk Level: {risk_level.value}
            Detected Threats: {', '.join(threat_descriptions) if threat_descriptions else 'none'}
            Content Summary: {content_summary}
            Analysis: {overall_explanation}
            
            Include:
            - Clear explanation of what was detected
            - Why it's concerning for children
            - What action was taken (blocked/warned/allowed)
            - Recommended next steps for parents
            - Reassurance about the safety system
            
            Keep it factual, clear, and actionable. Avoid technical jargon.
            """
            
            parent_message = await self._make_education_api_request(prompt)
            return parent_message or self._fallback_parent_message(risk_level, threats)
            
        except Exception as e:
            self.logger.error(f"Failed to generate parent message: {str(e)}")
            return self._fallback_parent_message(risk_level, threats)
    
    async def _make_education_api_request(self, prompt: str) -> str:
        """Make API request for education content generation"""
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "blackbox",
                "temperature": 0.3,  # Lower temperature for more consistent educational content
                "max_tokens": 300
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self._prepare_api_headers(),
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                        return content.strip()
                    else:
                        self.logger.error(f"Education API request failed with status {response.status}")
                        return ""
                        
        except Exception as e:
            self.logger.error(f"Education API request failed: {str(e)}")
            return ""
    
    def _create_content_summary(self, message: InputMessage) -> str:
        """Create a brief summary of the content for parents"""
        summary_parts = []
        
        if message.text:
            text_length = len(message.text)
            if text_length > 100:
                summary_parts.append(f"Text message ({text_length} characters)")
            else:
                summary_parts.append("Short text message")
        
        if message.image_data or message.image_path:
            summary_parts.append("Image content")
        
        return " with ".join(summary_parts) if summary_parts else "Content"
    
    def _generate_severity_explanation(self, risk_level: RiskLevel, threats: List[ThreatCategory]) -> str:
        """Generate explanation of severity level"""
        explanations = {
            RiskLevel.SAFE: "Content appears safe and appropriate for children.",
            RiskLevel.LOW: "Content has minor concerns but is generally acceptable with guidance.",
            RiskLevel.MEDIUM: "Content has concerning elements that require parental awareness and discussion.",
            RiskLevel.HIGH: "Content poses significant risks and has been blocked for child safety."
        }
        
        base_explanation = explanations.get(risk_level, "Content requires review.")
        
        if threats:
            threat_names = [threat.value.replace('_', ' ').title() for threat in threats]
            threat_text = ", ".join(threat_names)
            base_explanation += f" Specific concerns: {threat_text}."
        
        return base_explanation
    
    def _generate_recommended_actions(self, risk_level: RiskLevel, threats: List[ThreatCategory]) -> List[str]:
        """Generate recommended actions for parents"""
        actions = []
        
        if risk_level == RiskLevel.SAFE:
            actions.append("No immediate action required")
            actions.append("Continue monitoring your child's online activity")
        
        elif risk_level == RiskLevel.LOW:
            actions.append("Discuss appropriate online behavior with your child")
            actions.append("Review and reinforce family internet rules")
        
        elif risk_level == RiskLevel.MEDIUM:
            actions.append("Have a conversation with your child about what they encountered")
            actions.append("Review privacy settings and parental controls")
            actions.append("Consider additional monitoring tools")
        
        elif risk_level == RiskLevel.HIGH:
            actions.append("Discuss this incident immediately with your child")
            actions.append("Review all recent online activity")
            actions.append("Consider restricting internet access temporarily")
            actions.append("Contact school counselor or child safety resources if needed")
        
        # Add threat-specific actions
        if ThreatCategory.GROOMING in threats or ThreatCategory.PREDATORY in threats:
            actions.append("Save screenshots/evidence of the content")
            actions.append("Consider reporting to local authorities")
            actions.append("Review who your child communicates with online")
        
        if ThreatCategory.SELF_HARM in threats:
            actions.append("Check in with your child about their emotional wellbeing")
            actions.append("Consider professional counseling support")
        
        return actions
    
    def _generate_resources(self, threats: List[ThreatCategory]) -> List[str]:
        """Generate relevant educational resources"""
        resources = [
            "Common Sense Media - Age-appropriate content guides",
            "National Center for Missing & Exploited Children - Online safety tips",
            "ConnectSafely.org - Parent guides for social media safety"
        ]
        
        if ThreatCategory.GROOMING in threats or ThreatCategory.PREDATORY in threats:
            resources.extend([
                "FBI's Internet Crime Complaint Center (IC3)",
                "National Child Abuse Hotline: 1-800-4-A-CHILD (1-800-422-4453)"
            ])
        
        if ThreatCategory.SELF_HARM in threats:
            resources.extend([
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741"
            ])
        
        if ThreatCategory.HATE_SPEECH in threats:
            resources.extend([
                "Anti-Defamation League - Hate speech education resources",
                "Teaching Tolerance - Classroom and family resources"
            ])
        
        return resources
    
    def _fallback_child_message(self, risk_level: RiskLevel) -> str:
        """Fallback child message when AI generation fails"""
        messages = {
            RiskLevel.SAFE: "Great job staying safe online! Keep being smart about what you share and see.",
            RiskLevel.LOW: "This content might not be the best choice. Remember to always choose kind and positive things online!",
            RiskLevel.MEDIUM: "This content isn't quite right for you. It's always okay to talk to a grown-up you trust about things you see online.",
            RiskLevel.HIGH: "This content has been blocked to keep you safe. Please talk to a parent or trusted adult about what happened."
        }
        return messages.get(risk_level, "Please talk to a trusted adult about this content.")
    
    def _fallback_parent_message(self, risk_level: RiskLevel, threats: List[ThreatCategory]) -> str:
        """Fallback parent message when AI generation fails"""
        threat_text = ", ".join([t.value.replace('_', ' ') for t in threats]) if threats else "general safety concerns"
        
        return f"""
        Your child encountered content with {risk_level.value} risk level.
        
        Detected issues: {threat_text}
        
        Our safety system has taken appropriate action to protect your child. 
        We recommend discussing online safety with your child and reviewing their internet activity.
        
        If you have concerns, please consider consulting with school counselors or child safety resources.
        """
    
    def _fallback_education_content(self, risk_level: RiskLevel, threats: List[ThreatCategory]) -> EducationContent:
        """Fallback education content when generation fails"""
        return EducationContent(
            child_message=self._fallback_child_message(risk_level),
            parent_message=self._fallback_parent_message(risk_level, threats),
            severity_explanation=self._generate_severity_explanation(risk_level, threats),
            recommended_actions=self._generate_recommended_actions(risk_level, threats),
            resources=self._generate_resources(threats)
        )
