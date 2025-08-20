"""
Configuration settings for the FastAPI application
"""

import os
import sys
from pydantic_settings import BaseSettings
from typing import Optional

# Add parent directory to path to import config_loader
sys.path.append('/app')
from config_loader import get_config

class Settings(BaseSettings):
    """Application settings"""

    # Database settings
    database_url: str = "postgresql://pipeline_user:pipeline_password@postgres:5432/pipeline_db"

    # API settings
    api_title: str = "Pipeline Data API"
    api_version: str = "1.0.0"
    api_description: str = "API for querying processed data from OneDrive ETL pipeline"

    # Security settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Microsoft Graph API settings
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # Pagination settings
    default_page_size: int = 100
    max_page_size: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with config.yaml values if available
        try:
            config = get_config()
            
            # Database configuration
            if config.get_database_url():
                self.database_url = config.get_database_url()
            
            # API configuration
            api_config = config.get_api_config()
            if api_config.get('secret_key'):
                self.secret_key = api_config['secret_key']
            
            # Microsoft Graph API configuration
            ms_config = config.get_microsoft_graph_config()
            if ms_config.get('client_id'):
                self.microsoft_client_id = ms_config['client_id']
            if ms_config.get('client_secret'):
                self.microsoft_client_secret = ms_config['client_secret']
            if ms_config.get('tenant_id'):
                self.microsoft_tenant_id = ms_config['tenant_id']
            
            # Logging configuration
            logging_config = config.get_logging_config()
            if logging_config.get('level'):
                self.log_level = logging_config['level']
            if logging_config.get('format'):
                self.log_format = logging_config['format']
                
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")

# Create settings instance
settings = Settings()
