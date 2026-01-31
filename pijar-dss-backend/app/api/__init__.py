"""
API Module.

Provides REST API endpoints for the Pijar DSS backend.
"""

from .routes import router

__all__ = ['router']