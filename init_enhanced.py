#!/usr/bin/env python3
"""
Enhanced Backend Initialization Script
Initializes database, services, and starts the application
"""

import asyncio
import logging
import os
from pathlib import Path

# Import configuration and services
from config import settings, get_config
from database import DatabaseManager
from ai_service import AIService
from vector_db import VectorDBService
from cache_service import CacheService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize database tables and schema"""
    logger.info("Initializing database...")
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

async def initialize_ai_service():
    """Initialize AI service and test connections"""
    logger.info("Initializing AI service...")
    try:
        ai_service = AIService()
        if settings.is_ai_enabled():
            logger.info(f"AI provider: {settings.ai_provider}")
            # Test AI connection with a simple query
            test_response = await ai_service.analyze_conversation(
                "Hello, this is a test message.",
                "sentiment"
            )
            logger.info(f"AI service test successful: {test_response.provider}")
        else:
            logger.warning("AI service not configured, using local fallback")
        return True
    except Exception as e:
        logger.error(f"AI service initialization failed: {e}")
        return False

async def initialize_vector_db():
    """Initialize vector database if enabled"""
    if not settings.is_vector_db_enabled():
        logger.info("Vector database disabled")
        return True
        
    logger.info("Initializing vector database...")
    try:
        vector_db = VectorDBService()
        await vector_db.initialize()
        logger.info(f"Vector database initialized: {settings.vector_db_type}")
        return True
    except Exception as e:
        logger.error(f"Vector database initialization failed: {e}")
        return False

async def initialize_cache():
    """Initialize cache service"""
    logger.info("Initializing cache service...")
    try:
        cache_service = CacheService()
        # Test cache connection
        await cache_service.set("test_key", "test_value", ttl=60)
        test_value = await cache_service.get("test_key")
        if test_value == "test_value":
            logger.info("Cache service initialized successfully")
            await cache_service.delete("test_key")
        else:
            logger.warning("Cache test failed, using fallback")
        return True
    except Exception as e:
        logger.error(f"Cache service initialization failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        settings.upload_directory,
        settings.knowledge_base_directory,
        "./data/uploads",
        "./reports/generated",
        "./static",
        "./templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")

def check_environment():
    """Check environment configuration"""
    logger.info("Checking environment configuration...")
    
    # Check required environment variables
    required_vars = ["SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly")
    
    # Check AI provider configuration
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        logger.warning("OpenAI API key not configured")
    elif settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
        logger.warning("Anthropic API key not configured")
    
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database: {settings.database_type}")
    logger.info(f"AI Provider: {settings.ai_provider}")
    logger.info(f"Vector DB: {settings.vector_db_type}")

async def main():
    """Main initialization function"""
    logger.info("Starting MirrorCore Relationship Therapist System initialization...")
    
    # Load configuration
    config = get_config()
    
    # Check environment
    check_environment()
    
    # Create directories
    create_directories()
    
    # Initialize services
    services = [
        ("Database", initialize_database()),
        ("Cache", initialize_cache()),
        ("Vector DB", initialize_vector_db()),
        ("AI Service", initialize_ai_service())
    ]
    
    success_count = 0
    for service_name, service_init in services:
        try:
            success = await service_init
            if success:
                success_count += 1
                logger.info(f"✓ {service_name} initialized")
            else:
                logger.error(f"✗ {service_name} failed")
        except Exception as e:
            logger.error(f"✗ {service_name} failed with exception: {e}")
    
    logger.info(f"Initialization complete: {success_count}/{len(services)} services ready")
    
    if success_count >= 2:  # At least database and cache
        logger.info("System ready to start!")
        return True
    else:
        logger.error("Critical services failed, system may not function properly")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        logger.info("Initialization successful - ready to start server")
        exit(0)
    else:
        logger.error("Initialization failed")
        exit(1)