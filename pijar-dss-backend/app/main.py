"""
Pijar DSS Backend - Main Application Entry Point.

FastAPI application for the Decision Support System backend.
Production-ready with configurable CORS.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"Max simulations: {settings.max_n_simulations}")
    print(f"Parallel jobs: {settings.n_jobs}")
    
    # Log CORS configuration
    origins = get_allowed_origins()
    print(f"CORS allowed origins: {origins}")
    
    yield
    
    # Shutdown
    print("Shutting down...")


def get_allowed_origins() -> list:
    """
    Get allowed CORS origins based on environment.
    
    Priority:
    1. ALLOWED_ORIGINS environment variable (comma-separated)
    2. Default production origins
    
    Always includes localhost for development/testing.
    """
    # Check for ALLOWED_ORIGINS env var
    allowed_env = os.getenv("ALLOWED_ORIGINS", "")
    
    if allowed_env:
        # Parse comma-separated origins
        origins = [origin.strip() for origin in allowed_env.split(",") if origin.strip()]
    else:
        # Default production origins - add your actual domains here
        origins = []
    
    # Always include the known Vercel domain
    default_origins = [
        "https://pijardss.vercel.app/",
        "https://pijardss.vercel.app",
        "https://pijar-dss.vercel.app",
        "https://pijar-dss-frontend.vercel.app",
    ]
    
    # Add localhost for development/testing
    localhost_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Combine all origins (avoiding duplicates)
    all_origins = list(set(origins + default_origins + localhost_origins))
    
    return all_origins


def create_app() -> FastAPI:
    """
    Application factory.
    
    Creates and configures the FastAPI application.
    """
    settings = get_settings()
    
    # Determine if we should show docs
    show_docs = settings.debug or os.getenv("SHOW_DOCS", "false").lower() == "true"
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Quantitative Decision Support System for Pijar PT Expansion",
        lifespan=lifespan,
        docs_url="/docs" if show_docs else None,
        redoc_url="/redoc" if show_docs else None,
    )
    
    # Get allowed origins
    allowed_origins = get_allowed_origins()
    
    # CORS middleware - MUST be added before routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1", tags=["simulation"])
    
    # Root endpoint for basic health check
    @app.get("/")
    async def root():
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running"
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )