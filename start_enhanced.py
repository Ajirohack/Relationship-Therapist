#!/usr/bin/env python3
"""
Enhanced Backend Startup Script
Runs initialization and starts the FastAPI server with all integrations
"""

import asyncio
import logging
import subprocess
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from init_enhanced import main as init_main

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'jinja2',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.error("Please install them with: pip install -r requirements.txt")
        return False
    
    logger.info("All required dependencies found")
    return True

def start_server():
    """Start the FastAPI server"""
    logger.info("Starting FastAPI server...")
    
    # Determine which main file to use
    main_file = "main_simple.py" if Path("main_simple.py").exists() else "main.py"
    
    cmd = [
        "uvicorn",
        f"{main_file.replace('.py', '')}:app",
        "--host", settings.host,
        "--port", str(settings.port),
        "--log-level", settings.log_level.lower()
    ]
    
    if settings.reload and settings.environment == "development":
        cmd.append("--reload")
    
    logger.info(f"Starting server with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return True
    
    return True

async def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("Core Engine Relationship Therapist System - Enhanced Backend")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        return False
    
    # Run initialization
    logger.info("Running system initialization...")
    init_success = await init_main()
    
    if not init_success:
        logger.error("Initialization failed - starting with limited functionality")
        # Continue anyway for development
    
    logger.info("=" * 60)
    logger.info("System Status:")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Host: {settings.host}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"AI Provider: {settings.ai_provider}")
    logger.info(f"Database: {settings.database_type}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    logger.info("=" * 60)
    
    # Start the server
    return start_server()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            logger.info("Server shutdown complete")
            exit(0)
        else:
            logger.error("Server failed to start")
            exit(1)
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"Startup failed with exception: {e}")
        exit(1)