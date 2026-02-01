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
    
    yield
    
    # Shutdown
    print("Shutting down...")


def get_allowed_origins() -> list:
    """
    Get allowed CORS origins based on environment.
    
    In development: Allow all origins
    In production: Use ALLOWED_ORIGINS env var or defaults
    """
    settings = get_settings()
    
    if settings.debug:
        # Development: allow all
        return ["*"]
    
    # Production: parse from environment or use defaults
    allowed = os.getenv("ALLOWED_ORIGINS", "")
    
    if allowed:
        # Split comma-separated origins
        origins = [origin.strip() for origin in allowed.split(",")]
    else:
        # Default production origins (update these!)
        origins = [
            "https://pijar-dss.vercel.app",
            "https://pijar-dss-*.vercel.app",  # Preview deployments
        ]
    
    # Always allow localhost for testing
    origins.extend([
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ])
    
    return origins


def create_app() -> FastAPI:
    """
    Application factory.
    
    Creates and configures the FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Quantitative Decision Support System for Pijar PT Expansion",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,  # Disable docs in production
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # CORS middleware - production-ready configuration
    allowed_origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
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