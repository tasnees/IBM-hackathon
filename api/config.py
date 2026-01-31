"""Configuration settings for the Support API."""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ServiceNow Configuration
    servicenow_instance: str = os.getenv("SERVICENOW_INSTANCE", "your-instance.service-now.com")
    servicenow_username: str = os.getenv("SERVICENOW_USERNAME", "")
    servicenow_password: str = os.getenv("SERVICENOW_PASSWORD", "")
    
    # Slack Configuration
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_default_channel: str = os.getenv("SLACK_DEFAULT_CHANNEL", "#incidents")
    
    # GitHub Configuration
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_default_repo: str = os.getenv("GITHUB_DEFAULT_REPO", "")
    
    # API Configuration
    api_title: str = "TechNova Support API"
    api_version: str = "1.0.0"
    api_description: str = "API for creating ServiceNow incidents and sending Slack notifications"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
