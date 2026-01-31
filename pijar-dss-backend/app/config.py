"""
Configuration management for Pijar DSS Backend.

Loads settings from environment variables with sensible defaults.
Uses Pydantic Settings for type validation and environment parsing.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic Settings automatically reads from .env file and
    environment variables, with type coercion and validation.
    """
    
    # Application metadata
    app_name: str = "Pijar DSS Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Simulation defaults
    default_n_simulations: int = 500
    default_time_horizon: int = 36
    max_n_simulations: int = 10000
    
    # Parallel processing
    # -1 means use all available CPU cores
    n_jobs: int = -1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader.
    
    Uses lru_cache to ensure settings are only loaded once,
    avoiding repeated file I/O on every request.
    """
    return Settings()