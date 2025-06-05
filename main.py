#!/usr/bin/env python3
"""
Relationship Therapist System - Main Application
A comprehensive AI-powered relationship analysis and guidance system
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import asyncio
from datetime import datetime
import logging
import uvicorn
from pathlib import Path

# Import custom modules
from conversation_analyzer import ConversationAnalyzer
from ai_therapist import AITherapist
from knowledge_base import KnowledgeBase
from mcp_server import MCPServer
# UserProfile is defined in this file and database.py
from report_generator import ReportGenerator
from data_processor import DataProcessor
from real_time_monitor import RealTimeMonitor

# Import new enhanced services
from config import Settings
from auth import AuthService, get_current_user, get_current_active_user, require_role, User
from database import DatabaseManager
from ai_service import AIService
from vector_db import VectorDBService
from cache_service import CacheManager
from task_service import AsyncTaskManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Relationship Therapist System",
    description="AI-powered relationship analysis and therapy assistance",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize enhanced services
database_manager = DatabaseManager()
auth_service = AuthService()
ai_service = AIService()
vector_db_manager = VectorDBService()
cache_manager = CacheManager(settings)
task_manager = AsyncTaskManager(settings)

# Initialize existing components (updated to use new services)
conversation_analyzer = ConversationAnalyzer()
data_processor = DataProcessor()
knowledge_base = KnowledgeBase()
ai_therapist = AITherapist()
real_time_monitor = RealTimeMonitor(conversation_analyzer, ai_therapist)
report_generator = ReportGenerator()
mcp_server = MCPServer()

# Security
security = HTTPBearer()

# Pydantic models
class ConversationInput(BaseModel):
    user_id: str
    conversation_data: List[Dict[str, Any]]
    platform: Optional[str] = "unknown"
    metadata: Optional[Dict[str, Any]] = {}

class RealtimeInput(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = {}
    platform: Optional[str] = "unknown"

class UserProfileInput(BaseModel):
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    relationship_status: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    goals: Optional[List[str]] = []

# New authentication models
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Enhanced analysis models
class AdvancedAnalysisRequest(BaseModel):
    conversation_id: str
    analysis_type: str  # "sentiment", "patterns", "recommendations", "full"
    options: Optional[Dict[str, Any]] = {}

class KnowledgeUpload(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class AnalysisRequest(BaseModel):
    user_id: str
    conversation_history: List[Dict[str, Any]]
    analysis_type: str = "comprehensive"
    include_recommendations: bool = True

class RealtimeRecommendation(BaseModel):
    user_id: str
    current_conversation: str
    context: Optional[Dict[str, Any]] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    preferences: Dict[str, Any]
    relationship_goals: List[str]
    communication_style: str

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Relationship Therapist System API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await database_manager.health_check()
        
        # Check cache connection
        cache_status = await cache_manager.health_check()
        
        # Check vector database connection
        vector_db_status = await vector_db_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "cache": cache_status,
                "vector_db": vector_db_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        user = await auth_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        # Store refresh token
        await auth_service.store_refresh_token(user.id, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        user = await auth_service.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        # Store refresh token
        await auth_service.store_refresh_token(user.id, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/api/v1/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user and revoke refresh tokens"""
    try:
        await auth_service.revoke_user_tokens(current_user.id)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.post("/api/v1/upload/conversation")
async def upload_conversation(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process conversation file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.txt', '.json', '.csv', '.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Read file content
        content = await file.read()
        
        # Submit task for background processing
        task_id = await task_manager.submit_conversation_analysis(
            user_id=current_user.id,
            file_content=content,
            filename=file.filename,
            file_type=file.content_type
        )
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "task_id": task_id,
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.post("/api/v1/analyze/conversation")
async def analyze_conversation(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze conversation history with enhanced AI
    """
    try:
        # Verify user owns the conversation or has permission
        if request.user_id != current_user.id and current_user.role not in ["admin", "therapist"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check cache first
        cache_key = f"analysis:{request.user_id}:{hash(str(request.conversation_history))}"
        cached_result = await cache_manager.conversation_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Enhanced AI analysis
        analysis_result = await ai_service.analyze_conversation(
            conversation_data=request.conversation_history,
            user_id=request.user_id,
            analysis_type=request.analysis_type
        )
        
        if request.include_recommendations:
            recommendations = await ai_therapist.generate_recommendations(
                user_id=request.user_id,
                analysis=analysis_result
            )
            analysis_result["recommendations"] = recommendations
        
        # Store in database
        conversation_id = await database_manager.store_conversation(
            user_id=request.user_id,
            messages=request.conversation_history,
            analysis_result=analysis_result
        )
        
        # Cache result
        result = {
            "status": "success",
            "conversation_id": conversation_id,
            "analysis": analysis_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        await cache_manager.conversation_cache.set(cache_key, result, expire=3600)
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/realtime/recommendation")
async def get_realtime_recommendation(
    request: RealtimeInput,
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time recommendations with enhanced AI"""
    try:
        # Verify user access
        if request.user_id != current_user.id and current_user.role not in ["admin", "therapist"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Rate limiting check
        rate_limit_key = f"realtime:{current_user.id}"
        if not await cache_manager.rate_limiter.check_rate_limit(
            rate_limit_key, 
            limit=settings.REALTIME_RATE_LIMIT, 
            window=60
        ):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Get user context from database
        user_profile = await database_manager.get_user_profile(request.user_id)
        conversation_history = await database_manager.get_recent_conversations(
            request.user_id, 
            limit=10
        )
        
        # Enhanced real-time recommendation
        recommendation = await ai_service.get_realtime_recommendation(
            message=request.message,
            user_id=request.user_id,
            user_profile=user_profile,
            conversation_history=conversation_history,
            context=request.context,
            platform=request.platform
        )
        
        # Store interaction for learning
        await database_manager.store_realtime_interaction(
            user_id=request.user_id,
            message=request.message,
            recommendation=recommendation,
            platform=request.platform,
            context=request.context
        )
        
        return {
            "status": "success",
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Real-time recommendation failed: {e}")
        raise HTTPException(status_code=500, detail="Recommendation failed")

@app.post("/api/v1/user/profile")
async def create_user_profile(profile: UserProfile):
    """
    Create or update user profile
    """
    try:
        result = await knowledge_base.store_user_profile(profile.dict())
        return JSONResponse({
            "status": "success",
            "message": "User profile created/updated successfully",
            "profile_id": result["profile_id"]
        })
    
    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    Retrieve user profile
    """
    try:
        profile = await knowledge_base.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return JSONResponse({
            "status": "success",
            "profile": profile
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/user/{user_id}/report")
async def generate_user_report(user_id: str, report_type: str = "comprehensive"):
    """
    Generate comprehensive relationship analysis report
    """
    try:
        report = await report_generator.generate_report(
            user_id=user_id,
            report_type=report_type
        )
        
        return JSONResponse({
            "status": "success",
            "report": report,
            "generated_at": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/realtime/{user_id}")
async def websocket_realtime_monitoring(websocket, user_id: str):
    """
    WebSocket endpoint for real-time conversation monitoring
    """
    await real_time_monitor.handle_websocket_connection(websocket, user_id)

@app.post("/api/v1/knowledge/upload")
async def upload_knowledge_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("general")
):
    """
    Upload knowledge base documents (PDFs, text files, etc.)
    """
    try:
        result = await knowledge_base.ingest_documents(files, category)
        return JSONResponse({
            "status": "success",
            "message": "Knowledge documents uploaded successfully",
            "processed_documents": result["processed_count"]
        })
    
    except Exception as e:
        logger.error(f"Knowledge upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP Server Integration
@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    try:
        logger.info("Starting Relationship Therapist System v2.0.0...")
        
        # Initialize database
        await database_manager.connect()
        await database_manager.create_tables()
        logger.info("Database initialized successfully")
        
        # Initialize authentication service
        await auth_service.initialize()
        logger.info("Authentication service initialized")
        
        # Initialize vector database
        await vector_db_manager.initialize()
        logger.info("Vector database initialized")
        
        # Initialize cache manager
        await cache_manager.initialize()
        logger.info("Cache manager initialized")
        
        # Initialize task manager
        await task_manager.initialize()
        logger.info("Task manager initialized")
        
        # Initialize AI service
        await ai_service.initialize()
        logger.info("AI service initialized")
        
        # Load knowledge base with vector embeddings
        await knowledge_base.load_knowledge_base()
        if vector_db_manager.is_available():
            await knowledge_base.build_vector_index(vector_db_manager)
        logger.info("Knowledge base loaded successfully")
        
        # Start MCP server
        await mcp_server.start()
        logger.info("MCP server started successfully")
        
        logger.info("All services started successfully!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup all services on shutdown"""
    try:
        logger.info("Shutting down Relationship Therapist System...")
        
        # Stop MCP server
        await mcp_server.stop()
        logger.info("MCP server stopped")
        
        # Cleanup task manager
        await task_manager.cleanup()
        logger.info("Task manager cleaned up")
        
        # Cleanup cache manager
        await cache_manager.cleanup()
        logger.info("Cache manager cleaned up")
        
        # Cleanup vector database
        await vector_db_manager.cleanup()
        logger.info("Vector database cleaned up")
        
        # Disconnect database
        await database_manager.disconnect()
        logger.info("Database disconnected")
        
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )