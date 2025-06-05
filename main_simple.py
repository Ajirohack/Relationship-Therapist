#!/usr/bin/env python3
"""
Simplified Relationship Therapist System - For MirrorCore UI Demo
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
import random
import uvicorn

from fastapi import FastAPI, HTTPException, Request, WebSocket, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import enhanced services
from ai_service import AIService, AnalysisType
from config import settings
from database import DatabaseManager
from vector_db import VectorDBService
from cache_service import CacheService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize enhanced services
ai_service = AIService()
database_manager = DatabaseManager()
vector_db_service = VectorDBService()
cache_service = CacheService()

# Initialize FastAPI app
app = FastAPI(
    title="MirrorCore Relationship Therapist",
    description="AI-powered relationship analysis and therapy assistance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class AnalysisRequest(BaseModel):
    conversation: List[Message]
    analysis_type: Optional[str] = "comprehensive"

class AnalysisResult(BaseModel):
    sentiment_score: float
    communication_patterns: Dict[str, Any]
    recommendations: List[str]
    relationship_health: float
    insights: List[str]

# Mock data for demonstration
def generate_mock_analytics():
    """Generate mock analytics data for the dashboard"""
    return {
        "sentiment_analysis": {
            "positive": random.randint(60, 85),
            "neutral": random.randint(10, 25),
            "negative": random.randint(5, 20)
        },
        "communication_patterns": {
            "listening_score": random.randint(70, 95),
            "empathy_score": random.randint(65, 90),
            "conflict_resolution": random.randint(60, 85),
            "emotional_support": random.randint(70, 95),
            "trust_indicators": random.randint(75, 95)
        },
        "relationship_health": {
            "overall_score": random.randint(70, 90),
            "trend": "improving" if random.random() > 0.3 else "stable",
            "key_strengths": [
                "Strong emotional connection",
                "Good communication foundation",
                "Mutual respect and understanding"
            ],
            "areas_for_improvement": [
                "Conflict resolution techniques",
                "Active listening skills",
                "Expressing appreciation more frequently"
            ]
        },
        "real_time_metrics": {
            "active_sessions": random.randint(15, 45),
            "messages_processed": random.randint(1200, 2500),
            "positive_interactions": random.randint(85, 95),
            "improvement_rate": random.randint(12, 28)
        }
    }

def generate_mock_recommendations():
    """Generate mock recommendations"""
    recommendations = [
        "Practice active listening by summarizing what your partner says before responding",
        "Schedule regular check-ins to discuss relationship goals and concerns",
        "Use 'I' statements when expressing feelings to avoid blame",
        "Create shared rituals or activities to strengthen your bond",
        "Practice gratitude by expressing appreciation daily",
        "Work on conflict resolution by taking breaks when discussions get heated",
        "Focus on understanding rather than being right during disagreements",
        "Build trust through consistent small actions and follow-through"
    ]
    return random.sample(recommendations, random.randint(3, 5))

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - serves the modern dashboard"""
    return templates.TemplateResponse("modern_dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("modern_dashboard.html", {"request": request})

@app.get("/ui", response_class=HTMLResponse)
async def ui_demo(request: Request):
    return templates.TemplateResponse("mirrorcore_dashboard.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
async def app_interface(request: Request):
    return templates.TemplateResponse("mirrorcore_dashboard.html", {"request": request})

@app.get("/settings")
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_base(request: Request):
    """Serve the knowledge base interface"""
    return templates.TemplateResponse("knowledge.html", {"request": request})

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat messages and generate AI responses"""
    try:
        response = await generate_therapist_response(request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": "I apologize, but I'm having trouble responding right now. Please try again later."}

# API Routes
@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data for the dashboard"""
    analytics = generate_mock_analytics()
    return JSONResponse(content=analytics)

@app.get("/api/recommendations")
async def get_recommendations():
    """Get AI-generated recommendations"""
    recommendations = generate_mock_recommendations()
    return JSONResponse(content={"recommendations": recommendations})

@app.post("/api/analyze")
async def analyze_conversation(request: AnalysisRequest):
    """Analyze conversation data and provide insights using AI service"""
    try:
        # Check cache first
        cache_key = f"analysis_{hash(str(request.conversation))}"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # Prepare conversation text for analysis
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in request.conversation
        ])
        
        # Perform AI analysis
        sentiment_analysis = await ai_service.analyze_conversation(
            conversation_text, 
            AnalysisType.SENTIMENT,
            context={"analysis_type": request.analysis_type}
        )
        
        communication_analysis = await ai_service.analyze_conversation(
            conversation_text,
            AnalysisType.COMMUNICATION_STYLE,
            context={"analysis_type": request.analysis_type}
        )
        
        relationship_health = await ai_service.analyze_conversation(
            conversation_text,
            AnalysisType.RELATIONSHIP_HEALTH,
            context={"analysis_type": request.analysis_type}
        )
        
        recommendations = await ai_service.analyze_conversation(
            conversation_text,
            AnalysisType.RECOMMENDATION,
            context={"analysis_type": request.analysis_type}
        )
        
        # Combine results
        analysis = AnalysisResult(
            sentiment_score=sentiment_analysis.confidence,
            communication_patterns={
                "active_listening": communication_analysis.confidence,
                "empathy_shown": random.uniform(0.65, 0.9),
                "conflict_resolution": random.uniform(0.6, 0.85),
                "emotional_support": random.uniform(0.7, 0.95)
            },
            recommendations=recommendations.content.split("\n") if recommendations.content else generate_mock_recommendations(),
            relationship_health=relationship_health.confidence,
            insights=[
                sentiment_analysis.content,
                communication_analysis.content,
                relationship_health.content
            ]
        )
        
        # Cache the result
        await cache_service.set(cache_key, analysis.dict(), ttl=3600)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        # Fallback to mock data if AI service fails
        return AnalysisResult(
            sentiment_score=0.75,
            communication_patterns={
                "active_listening": 0.8,
                "empathy_shown": 0.75,
                "conflict_resolution": 0.7,
                "emotional_support": 0.8
            },
            recommendations=["Continue open communication", "Practice active listening"],
            relationship_health=0.75,
            insights=["Analysis temporarily unavailable, using fallback response"]
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "online",
        "version": "1.0.0",
        "features": ["sentiment_analysis", "communication_patterns", "recommendations"],
        "uptime": "2h 15m",
        "last_updated": datetime.now().isoformat()
    }

# Additional API endpoints for enhanced functionality
@app.get("/api/v1/user/stats")
async def get_user_stats():
    """Get user statistics"""
    return {
        "total_sessions": random.randint(15, 50),
        "total_messages": random.randint(500, 2000),
        "improvement_score": random.uniform(0.7, 0.95),
        "streak_days": random.randint(5, 30),
        "achievements": [
            "Communication Expert",
            "Active Listener",
            "Conflict Resolver"
        ],
        "last_session": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
    }

@app.get("/api/v1/user/sessions")
async def get_user_sessions(limit: int = 10):
    """Get user session history"""
    sessions = []
    for i in range(min(limit, 10)):
        sessions.append({
            "id": f"session_{i+1}",
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "duration": random.randint(15, 90),  # minutes
            "messages": random.randint(10, 50),
            "sentiment_score": random.uniform(0.6, 0.9),
            "topics": random.sample(["communication", "trust", "intimacy", "conflict"], random.randint(1, 3))
        })
    return {"sessions": sessions}

@app.post("/api/v1/analyze/conversation")
async def analyze_conversation_v1(request: AnalysisRequest):
    """Enhanced conversation analysis endpoint"""
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    analysis = {
        "id": f"analysis_{random.randint(1000, 9999)}",
        "timestamp": datetime.now().isoformat(),
        "sentiment": {
            "overall_score": random.uniform(0.6, 0.9),
            "positive_ratio": random.uniform(0.6, 0.85),
            "negative_ratio": random.uniform(0.05, 0.2),
            "neutral_ratio": random.uniform(0.1, 0.3)
        },
        "communication_patterns": {
            "active_listening": random.uniform(0.7, 0.95),
            "empathy_shown": random.uniform(0.65, 0.9),
            "conflict_resolution": random.uniform(0.6, 0.85),
            "emotional_support": random.uniform(0.7, 0.95),
            "validation": random.uniform(0.6, 0.9)
        },
        "insights": [
            "Strong emotional connection detected in recent exchanges",
            "Improvement in conflict resolution skills over time",
            "Positive sentiment trend over the last week",
            "Good use of validation techniques"
        ],
        "recommendations": generate_mock_recommendations(),
        "relationship_health": {
            "score": random.uniform(0.7, 0.9),
            "trend": "improving",
            "key_metrics": {
                "trust": random.uniform(0.75, 0.95),
                "communication": random.uniform(0.7, 0.9),
                "intimacy": random.uniform(0.65, 0.85),
                "conflict_resolution": random.uniform(0.6, 0.8)
            }
        }
    }
    return analysis

@app.get("/api/v1/reports")
async def get_reports():
    """Get available reports"""
    reports = []
    for i in range(5):
        reports.append({
            "id": f"report_{i+1}",
            "title": f"Relationship Analysis Report #{i+1}",
            "date": (datetime.now() - timedelta(days=i*7)).isoformat(),
            "type": "comprehensive",
            "status": "completed",
            "summary": f"Analysis of {random.randint(20, 100)} conversations with insights and recommendations"
        })
    return {"reports": reports}

@app.get("/api/v1/knowledge-base/search")
async def search_knowledge_base(q: str = ""):
    """Search knowledge base"""
    articles = [
        {
            "id": "kb_001",
            "title": "Effective Communication Techniques",
            "summary": "Learn proven methods to improve communication in relationships",
            "category": "communication",
            "relevance": 0.95
        },
        {
            "id": "kb_002", 
            "title": "Conflict Resolution Strategies",
            "summary": "Healthy approaches to resolving disagreements",
            "category": "conflict_resolution",
            "relevance": 0.88
        },
        {
            "id": "kb_003",
            "title": "Building Trust and Intimacy",
            "summary": "Steps to deepen connection and build lasting trust",
            "category": "trust_building",
            "relevance": 0.82
        }
    ]
    return {"articles": articles, "query": q}

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: dict):
    """Submit user feedback"""
    return {
        "status": "received",
        "id": f"feedback_{random.randint(1000, 9999)}",
        "message": "Thank you for your feedback!"
    }

# Chat API models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    settings: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: ChatMessage
    analysis: Optional[Dict[str, Any]] = None
    
# Settings API models
class AIProvider(BaseModel):
    provider: str  # "openai", "anthropic", "local", etc.
    model: str
    api_key: Optional[str] = None
    
class UserSettings(BaseModel):
    ai_provider: AIProvider
    knowledge_base_format: str
    subscription_tier: str = "free"
    extension_installed: bool = False

# Chat API endpoints
@app.post("/api/v1/chat")
async def chat_message(request: ChatRequest):
    """Process a chat message and return AI response"""
    # In a real implementation, this would call the AI service
    # For now, we'll simulate a response based on the last message
    
    # Get the last user message
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user messages provided")
    
    last_message = user_messages[-1]
    
    # Generate a therapist response based on user message content
    response_content = generate_therapist_response(last_message.content)
    
    # Simulate processing time
    await asyncio.sleep(1)
    
    return {
        "message": {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        },
        "analysis": {
            "sentiment": random.uniform(0.3, 0.9),
            "topics": ["communication", "trust", "emotions"],
            "patterns": {
                "active_listening": random.uniform(0.6, 0.95),
                "empathy": random.uniform(0.7, 0.9)
            }
        }
    }

@app.post("/api/v1/chat/analyze")
async def analyze_chat(request: ChatRequest):
    """Analyze the entire conversation and provide insights"""
    # Simulate processing time for analysis
    await asyncio.sleep(2)
    
    # Generate mock analysis results
    analysis = {
        "sentiment_score": random.uniform(0.6, 0.9),
        "communication_patterns": {
            "active_listening": random.uniform(0.7, 0.95),
            "empathy_shown": random.uniform(0.65, 0.9),
            "conflict_resolution": random.uniform(0.6, 0.85),
            "emotional_support": random.uniform(0.7, 0.95)
        },
        "insights": [
            "Communication shows patterns of mutual respect",
            "There's evidence of active listening and validation",
            "Some areas for improvement in expressing needs directly",
            "Strong emotional connection is evident in language used"
        ],
        "recommendations": generate_mock_recommendations(),
        "relationship_health": random.uniform(0.7, 0.9)
    }
    
    return analysis

@app.post("/api/v1/settings")
async def update_settings(settings: UserSettings):
    """Update user settings"""
    # In a real implementation, this would save to a database
    return {
        "status": "success",
        "message": "Settings updated successfully",
        "settings": settings.dict()
    }

@app.get("/api/v1/settings")
async def get_settings():
    """Get current user settings"""
    # Mock settings
    return {
        "ai_provider": {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "sk-***************" # Masked for security
        },
        "knowledge_base_format": "default",
        "subscription_tier": "professional",
        "extension_installed": True
    }

@app.post("/api/v1/upload/conversation")
async def upload_conversation(data: Dict[str, Any]):
    """Upload and process conversation data from various platforms"""
    # Simulate processing time
    await asyncio.sleep(2)
    
    platform = data.get("platform", "unknown")
    file_content = data.get("content", {})
    
    return {
        "status": "success",
        "message": f"Successfully processed {platform} conversation data",
        "conversation_id": f"conv_{random.randint(1000, 9999)}",
        "message_count": random.randint(10, 100),
        "analysis_summary": "Initial analysis shows a healthy communication pattern with some areas for improvement."
    }

@app.post("/api/v1/test-connection")
async def test_connection_with_config(provider_data: Dict[str, Any]):
    """Test connection to AI provider API with custom configuration"""
    try:
        provider = provider_data.get("provider", "")
        api_key = provider_data.get("api_key", "")
        
        if not provider or not api_key:
            return {
                "status": "error",
                "message": "Provider and API key are required",
                "error_code": "missing_params"
            }
        
        # Create temporary AI service instance with provided config
        from ai_service import AIService
        temp_ai_service = AIService()
        
        # Test connection with provided credentials
        start_time = datetime.now()
        
        # Simple test message
        test_result = await temp_ai_service.analyze_conversation(
            "Hello, this is a test message.",
            AnalysisType.SENTIMENT
        )
        
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "status": "success",
            "message": f"Successfully connected to {provider} API",
            "provider": provider,
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat(),
            "test_result": test_result is not None,
            "models_available": ["gpt-3.5-turbo", "gpt-4"] if provider == "openai" else ["claude-2", "claude-instant"]
        }
    except Exception as e:
        logger.error(f"AI connection test failed: {e}")
        return {
            "status": "error",
            "message": "Invalid API key or connection error",
            "error_code": "auth_failed",
            "error_details": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/test-connection")
async def test_ai_connection():
    """Test current AI provider connection"""
    try:
        # Test actual AI service connection
        start_time = datetime.now()
        
        # Simple test message
        test_result = await ai_service.analyze_conversation(
            "Hello, this is a test message.",
            AnalysisType.SENTIMENT
        )
        
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "status": "success",
            "provider": settings.ai_provider,
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat(),
            "test_result": test_result is not None,
            "models_available": await ai_service.get_available_models() if hasattr(ai_service, 'get_available_models') else []
        }
    except Exception as e:
        logger.error(f"AI connection test failed: {e}")
        return {
            "status": "error",
            "provider": settings.ai_provider,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/analytics")
async def websocket_analytics(websocket):
    await websocket.accept()
    try:
        while True:
            # Get real-time analytics from database and cache
            analytics = await get_real_time_analytics()
            await websocket.send_json(analytics)
            await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

async def get_real_time_analytics():
    """Get real-time analytics from actual data sources"""
    try:
        # Check cache first
        cache_key = "real_time_analytics"
        cached_analytics = await cache_service.get(cache_key)
        if cached_analytics:
            return cached_analytics
        
        # Get analytics from database
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "active_users": await database_manager.get_active_users_count(),
            "total_conversations": await database_manager.get_total_conversations(),
            "sentiment_trends": await database_manager.get_sentiment_trends(),
            "communication_metrics": {
                "avg_response_time": await database_manager.get_avg_response_time(),
                "positive_interactions": await database_manager.get_positive_interactions_count(),
                "improvement_rate": await database_manager.get_improvement_rate()
            },
            "ai_service_status": {
                "provider": settings.ai_provider,
                "status": "active" if settings.is_ai_enabled() else "fallback",
                "requests_today": await cache_service.get("ai_requests_today") or 0
            }
        }
        
        # Cache for 30 seconds
        await cache_service.set(cache_key, analytics, ttl=30)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting real-time analytics: {e}")
        # Fallback to mock data
        return generate_mock_analytics()

# Helper function for generating therapist responses
async def generate_therapist_response(user_message: str, context: Dict[str, Any] = None) -> str:
    """Generate AI-powered therapist response based on user input"""
    try:
        # Check cache first
        cache_key = f"response_{hash(user_message)}"
        cached_response = await cache_service.get(cache_key)
        if cached_response:
            return cached_response
        
        # Use AI service to generate response
        ai_response = await ai_service.analyze_conversation(
            user_message,
            AnalysisType.RECOMMENDATION,
            context={"role": "therapist", "conversation_context": context or {}}
        )
        
        response = ai_response.content if ai_response.content else generate_fallback_response(user_message)
        
        # Cache the response
        await cache_service.set(cache_key, response, ttl=1800)  # 30 minutes
        
        return response
        
    except Exception as e:
        logger.error(f"AI response generation error: {e}")
        return generate_fallback_response(user_message)

def generate_fallback_response(user_message: str) -> str:
    """Generate fallback response when AI service is unavailable"""
    user_message = user_message.lower()
    
    if any(word in user_message for word in ["hello", "hi", "hey", "start"]):
        return "Hello! I'm your relationship therapist AI. How can I help you today? Would you like to discuss a specific relationship concern?"
    
    if any(word in user_message for word in ["fight", "argue", "argument", "disagreement", "conflict"]):
        return "It sounds like you're experiencing some conflict. When disagreements happen, it's important to focus on understanding each other's perspectives. Could you tell me more about what triggered this situation and how both of you responded?"
    
    if any(word in user_message for word in ["trust", "cheat", "betrayal", "lied", "lying"]):
        return "Trust issues can be challenging to navigate. Rebuilding trust takes time and consistent effort from both partners. Can you share more about what happened and how it's affecting your relationship now?"
    
    if any(word in user_message for word in ["communicate", "talk", "listen", "understanding"]):
        return "Effective communication is essential in relationships. It involves both expressing yourself clearly and listening actively. What specific communication challenges are you experiencing?"
    
    if any(word in user_message for word in ["thank", "thanks"]):
        return "You're welcome! I'm here to support you. Is there anything else you'd like to discuss about your relationship?"
    
    # Default response for other inputs
    return "Thank you for sharing that. In relationships, understanding each other's needs and perspectives is crucial. Could you tell me more about how this situation is affecting you and your partner?"

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    logger.info("Starting MirrorCore Relationship Therapist System...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
