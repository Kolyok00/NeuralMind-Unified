"""
Configuration management for GarvisNeuralMind Community System.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic app settings
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost/garvisneuralmind",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Community Features
    DISCORD_BOT_TOKEN: Optional[str] = Field(default=None, env="DISCORD_BOT_TOKEN")
    DISCORD_GUILD_ID: Optional[str] = Field(default=None, env="DISCORD_GUILD_ID")
    
    # VTuber Features
    VTUBE_STUDIO_PORT: int = Field(default=8001, env="VTUBE_STUDIO_PORT")
    ENABLE_VOICE_SYNTHESIS: bool = Field(default=True, env="ENABLE_VOICE_SYNTHESIS")
    
    # Community Moderation
    MAX_MESSAGE_LENGTH: int = Field(default=2000, env="MAX_MESSAGE_LENGTH")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # File Storage
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # Email (for community notifications)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = Field(default=None, env="FROM_EMAIL")
    
    # Analytics and Monitoring
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Plugin System
    PLUGINS_DIR: str = Field(default="plugins", env="PLUGINS_DIR")
    ENABLE_PLUGIN_SYSTEM: bool = Field(default=True, env="ENABLE_PLUGIN_SYSTEM")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Community feature flags
class CommunityFeatures:
    """Feature flags for community functionality."""
    
    # Core features
    USER_PROFILES: bool = True
    SOCIAL_INTERACTIONS: bool = True
    REAL_TIME_CHAT: bool = True
    
    # Social features  
    FRIEND_SYSTEM: bool = True
    GROUPS_AND_COMMUNITIES: bool = True
    USER_GENERATED_CONTENT: bool = True
    
    # VTuber features
    AVATAR_SYSTEM: bool = True
    VOICE_INTERACTION: bool = True
    LIVE_STREAMING: bool = True
    
    # Moderation
    AUTO_MODERATION: bool = True
    COMMUNITY_MODERATION: bool = True
    CONTENT_FILTERING: bool = True
    
    # Gamification
    ACHIEVEMENTS: bool = True
    REPUTATION_SYSTEM: bool = True
    LEADERBOARDS: bool = True
    
    # AI Features
    AI_COMPANIONS: bool = True
    PERSONALIZED_CONTENT: bool = True
    AI_MODERATION: bool = True
    
    # Beta features (can be toggled)
    COMMUNITY_MARKETPLACE: bool = False
    NFT_INTEGRATION: bool = False
    CRYPTO_REWARDS: bool = False


def get_community_features() -> CommunityFeatures:
    """Get community feature flags."""
    return CommunityFeatures()