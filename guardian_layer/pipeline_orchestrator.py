"""Main Pipeline Orchestrator for the Guardian App"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from .models import (
    InputMessage, PipelineResult, AgentResult, RiskLevel, 
    ThreatCategory, PipelineStage, EducationContent
)
from .agents import (
    TextClassifierAgent, ImageClassifierAgent, CrossModalAgent,
    ReasoningAgent, EducationAgent
)
from .config import config
from .utils import logger, calculate_weighted_risk_score, format_threats_for_display

class GuardianPipeline:
    """Main pipeline orchestrator that coordinates all agents"""
    
    def __init__(self):
        self.logger = logger
        
        # Initialize agents
        self.text_classifier = TextClassifierAgent()
        self.image_classifier = ImageClassifierAgent()
        self.cross_modal_agent = CrossModalAgent()
        self.reasoning_agent = ReasoningAgent()
        self.education_agent = EducationAgent()
        
        # Agent weights for risk score calculation
        self.agent_weights = {
            'TextClassifier': 1.0,
            'ImageClassifier': 1.0,
            'CrossModalAgent': 1.5,  # Higher weight for cross-modal analysis
            'ReasoningAgent': 2.0    # Highest weight for deep reasoning
        }
        
        self.current_stage = PipelineStage.INPUT
    
    async def process_message(self, message: InputMessage) -> PipelineResult:
        """
        Process a message through the entire guardian pipeline
        
        Args:
            message: The input message to process
            
        Returns:
            PipelineResult with final decision and educational content
        """
        start_time = time.time()
        agent_results = []
        
        try:
            self.logger.info(f"Starting pipeline processing for message {message.message_id}")
            self.current_stage = PipelineStage.INPUT
            
            # Step 1: Pre-Filter Agents (Cheap + Fast)
            self.current_stage = PipelineStage.TEXT_CLASSIFIER
            text_result = await self._run_text_classifier(message)
            if text_result:
                agent_results.append(text_result)
                if not self._should_continue(text_result):
                    return await self._finalize_result(message, agent_results, start_time, "blocked_by_text_filter")
            
            self.current_stage = PipelineStage.IMAGE_CLASSIFIER
            image_result = await self._run_image_classifier(message)
            if image_result:
                agent_results.append(image_result)
                if not self._should_continue(image_result):
                    return await self._finalize_result(message, agent_results, start_time, "blocked_by_image_filter")
            
            # Step 2: Cross-Modal Agent
            self.current_stage = PipelineStage.CROSS_MODAL
            cross_modal_result = await self._run_cross_modal_agent(message)
            if cross_modal_result:
                agent_results.append(cross_modal_result)
                if not self._should_continue(cross_modal_result):
                    return await self._finalize_result(message, agent_results, start_time, "blocked_by_cross_modal")
            
            # Step 3: Heavyweight Reasoning Agent
            self.current_stage = PipelineStage.REASONING
            reasoning_result = await self._run_reasoning_agent(message)
            if reasoning_result:
                agent_results.append(reasoning_result)
            
            # Step 4: Decision & Routing
            self.current_stage = PipelineStage.DECISION
            final_result = await self._finalize_result(message, agent_results, start_time, "completed")
            
            self.current_stage = PipelineStage.COMPLETE
            return final_result
            
        except Exception as e:
            self.logger.error(f"Pipeline processing failed for message {message.message_id}: {str(e)}")
            return await self._create_error_result(message, agent_results, start_time, str(e))
    
    async def _run_text_classifier(self, message: InputMessage) -> Optional[AgentResult]:
        """Run text classifier agent"""
        if self.text_classifier.can_process(message):
            self.logger.debug(f"Running text classifier for message {message.message_id}")
            return await self.text_classifier.process(message)
        return None
    
    async def _run_image_classifier(self, message: InputMessage) -> Optional[AgentResult]:
        """Run image classifier agent"""
        if self.image_classifier.can_process(message):
            self.logger.debug(f"Running image classifier for message {message.message_id}")
            return await self.image_classifier.process(message)
        return None
    
    async def _run_cross_modal_agent(self, message: InputMessage) -> Optional[AgentResult]:
        """Run cross-modal agent"""
        if self.cross_modal_agent.can_process(message):
            self.logger.debug(f"Running cross-modal agent for message {message.message_id}")
            return await self.cross_modal_agent.process(message)
        return None
    
    async def _run_reasoning_agent(self, message: InputMessage) -> Optional[AgentResult]:
        """Run reasoning agent"""
        if self.reasoning_agent.can_process(message):
            self.logger.debug(f"Running reasoning agent for message {message.message_id}")
            return await self.reasoning_agent.process(message)
        return None
    
    def _should_continue(self, result: AgentResult) -> bool:
        """
        Determine if pipeline should continue based on agent result
        
        Args:
            result: Agent result to evaluate
            
        Returns:
            True if pipeline should continue, False if should stop and block
        """
        # Stop immediately for high-risk threats
        high_risk_threats = {
            ThreatCategory.CSAM, 
            ThreatCategory.GROOMING, 
            ThreatCategory.PREDATORY
        }
        
        if any(threat in high_risk_threats for threat in result.threats_detected):
            self.logger.warning(f"High-risk threat detected by {result.agent_name}: {result.threats_detected}")
            return False
        
        # Stop if risk score is very high
        if result.risk_score >= config.model.high_risk_threshold:
            self.logger.warning(f"High risk score detected by {result.agent_name}: {result.risk_score}")
            return False
        
        # Continue processing
        return True
    
    async def _finalize_result(
        self, 
        message: InputMessage, 
        agent_results: List[AgentResult], 
        start_time: float,
        completion_reason: str
    ) -> PipelineResult:
        """
        Finalize the pipeline result with decision and educational content
        
        Args:
            message: Original input message
            agent_results: Results from all agents
            start_time: Pipeline start time
            completion_reason: Reason for completion
            
        Returns:
            Final pipeline result
        """
        # Calculate overall risk score
        risk_scores = {result.agent_name: result.risk_score for result in agent_results}
        overall_risk_score = calculate_weighted_risk_score(risk_scores, self.agent_weights)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk_score)
        
        # Collect all threats
        all_threats = []
        for result in agent_results:
            all_threats.extend(result.threats_detected)
        unique_threats = list(set(all_threats))
        
        # Create explanation
        explanation = self._create_explanation(agent_results, overall_risk_score, completion_reason)
        
        # Determine if content should be blocked
        blocked = self._should_block_content(risk_level, unique_threats)
        
        # Generate educational content
        self.current_stage = PipelineStage.EDUCATION
        education_content = await self.education_agent.generate_education_content(
            message, risk_level, unique_threats, explanation
        )
        
        # Create final result
        processing_time = time.time() - start_time
        
        result = PipelineResult(
            message_id=message.message_id,
            risk_level=risk_level,
            overall_risk_score=overall_risk_score,
            threats_detected=unique_threats,
            agent_results=agent_results,
            decision=self._create_decision_text(risk_level, blocked, unique_threats),
            child_message=education_content.child_message,
            parent_message=education_content.parent_message,
            blocked=blocked,
            processing_time=processing_time
        )
        
        self.logger.info(
            f"Pipeline completed for message {message.message_id}: "
            f"risk_level={risk_level.value}, blocked={blocked}, "
            f"threats={[t.value for t in unique_threats]}, "
            f"processing_time={processing_time:.2f}s"
        )
        
        return result
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on overall risk score"""
        if risk_score >= config.model.high_risk_threshold:
            return RiskLevel.HIGH
        elif risk_score >= config.model.medium_risk_threshold:
            return RiskLevel.MEDIUM
        elif risk_score >= config.model.low_risk_threshold:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE
    
    def _should_block_content(self, risk_level: RiskLevel, threats: List[ThreatCategory]) -> bool:
        """Determine if content should be blocked"""
        # Always block high-risk content
        if risk_level == RiskLevel.HIGH:
            return True
        
        # Block specific high-severity threats regardless of overall risk
        high_severity_threats = {
            ThreatCategory.CSAM,
            ThreatCategory.GROOMING, 
            ThreatCategory.PREDATORY
        }
        
        return any(threat in high_severity_threats for threat in threats)
    
    def _create_explanation(
        self, 
        agent_results: List[AgentResult], 
        overall_risk_score: float,
        completion_reason: str
    ) -> str:
        """Create human-readable explanation of the analysis"""
        if not agent_results:
            return "No analysis performed due to processing error."
        
        explanations = []
        
        for result in agent_results:
            if result.threats_detected:
                threat_text = format_threats_for_display(result.threats_detected)
                explanations.append(f"{result.agent_name} detected: {threat_text}")
            elif result.risk_score > 0.3:
                explanations.append(f"{result.agent_name} flagged potential concerns")
        
        if not explanations:
            explanations.append("Content appears safe based on automated analysis")
        
        base_explanation = ". ".join(explanations)
        base_explanation += f". Overall risk score: {overall_risk_score:.2f}"
        
        if completion_reason.startswith("blocked_by"):
            base_explanation += f". Processing stopped early due to safety concerns."
        
        return base_explanation
    
    def _create_decision_text(
        self, 
        risk_level: RiskLevel, 
        blocked: bool, 
        threats: List[ThreatCategory]
    ) -> str:
        """Create decision text explaining the action taken"""
        if blocked:
            if threats:
                threat_text = format_threats_for_display(threats)
                return f"Content blocked due to {threat_text}. Child safety prioritized."
            else:
                return f"Content blocked due to {risk_level.value} risk level."
        else:
            if risk_level == RiskLevel.SAFE:
                return "Content allowed - appears safe for children."
            elif risk_level == RiskLevel.LOW:
                return "Content allowed with educational guidance provided."
            elif risk_level == RiskLevel.MEDIUM:
                return "Content allowed with warning and parent notification."
            else:
                return "Content requires review."
    
    async def _create_error_result(
        self, 
        message: InputMessage, 
        agent_results: List[AgentResult], 
        start_time: float,
        error_message: str
    ) -> PipelineResult:
        """Create error result when pipeline fails"""
        processing_time = time.time() - start_time
        
        # Use conservative estimates for safety
        return PipelineResult(
            message_id=message.message_id,
            risk_level=RiskLevel.MEDIUM,
            overall_risk_score=0.5,
            threats_detected=[],
            agent_results=agent_results,
            decision=f"Processing error occurred: {error_message}. Content blocked for safety.",
            child_message="We're having trouble checking this content right now. Please ask a grown-up for help.",
            parent_message=f"Content analysis failed due to technical error: {error_message}. Content has been blocked as a safety precaution.",
            blocked=True,
            processing_time=processing_time
        )
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'current_stage': self.current_stage.value,
            'agents_loaded': {
                'text_classifier': self.text_classifier is not None,
                'image_classifier': self.image_classifier is not None,
                'cross_modal_agent': self.cross_modal_agent is not None,
                'reasoning_agent': self.reasoning_agent is not None,
                'education_agent': self.education_agent is not None
            },
            'configuration': {
                'low_risk_threshold': config.model.low_risk_threshold,
                'medium_risk_threshold': config.model.medium_risk_threshold,
                'high_risk_threshold': config.model.high_risk_threshold
            }
        }
