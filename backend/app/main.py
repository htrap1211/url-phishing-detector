"""
FastAPI application for URL Phishing Detection.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import url_check

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ML-based URL phishing detection system with threat intelligence enrichment"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    url_check.router,
    prefix="/api/v1/url",
    tags=["URL Check"]
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Model version: {settings.MODEL_VERSION}")
    
    # Pre-load ML model
    try:
        from app.ml.model import get_detector
        detector = get_detector()
        logger.info("✅ ML model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
        logger.warning("API will start but predictions will fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        from app.ml.model import get_detector
        detector = get_detector()
        model_loaded = detector.model is not None
    except:
        model_loaded = False
    
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "model_version": settings.MODEL_VERSION
    }
