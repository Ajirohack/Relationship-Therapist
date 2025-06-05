#!/usr/bin/env python3
"""
Startup Script for Relationship Therapist AI System
Quick setup and launch script with health checks
"""

import os
import sys
import subprocess
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
        
    def check_python_version(self) -> bool:
        """
        Check if Python version is compatible
        """
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        
        logger.info(f"Python version: {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def check_dependencies(self) -> bool:
        """
        Check if required system dependencies are available
        """
        logger.info("Checking system dependencies...")
        
        dependencies = {
            "pip": "pip --version",
            "git": "git --version"
        }
        
        missing = []
        
        for dep, cmd in dependencies.items():
            try:
                subprocess.run(cmd.split(), capture_output=True, check=True)
                logger.info(f"{dep}: Available ✓")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error(f"{dep}: Not found ✗")
                missing.append(dep)
        
        if missing:
            logger.error(f"Missing dependencies: {', '.join(missing)}")
            return False
        
        return True
    
    def create_virtual_environment(self) -> bool:
        """
        Create virtual environment if it doesn't exist
        """
        if self.venv_path.exists():
            logger.info("Virtual environment already exists ✓")
            return True
        
        logger.info("Creating virtual environment...")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True)
            logger.info("Virtual environment created ✓")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self) -> str:
        """
        Get path to Python executable in virtual environment
        """
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "python.exe")
        else:  # Unix/Linux/macOS
            return str(self.venv_path / "bin" / "python")
    
    def get_venv_pip(self) -> str:
        """
        Get path to pip executable in virtual environment
        """
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:  # Unix/Linux/macOS
            return str(self.venv_path / "bin" / "pip")
    
    def install_requirements(self) -> bool:
        """
        Install Python requirements
        """
        if not self.requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
        
        logger.info("Installing Python requirements...")
        try:
            # Upgrade pip first
            subprocess.run([
                self.get_venv_pip(), "install", "--upgrade", "pip"
            ], check=True)
            
            # Install requirements
            subprocess.run([
                self.get_venv_pip(), "install", "-r", str(self.requirements_file)
            ], check=True)
            
            logger.info("Requirements installed ✓")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install requirements: {e}")
            return False
    
    def download_models(self) -> bool:
        """
        Download required AI models
        """
        logger.info("Downloading required AI models...")
        
        models_to_download = [
            "python -m spacy download en_core_web_sm",
            "python -c \"import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')\""
        ]
        
        for cmd in models_to_download:
            try:
                # Use virtual environment python
                cmd_parts = cmd.split()
                cmd_parts[0] = self.get_venv_python()
                
                subprocess.run(cmd_parts, check=True, shell=False)
                logger.info(f"Model download completed: {cmd.split()[-1]} ✓")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Model download failed (will try at runtime): {e}")
                # Don't fail the entire setup for model downloads
        
        return True
    
    def setup_environment(self) -> bool:
        """
        Set up environment configuration
        """
        if self.env_file.exists():
            logger.info(".env file already exists ✓")
            return True
        
        if not self.env_example.exists():
            logger.warning(".env.example not found, skipping environment setup")
            return True
        
        logger.info("Creating .env file from template...")
        try:
            # Copy .env.example to .env
            with open(self.env_example, 'r') as src:
                content = src.read()
            
            with open(self.env_file, 'w') as dst:
                dst.write(content)
            
            logger.info(".env file created ✓")
            logger.warning("Please edit .env file with your configuration before running the system")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def create_directories(self) -> bool:
        """
        Create necessary directories
        """
        logger.info("Creating necessary directories...")
        
        directories = [
            "uploads",
            "reports",
            "knowledge_base",
            "temp",
            "logs",
            "models",
            "backups"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Directory created: {dir_name} ✓")
        
        return True
    
    def run_health_check(self) -> bool:
        """
        Run basic health check
        """
        logger.info("Running system health check...")
        
        try:
            # Try to import main modules
            sys.path.insert(0, str(self.project_root))
            
            import main
            logger.info("Main module import: ✓")
            
            # Check if we can create basic instances
            from conversation_analyzer import ConversationAnalyzer
            analyzer = ConversationAnalyzer()
            logger.info("Conversation Analyzer: ✓")
            
            from ai_therapist import AITherapist
            therapist = AITherapist()
            logger.info("AI Therapist: ✓")
            
            logger.info("Health check completed ✓")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000, 
                    reload: bool = True, workers: int = 1) -> None:
        """
        Start the FastAPI server
        """
        logger.info(f"Starting server on {host}:{port}...")
        
        try:
            cmd = [
                self.get_venv_python(), "-m", "uvicorn", "main:app",
                "--host", host,
                "--port", str(port)
            ]
            
            if reload:
                cmd.append("--reload")
            
            if workers > 1:
                cmd.extend(["--workers", str(workers)])
            
            # Change to project directory
            os.chdir(self.project_root)
            
            logger.info(f"Server command: {' '.join(cmd)}")
            logger.info(f"API Documentation: http://{host}:{port}/docs")
            logger.info(f"Health Check: http://{host}:{port}/health")
            logger.info("Press Ctrl+C to stop the server")
            
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
    
    def setup_system(self) -> bool:
        """
        Complete system setup
        """
        logger.info("Starting Relationship Therapist AI System Setup")
        logger.info("=" * 60)
        
        setup_steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking dependencies", self.check_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing requirements", self.install_requirements),
            ("Downloading AI models", self.download_models),
            ("Setting up environment", self.setup_environment),
            ("Creating directories", self.create_directories),
            ("Running health check", self.run_health_check)
        ]
        
        for step_name, step_func in setup_steps:
            logger.info(f"\n{step_name}...")
            if not step_func():
                logger.error(f"Setup failed at: {step_name}")
                return False
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Edit .env file with your configuration")
        logger.info("2. Run: python start.py --run")
        logger.info("3. Visit http://localhost:8000/docs for API documentation")
        logger.info("=" * 60)
        
        return True
    
    def run_tests(self) -> bool:
        """
        Run system tests
        """
        logger.info("Running system tests...")
        
        try:
            test_script = self.project_root / "test_system.py"
            if not test_script.exists():
                logger.error("test_system.py not found")
                return False
            
            result = subprocess.run([
                self.get_venv_python(), str(test_script)
            ], cwd=self.project_root)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Relationship Therapist AI System Startup Script"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true", 
        help="Run complete system setup"
    )
    
    parser.add_argument(
        "--run", 
        action="store_true", 
        help="Start the server"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run system tests"
    )
    
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Server host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Server port (default: 8000)"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--no-reload", 
        action="store_true", 
        help="Disable auto-reload in development"
    )
    
    args = parser.parse_args()
    
    starter = SystemStarter()
    
    # If no specific action is specified, show help
    if not any([args.setup, args.run, args.test]):
        parser.print_help()
        print("\nQuick start:")
        print("  python start.py --setup    # First time setup")
        print("  python start.py --run      # Start the server")
        print("  python start.py --test     # Run tests")
        return
    
    # Run setup if requested
    if args.setup:
        if not starter.setup_system():
            sys.exit(1)
        return
    
    # Run tests if requested
    if args.test:
        if not starter.run_tests():
            sys.exit(1)
        return
    
    # Start server if requested
    if args.run:
        # Quick health check before starting
        if not starter.run_health_check():
            logger.error("Health check failed. Run --setup first.")
            sys.exit(1)
        
        starter.start_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            workers=args.workers
        )

if __name__ == "__main__":
    main()