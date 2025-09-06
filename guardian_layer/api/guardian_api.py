"""FastAPI application for Guardian Layer REST API"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Union

from ..schemas.guardian_schemas import GuardianRequest, GuardianResponse
from ..schemas.api_schemas import APIResponse, ErrorResponse, HealthResponse
from ..guardian_layer import guardian_layer
from ..utils import logger

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
    
    This endpoint implements the 3-step Guardian Layer pipeline:
    1. Input Layer: Accepts text and/or image content
    2. Guardrail Models: Runs text and image classifiers
    3. Structured Output: Returns standardized risk categories with scores
    """
    try:
        # Validate input
        if not request.text and not request.image:
            raise HTTPException(
                status_code=400, 
                detail="Either text or image content must be provided"
            )
        
        # Process through guardian layer
        result = await guardian_layer.process_request(request)
        
        # Return structured response
        return APIResponse(
            success=True,
            data=result,
            message="Content analysis completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content analysis failed: {str(e)}"
        )

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
