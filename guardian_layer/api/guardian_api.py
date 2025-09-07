"""FastAPI application for Guardian Layer REST API"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Union

from ..schemas.guardian_schemas import GuardianRequest, GuardianResponse
from ..schemas.api_schemas import APIResponse, ErrorResponse, HealthResponse, EnhancedAPIResponse
from ..schemas.simple_schemas import ContentRequest, SimpleRequest
from ..guardian_layer import guardian_layer
from ..utils import logger
import base64
import re

# Create FastAPI app
app = FastAPI(
    title="Guardian Layer API",
    description="Content moderation API with structured outputs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An internal server error occurred",
            details={"exception": str(exc)}
        ).dict()
    )

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/status")
async def get_status():
    """Get guardian layer status"""
    try:
        status = guardian_layer.get_status()
        return APIResponse(
            success=True,
            data=status,
            message="Guardian layer status retrieved"
        )
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get status")

@app.post("/guardian/check", response_model=APIResponse)
async def check_content(request: GuardianRequest):
    """
    Main endpoint: Analyze content for safety risks
    
    This endpoint determines content type and calls appropriate analysis function:
    - If text is provided: calls text analysis function
    - If image is provided: calls image analysis function
    - Returns APIResponse with analysis results
    """
    try:
        print("----------------------------------------------------------------")
        print("Received request:", request)
        # Validate input
        if not request.text and not request.image:
            print("Neither text nor image provided", request)   
            raise HTTPException(
                status_code=400, 
                detail="Either text or image content must be provided"
            )
        
        # Determine content type and call appropriate analysis function
        if request.text and not request.image:
            # Text only analysis
            result = await analyze_text_content(request)
            message = "Text analysis completed"
        elif request.image and not request.text:
            # Image only analysis
            result = await analyze_image_content(request)
            message = "Image analysis completed"
        
        # Return structured response
        return APIResponse(
            success=True,
            data=result,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content analysis failed: {str(e)}"
        )

async def analyze_text_content(request: GuardianRequest):
    """
    Analyze text content for safety risks
    
    Args:
        request: GuardianRequest containing text content
        
    Returns:
        GuardianResponse with text analysis results
    """
    from ..schemas.guardian_schemas import (
        GuardianResponse, RiskResult, generate_input_id, determine_status
    )
    import time
    
    start_time = time.time()
    input_id = generate_input_id()
    
    try:
        logger.info(f"Analyzing text content for request {input_id}")
        
        # Create input message for text analysis
        message = guardian_layer._create_input_message(request, input_id)
        
        # Analyze text only
        text_risks = await guardian_layer._analyze_text(message)
        
        # Create results with text risks only
        results = RiskResult(
            text_risk=text_risks,
            image_risk=[]  # Empty for text-only analysis
        )
        
        status = determine_status(text_risks, [])
        processing_time = time.time() - start_time
        
        response = GuardianResponse(
            input_id=input_id,
            results=results,
            status=status,
            processing_time=processing_time
        )
        
        logger.info(f"Text analysis completed for {input_id}: status={status.value}")
        return response
        
    except Exception as e:
        logger.error(f"Text analysis failed for {input_id}: {str(e)}")
        raise

async def analyze_image_content(request: GuardianRequest):
    """
    Analyze image content for safety risks
    
    Args:
        request: GuardianRequest containing image content
        
    Returns:
        GuardianResponse with image analysis results
    """
    from ..schemas.guardian_schemas import (
        GuardianResponse, RiskResult, generate_input_id, determine_status
    )
    import time
    
    start_time = time.time()
    input_id = generate_input_id()
    
    try:
        logger.info(f"Analyzing image content for request {input_id}")
        
        # Create input message for image analysis
        message = guardian_layer._create_input_message(request, input_id)
        
        # Analyze image only
        image_risks = await guardian_layer._analyze_image(message)
        
        # Create results with image risks only
        results = RiskResult(
            text_risk=[],  # Empty for image-only analysis
            image_risk=image_risks
        )
        
        status = determine_status([], image_risks)
        processing_time = time.time() - start_time
        
        response = GuardianResponse(
            input_id=input_id,
            results=results,
            status=status,
            processing_time=processing_time
        )
        
        logger.info(f"Image analysis completed for {input_id}: status={status.value}")
        return response
        
    except Exception as e:
        logger.error(f"Image analysis failed for {input_id}: {str(e)}")
        raise

def combine_analysis_results(text_result, image_result, request):
    """
    Combine text and image analysis results into a single response
    
    Args:
        text_result: GuardianResponse from text analysis
        image_result: GuardianResponse from image analysis
        request: Original GuardianRequest
        
    Returns:
        Combined GuardianResponse
    """
    from ..schemas.guardian_schemas import (
        GuardianResponse, RiskResult, generate_input_id, determine_status
    )
    
    # Combine risks from both analyses
    combined_text_risks = text_result.results.text_risk
    combined_image_risks = image_result.results.image_risk
    
    # Create combined results
    results = RiskResult(
        text_risk=combined_text_risks,
        image_risk=combined_image_risks
    )
    
    # Determine overall status
    status = determine_status(combined_text_risks, combined_image_risks)
    
    # Use the longer processing time
    processing_time = max(text_result.processing_time, image_result.processing_time)
    
    # Create combined response
    response = GuardianResponse(
        input_id=generate_input_id(),
        results=results,
        status=status,
        processing_time=processing_time
    )
    
    return response

@app.post("/guardian/check/text", response_model=APIResponse)
async def check_text_only(text: str, user_id: Union[str, None] = None):
    """Convenience endpoint for text-only analysis"""
    request = GuardianRequest(text=text, user_id=user_id)
    return await check_content(request)

@app.post("/guardian/check/image", response_model=APIResponse)
async def check_image_only(image: str, user_id: Union[str, None] = None):
    """Convenience endpoint for image-only analysis"""
    request = GuardianRequest(image=image, user_id=user_id)
    return await check_content(request)

# ===== NOUVEAUX ENDPOINTS AVEC SCHÉMAS SIMPLIFIÉS =====

@app.post("/guardian/analyze", response_model=APIResponse)
async def analyze_content_simple(request: ContentRequest):
    """
    Endpoint simplifié avec type de contenu explicite
    
    Utilise ContentRequest au lieu de GuardianRequest:
    - content: le contenu à analyser (texte ou image base64)
    - content_type: "text" ou "image"
    - user_id: optionnel
    """
    try:
        logger.info(f"Analyzing {request.content_type} content")
        
        if request.content_type.lower() == "text":
            # Analyse de texte
            result = await analyze_text_simple(request.content, request.user_id)
            message = "Text analysis completed"
        elif request.content_type.lower() == "image":
            # Analyse d'image
            result = await analyze_image_simple(request.content, request.user_id)
            message = "Image analysis completed"
        else:
            raise HTTPException(
                status_code=400,
                detail="content_type must be 'text' or 'image'"
            )
        
        return APIResponse(
            success=True,
            data=result,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content analysis failed: {str(e)}"
        )

@app.post("/guardian/auto-analyze", response_model=EnhancedAPIResponse)
async def auto_analyze_content(request: SimpleRequest):
    """
    Endpoint ultra-simplifié avec détection automatique du type
    
    Utilise SimpleRequest:
    - content: le contenu à analyser (détection automatique du type)
    - user_id: optionnel
    
    Détecte automatiquement si c'est du texte ou une image base64
    Si des risques sont détectés, passe les résultats à l'agent layer pour prise de décision
    """
    try:
        print("----------------------------------------------------------------")
        print(request)
        logger.info("Auto-analyzing content")
        
        # Détection automatique du type de contenu
        content_type = detect_content_type(request.content)
        
        if content_type == "text":
            result = await analyze_text_simple(request.content, request.user_id)
            print("result", result)
            message = "Text analysis completed (auto-detected)"
        elif content_type == "image":
            result = await analyze_image_simple(request.content, request.user_id)
            message = "Image analysis completed (auto-detected)"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unable to determine content type. Please use explicit endpoint."
            )
        
        # Check if there are any risks detected
        text_risks = result.results.text_risk if result.results.text_risk else []
        image_risks = result.results.image_risk if result.results.image_risk else []
        
        # If no risks detected, return early and wait for another message
        if not text_risks and not image_risks:
            logger.info(f"No risks detected for message {result.input_id}. Returning safe status.")
            return EnhancedAPIResponse(
                success=True,
                data={
                    "guardian_analysis": result.dict(),
                    "agent_processing": {
                        "triggered": False,
                        "message_id": None,
                        "actions_planned": 0,
                        "action_types": [],
                        "followup_required": False,
                        "followup_date": None
                    }
                },
                message=f"{message} - No risks detected"
            )
        
        # If risks are detected, pass to agent layer for decision-making
        logger.info(f"Risks detected for message {result.input_id}. Triggering agent layer processing.")
        
        try:
            # Import agent layer components
            import sys
            from pathlib import Path
            agent_path = Path(__file__).parent.parent.parent / "agent_layer"
            if str(agent_path) not in sys.path:
                sys.path.append(str(agent_path))
            
            from agent_layer.integrations.guardian_integration import GuardianIntegration
            from agent_layer.agents.ai_agent import AIAgent
            
            # Convert Guardian response to SuspiciousMessage format
            integration = GuardianIntegration()
            suspicious_message = integration.convert_guardian_response(
                guardian_response=result,
                original_content=request.content,
                additional_metadata={
                    "user_id": request.user_id,
                    "content_type": content_type,
                    "platform": "guardian_api",
                    "sender_type": "unknown"
                }
            )
            
            # Process with AI Agent
            ai_agent = AIAgent(use_llm=True)
            action_plan = ai_agent.process_suspicious_message(suspicious_message)
            
            logger.info(f"Agent processing completed for message {result.input_id}. Generated {len(action_plan.decisions)} actions.")
            
            # Return response indicating agent processing was triggered
            return EnhancedAPIResponse(
                success=True,
                data={
                    "guardian_analysis": result.dict(),
                    "agent_processing": {
                        "triggered": True,
                        "message_id": suspicious_message.message_id,
                        "actions_planned": len(action_plan.decisions),
                        "action_types": [d.action_type.value for d in action_plan.decisions],
                        "followup_required": action_plan.followup_required,
                        "followup_date": action_plan.followup_date.isoformat() if action_plan.followup_date else None,
                        "action_plan": action_plan.to_dict()
                    }
                },
                message=f"{message} - Risks detected, agent actions initiated"
            )
            
        except Exception as agent_error:
            logger.error(f"Agent layer processing failed: {str(agent_error)}")
            # Return Guardian results even if agent processing fails
            return EnhancedAPIResponse(
                success=True,
                data={
                    "guardian_analysis": result.dict(),
                    "agent_processing": {
                        "triggered": False,
                        "error": str(agent_error)
                    }
                },
                message=f"{message} - Risks detected, but agent processing failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Auto-analysis failed: {str(e)}"
        )

# ===== FONCTIONS D'ANALYSE SIMPLIFIÉES =====

async def analyze_text_simple(text_content: str, user_id: str = None):
    """
    Analyse de texte simplifiée
    
    Args:
        text_content: Le texte à analyser
        user_id: ID utilisateur optionnel
        
    Returns:
        GuardianResponse avec résultats d'analyse
    """
    from ..schemas.guardian_schemas import (
        GuardianResponse, RiskResult, generate_input_id, determine_status
    )
    from ..models import InputMessage
    
    start_time = time.time()
    input_id = generate_input_id()
    
    try:
        logger.info(f"Simple text analysis for request {input_id}")
        
        # Créer un message d'entrée
        message = InputMessage(
            message_id=input_id,
            text=text_content,
            user_id=user_id
        )
        
        # Analyser le texte
        text_risks = await guardian_layer._analyze_text(message)
        
        # Créer la réponse
        results = RiskResult(
            text_risk=text_risks,
            image_risk=[]
        )
        
        status = determine_status(text_risks, [])
        processing_time = time.time() - start_time
        
        response = GuardianResponse(
            input_id=input_id,
            results=results,
            status=status,
            processing_time=processing_time
        )
        
        logger.info(f"Simple text analysis completed: {status.value}")
        return response
        
    except Exception as e:
        logger.error(f"Simple text analysis failed: {str(e)}")
        raise

async def analyze_image_simple(image_content: str, user_id: str = None):
    """
    Analyse d'image simplifiée
    
    Args:
        image_content: Image en base64
        user_id: ID utilisateur optionnel
        
    Returns:
        GuardianResponse avec résultats d'analyse
    """
    from ..schemas.guardian_schemas import (
        GuardianResponse, RiskResult, generate_input_id, determine_status
    )
    from ..models import InputMessage
    
    start_time = time.time()
    input_id = generate_input_id()
    
    try:
        logger.info(f"Simple image analysis for request {input_id}")
        
        # Décoder l'image base64
        try:
            image_data = base64.b64decode(image_content)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image: {str(e)}"
            )
        
        # Créer un message d'entrée
        message = InputMessage(
            message_id=input_id,
            image_data=image_data,
            user_id=user_id
        )
        
        # Analyser l'image
        image_risks = await guardian_layer._analyze_image(message)
        
        # Créer la réponse
        results = RiskResult(
            text_risk=[],
            image_risk=image_risks
        )
        
        status = determine_status([], image_risks)
        processing_time = time.time() - start_time
        
        response = GuardianResponse(
            input_id=input_id,
            results=results,
            status=status,
            processing_time=processing_time
        )
        
        logger.info(f"Simple image analysis completed: {status.value}")
        return response
        
    except Exception as e:
        logger.error(f"Simple image analysis failed: {str(e)}")
        raise

def detect_content_type(content: str) -> str:
    """
    Détecte automatiquement le type de contenu
    
    Args:
        content: Le contenu à analyser
        
    Returns:
        "text" ou "image" ou "unknown"
    """
    # Vérifier si c'est une image base64
    base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
    
    # Si le contenu est très long et correspond au pattern base64, c'est probablement une image
    if len(content) > 100 and re.match(base64_pattern, content):
        try:
            # Essayer de décoder pour vérifier
            decoded = base64.b64decode(content)
            # Vérifier les signatures d'images communes
            if (decoded.startswith(b'\xff\xd8\xff') or  # JPEG
                decoded.startswith(b'\x89PNG') or       # PNG
                decoded.startswith(b'GIF8') or          # GIF
                decoded.startswith(b'RIFF')):           # WebP
                return "image"
        except:
            pass
    
    # Sinon, considérer comme du texte
    return "text"

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize guardian layer on startup"""
    logger.info("Guardian Layer API starting up...")
    try:
        status = guardian_layer.get_status()
        logger.info(f"Guardian Layer initialized: {status}")
    except Exception as e:
        logger.error(f"Failed to initialize Guardian Layer: {str(e)}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Guardian Layer API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "guardian_app.api.guardian_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
