from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import datetime
import os

from app.config.settings import settings
from app.routers import email
from app.routers import dashboard
from app.core.logging import get_logger
from app.core.auth import verify_docs_access
from app.core.database import connect_db, disconnect_db

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB on startup
@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    await connect_db()
    logger.info("Database connected")
    
    # Load templates from files on first run
    try:
        from app.migrations.load_templates import load_templates_from_files
        await load_templates_from_files()
    except Exception as e:
        logger.warning(f"Could not load templates from files: {e}")
    
    logger.info("Application startup complete")


# Disconnect from MongoDB on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    await disconnect_db()
    logger.info("Application shutdown complete")


# Include routers
app.include_router(email.router, prefix="/email", tags=["Email"])
app.include_router(dashboard.router, tags=["Dashboard"])


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


@app.get("/docs", include_in_schema=False)
async def get_docs(credentials: HTTPBasicCredentials = Depends(verify_docs_access)):
    """Protected Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Docs",
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc(credentials: HTTPBasicCredentials = Depends(verify_docs_access)):
    """Protected ReDoc documentation."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi(credentials: HTTPBasicCredentials = Depends(verify_docs_access)):
    """Protected OpenAPI schema."""
    return app.openapi()


@app.get("/dashboard", include_in_schema=False)
async def get_dashboard(credentials: HTTPBasicCredentials = Depends(verify_docs_access)):
    """Protected dashboard UI."""
    dashboard_path = os.path.join(
        os.path.dirname(__file__), 
        "app/templates/dashboard.html"
    )
    return FileResponse(dashboard_path, media_type="text/html")
