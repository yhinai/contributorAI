"""Configuration settings for AI Contributor Summaries application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="AI Contributor Summaries", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Weaviate
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    # FriendliAI
    friendliai_api_key: str = Field(env="FRIENDLIAI_API_KEY")
    friendliai_base_url: str = Field(default="https://api.friendli.ai", env="FRIENDLIAI_BASE_URL")
    
    # GitHub
    github_token: str = Field(env="GITHUB_TOKEN")
    github_api_url: str = Field(default="https://api.github.com", env="GITHUB_API_URL")
    
    # Hypermode
    hypermode_api_key: str = Field(env="HYPERMODE_API_KEY")
    hypermode_base_url: str = Field(default="https://api.hypermode.com", env="HYPERMODE_BASE_URL")
    
    # ACI.dev
    aci_dev_api_key: str = Field(env="ACI_DEV_API_KEY")
    aci_dev_base_url: str = Field(default="https://api.aci.dev", env="ACI_DEV_BASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()