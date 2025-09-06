"""Base agent class for all Guardian App agents"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..models import InputMessage, AgentResult, ThreatCategory
from ..utils import timing_decorator, logger

class BaseAgent(ABC):
    """Abstract base class for all agents in the pipeline"""
    
    def __init__(self, name: str, confidence_threshold: float = 0.7):
        self.name = name
        self.confidence_threshold = confidence_threshold
        self.logger = logger
        
    @abstractmethod
    async def analyze(self, message: InputMessage) -> AgentResult:
        """
        Analyze the input message and return results
        
        Args:
            message: The input message to analyze
            
        Returns:
            AgentResult with analysis results
        """
        pass
    
    @abstractmethod
    def can_process(self, message: InputMessage) -> bool:
        """
        Check if this agent can process the given message type
        
        Args:
            message: The input message
            
        Returns:
            True if agent can process this message type
        """
        pass
    
    def should_escalate(self, result: AgentResult) -> bool:
        """
        Determine if the result should be escalated to the next agent
        
        Args:
            result: The analysis result
            
        Returns:
            True if should escalate to next agent
        """
        return (result.risk_score > self.confidence_threshold or 
                result.confidence < self.confidence_threshold or
                len(result.threats_detected) > 0)
    
    def _create_result(
        self, 
        confidence: float, 
        risk_score: float, 
        threats: List[ThreatCategory], 
        explanation: str,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Helper method to create AgentResult
        
        Args:
            confidence: Confidence in the analysis
            risk_score: Risk score (0.0 to 1.0)
            threats: List of detected threats
            explanation: Human-readable explanation
            processing_time: Time taken for processing
            metadata: Additional metadata
            
        Returns:
            AgentResult object
        """
        return AgentResult(
            agent_name=self.name,
            confidence=confidence,
            risk_score=risk_score,
            threats_detected=threats,
            explanation=explanation,
            processing_time=processing_time,
            metadata=metadata or {}
        )
    
    def _log_analysis(self, message: InputMessage, result: AgentResult):
        """Log the analysis result"""
        self.logger.info(
            f"{self.name} analyzed message {message.message_id}: "
            f"risk={result.risk_score:.2f}, confidence={result.confidence:.2f}, "
            f"threats={[t.value for t in result.threats_detected]}"
        )
    
    async def process(self, message: InputMessage) -> Optional[AgentResult]:
        """
        Main processing method that includes logging and error handling
        
        Args:
            message: The input message to process
            
        Returns:
            AgentResult if processing successful, None if agent can't process
        """
        if not self.can_process(message):
            self.logger.debug(f"{self.name} cannot process message {message.message_id}")
            return None
        
        start_time = time.time()
        try:
            self.logger.debug(f"{self.name} starting analysis of message {message.message_id}")
            
            result = await self.analyze(message)
            
            end_time = time.time()
            result.processing_time = end_time - start_time
            
            self._log_analysis(message, result)
            return result
            
        except Exception as e:
            self.logger.error(f"{self.name} failed to analyze message {message.message_id}: {str(e)}")
            # Return a safe result indicating processing failure
            return self._create_result(
                confidence=0.0,
                risk_score=0.5,  # Medium risk due to processing failure
                threats=[],
                explanation=f"Analysis failed: {str(e)}",
                processing_time=time.time() - start_time
            )

class AIAgent(BaseAgent):
    """Base class for AI-powered agents"""
    
    def __init__(self, name: str, api_key: str, confidence_threshold: float = 0.7):
        super().__init__(name, confidence_threshold)
        self.api_key = api_key
        
    def _prepare_api_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    async def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API request (to be implemented by specific agents)
        
        Args:
            payload: Request payload
            
        Returns:
            API response
        """
        raise NotImplementedError("Subclasses must implement _make_api_request")
