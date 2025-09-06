"""
BlackBox API client for LLM integration
"""

import os
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BlackBoxClient:
    """
    Client for interacting with BlackBox AI API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('BLACKBOX_API_KEY')
        self.base_url = "https://api.blackbox.ai/chat/completions"
        self.model = "blackboxai/openai/chatgpt-4o-latest"
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("BlackBox API key not found. Please set BLACKBOX_API_KEY environment variable.")
    
    def _make_request(self, messages: List[Dict[str, str]], 
                     temperature: float = 0.7, 
                     max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Make a request to the BlackBox API
        
        Args:
            messages: List of message objects with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            API response as dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"BlackBox API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse BlackBox API response: {str(e)}")
            raise
    
    def generate_decision_reasoning(self, message_content: str, threat_type: str, 
                                  severity: str, child_age: int, 
                                  context: Dict[str, Any]) -> str:
        """
        Generate reasoning for decision-making using LLM
        
        Args:
            message_content: The suspicious message content
            threat_type: Type of threat detected
            severity: Severity level
            child_age: Age of the child
            context: Additional context information
            
        Returns:
            Generated reasoning text
        """
        
        prompt = f"""
You are an AI safety expert analyzing a suspicious message sent to a child. 
Provide clear, professional reasoning for the recommended actions.

Message Details:
- Content: "{message_content}"
- Threat Type: {threat_type}
- Severity: {severity}
- Child Age: {child_age}
- Context: {json.dumps(context, indent=2)}

Please provide:
1. A brief analysis of the threat
2. Why this severity level is appropriate
3. Key factors that influenced the decision
4. Reasoning for the recommended actions

Keep the response professional, clear, and focused on child safety.
"""

        messages = [
            {
                "role": "system",
                "content": "You are an expert in child online safety and digital threat assessment. Provide clear, professional analysis for decision-making."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._make_request(messages, temperature=0.3)
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            self.logger.error(f"Failed to generate decision reasoning: {str(e)}")
            return f"Standard assessment for {threat_type} threat at {severity} severity level for child aged {child_age}."
    
    def generate_parent_message(self, child_name: str, threat_type: str, 
                               severity: str, action_taken: str, 
                               tone: str = "informative") -> Dict[str, str]:
        """
        Generate personalized message for parents
        
        Args:
            child_name: Name of the child
            threat_type: Type of threat
            severity: Severity level
            action_taken: Action that was taken
            tone: Tone of the message (urgent, informative, supportive)
            
        Returns:
            Dictionary with 'subject' and 'message' keys
        """
        
        prompt = f"""
Generate a message to inform a parent about a digital safety incident involving their child.

Details:
- Child's name: {child_name}
- Threat type: {threat_type}
- Severity: {severity}
- Action taken: {action_taken}
- Tone: {tone}

Requirements:
- Be clear and direct but not alarming
- Explain what happened in parent-friendly terms
- Mention the action taken
- Provide reassurance where appropriate
- Include a call to action for the parent
- Keep it concise but informative

Provide both a subject line and message body.
"""

        messages = [
            {
                "role": "system",
                "content": "You are a child safety communication specialist. Generate clear, supportive messages for parents about digital safety incidents."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._make_request(messages, temperature=0.4)
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse the response to extract subject and message
            lines = content.split('\n')
            subject = ""
            message = ""
            
            for i, line in enumerate(lines):
                if 'subject' in line.lower() and ':' in line:
                    subject = line.split(':', 1)[1].strip()
                elif subject and not message:
                    # Start collecting message after subject
                    if line.strip() and 'message' not in line.lower():
                        message = '\n'.join(lines[i:]).strip()
                        break
            
            # Fallback if parsing fails
            if not subject or not message:
                subject = f"Safety Alert for {child_name}"
                message = content
            
            return {
                "subject": subject,
                "message": message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate parent message: {str(e)}")
            return {
                "subject": f"Safety Alert for {child_name}",
                "message": f"We detected a {threat_type} incident involving {child_name}. We have taken appropriate action: {action_taken}. Please review this with your child."
            }
    
    def generate_child_message(self, child_name: str, child_age: int, 
                              threat_type: str, tone: str = "supportive") -> Dict[str, str]:
        """
        Generate age-appropriate message for children
        
        Args:
            child_name: Name of the child
            child_age: Age of the child
            threat_type: Type of threat
            tone: Tone of the message
            
        Returns:
            Dictionary with 'subject' and 'message' keys
        """
        
        prompt = f"""
Generate an age-appropriate safety message for a child who experienced an online safety incident.

Details:
- Child's name: {child_name}
- Child's age: {child_age}
- Threat type: {threat_type}
- Tone: {tone}

Requirements:
- Use age-appropriate language for a {child_age}-year-old
- Be supportive and non-blaming
- Provide a simple safety tip
- Reassure the child they did nothing wrong
- Encourage them to talk to trusted adults
- Keep it brief and easy to understand

Provide both a subject line and message body.
"""

        messages = [
            {
                "role": "system",
                "content": f"You are a child safety educator specializing in age-appropriate communication for children aged {child_age}. Create supportive, educational messages."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._make_request(messages, temperature=0.5)
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse the response
            lines = content.split('\n')
            subject = ""
            message = ""
            
            for i, line in enumerate(lines):
                if 'subject' in line.lower() and ':' in line:
                    subject = line.split(':', 1)[1].strip()
                elif subject and not message:
                    if line.strip() and 'message' not in line.lower():
                        message = '\n'.join(lines[i:]).strip()
                        break
            
            if not subject or not message:
                subject = f"Hi {child_name}, let's talk about staying safe online"
                message = content
            
            return {
                "subject": subject,
                "message": message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate child message: {str(e)}")
            return {
                "subject": f"Hi {child_name}, let's talk about staying safe online",
                "message": f"Hi {child_name}, we noticed something online that we want to help you with. Remember, you can always talk to a trusted grown-up if something online makes you feel uncomfortable."
            }
    
    def generate_sender_warning(self, threat_type: str, platform: str) -> Dict[str, str]:
        """
        Generate warning message for senders
        
        Args:
            threat_type: Type of inappropriate behavior
            platform: Platform where incident occurred
            
        Returns:
            Dictionary with 'subject' and 'message' keys
        """
        
        prompt = f"""
Generate a firm but professional warning message for someone who sent inappropriate content to a child.

Details:
- Violation type: {threat_type}
- Platform: {platform}

Requirements:
- Be firm and direct about the violation
- Explain why the behavior is unacceptable
- Mention potential consequences
- Reference community guidelines/laws
- Professional tone, not aggressive
- Clear call to action to stop the behavior

Provide both a subject line and message body.
"""

        messages = [
            {
                "role": "system",
                "content": "You are a digital safety enforcement specialist. Generate firm, professional warnings for policy violations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._make_request(messages, temperature=0.2)
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse the response
            lines = content.split('\n')
            subject = ""
            message = ""
            
            for i, line in enumerate(lines):
                if 'subject' in line.lower() and ':' in line:
                    subject = line.split(':', 1)[1].strip()
                elif subject and not message:
                    if line.strip() and 'message' not in line.lower():
                        message = '\n'.join(lines[i:]).strip()
                        break
            
            if not subject or not message:
                subject = "Warning: Inappropriate Communication Detected"
                message = content
            
            return {
                "subject": subject,
                "message": message
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate sender warning: {str(e)}")
            return {
                "subject": "Warning: Inappropriate Communication Detected",
                "message": f"Your recent communication has been identified as {threat_type}, which violates our community guidelines. Please review our policies and modify your behavior accordingly."
            }
