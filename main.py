from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime

from app.config.settings import settings
from app.routers import email
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(email.router, prefix="/email", tags=["Email"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/email/health"
    }


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.api_title,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

