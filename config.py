"""Configuration management for the Relationship Therapist System"""

import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

class VectorDBType(str, Enum):
    NONE = "none"
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    CHROMA = "chroma"

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "Relationship Therapist System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    DEBUG: bool = True
    CORS_ORIGINS: list = ["*"]
    
    # Database Settings
    database_type: DatabaseType = DatabaseType.SQLITE
    database_url: str = "sqlite:///./relationship_therapist.db"
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    
    # Vector Database Settings
    vector_db_type: VectorDBType = VectorDBType.NONE
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    # Redis Settings
    redis_enabled: bool = True
    redis_url: str = "redis://localhost:6379"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # AI/ML Settings
    ai_provider: AIProvider = AIProvider.LOCAL
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Authentication & Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Encryption
    encryption_key: Optional[str] = None
    
    # File Upload Settings
    max_file_size: int = 52428800
    allowed_file_types: list = [
        "text/plain", "application/pdf", "image/jpeg", "image/png", 
        "audio/mpeg", "audio/wav", "application/zip"
    ]
    upload_directory: str = "./data/uploads"
    
    # Knowledge Base Settings
    knowledge_base_directory: str = "./knowledge_base/documents"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Real-time Settings
    websocket_timeout: int = 300
    recommendation_cache_ttl: int = 3600
    
    # Celery Settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow"
    }

    def get_database_url(self) -> str:
        """Get the appropriate database URL based on configuration"""
        if self.database_type == DatabaseType.POSTGRESQL:
            if all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
                return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            else:
                raise ValueError("PostgreSQL configuration incomplete")
        return self.database_url
    
    def get_redis_url(self) -> str:
        """Get Redis URL with authentication if provided"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def is_ai_enabled(self) -> bool:
        """Check if AI provider is properly configured"""
        if self.ai_provider == AIProvider.OPENAI:
            return bool(self.openai_api_key)
        elif self.ai_provider == AIProvider.ANTHROPIC:
            return bool(self.anthropic_api_key)
        return True  # Local provider doesn't need API key
    
    def is_vector_db_enabled(self) -> bool:
        """Check if vector database is enabled and configured"""
        if self.vector_db_type == VectorDBType.QDRANT:
            return True  # Qdrant can work without API key for local instances
        elif self.vector_db_type == VectorDBType.PINECONE:
            return bool(self.pinecone_api_key and self.pinecone_environment)
        return self.vector_db_type != VectorDBType.NONE

# Global settings instance
settings = Settings()

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "debug": True,
    "reload": True,
    "log_level": "DEBUG"
}

PRODUCTION_CONFIG = {
    "debug": False,
    "reload": False,
    "log_level": "INFO",
    "cors_origins": ["https://yourdomain.com"]
}

TESTING_CONFIG = {
    "database_url": "sqlite:///./test_relationship_therapist.db",
    "redis_db": 1,
    "log_level": "WARNING"
}

def get_config() -> Settings:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        for key, value in PRODUCTION_CONFIG.items():
            setattr(settings, key, value)
    elif env == "testing":
        for key, value in TESTING_CONFIG.items():
            setattr(settings, key, value)
    else:  # development
        for key, value in DEVELOPMENT_CONFIG.items():
            setattr(settings, key, value)
    
    return settings