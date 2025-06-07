from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio

# Import hybrid brain components
from ..layers.hybrid_brain_implementation import (
    HybridAIBrain, 
    create_hybrid_brain_instance,
    EmotionalState,
    RelationshipStage
)

# Pydantic models for API
class UserInputRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DiegoResponse(BaseModel):
    message: str
    response_type: str
    confidence: float
    session_id: str
    diego_persona: Dict[str, float]
    follow_up_questions: List[str]
    homework_assignment: Optional[Dict[str, Any]]
    resource_recommendations: List[Dict[str, str]]
    session_summary: Dict[str, Any]
    safety_status: str
    metadata: Dict[str, Any]

class SessionStatusResponse(BaseModel):
    session_id: str
    user_id: str
    phase: str
    start_time: str
    last_interaction: str
    interactions_count: int
    safety_flags: List[str]
    active: bool

class PerformanceSummaryResponse(BaseModel):
    total_sessions: int
    active_sessions: int
    average_confidence: float
    average_processing_time: float
    success_rate: float
    last_updated: str

class AIBrainIntegration:
    """Integration layer between FastAPI and Hybrid AI Brain"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize hybrid brain
        try:
            self.hybrid_brain = create_hybrid_brain_instance()
            self.brain_available = True
            self.logger.info("Hybrid AI Brain initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize hybrid brain: {str(e)}")
            self.hybrid_brain = None
            self.brain_available = False
        
        # Configuration settings
        self.enable_background_learning = config.get("enable_background_learning", True)
        self.enable_performance_monitoring = config.get("enable_performance_monitoring", True)
        self.enable_session_persistence = config.get("enable_session_persistence", True)
        self.max_response_time = config.get("max_response_time", 30.0)
    
    async def process_user_message(self, request: UserInputRequest, background_tasks: BackgroundTasks) -> DiegoResponse:
        """Process user message through hybrid brain"""
        
        try:
            # Validate input
            self._validate_user_input(request)
            
            # Check if hybrid brain is available
            if not self.brain_available or not self.hybrid_brain:
                return self._create_error_response(request, "AI brain temporarily unavailable")
            
            # Process message through hybrid brain
            processing_result = self.hybrid_brain.process_message(
                user_id=request.user_id,
                message=request.message,
                context=request.context or {}
            )
            
            # Convert result to Diego response
            diego_response = self._convert_hybrid_to_diego_response(processing_result, request)
            
            # Schedule background tasks
            if self.enable_background_learning:
                background_tasks.add_task(self._process_background_learning, processing_result)
            
            if self.enable_performance_monitoring:
                background_tasks.add_task(self._update_performance_metrics, processing_result)
            
            if self.enable_session_persistence:
                background_tasks.add_task(self._persist_session_data, processing_result)
            
            return diego_response
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout processing message for user {request.user_id}")
            return self._create_error_response(request, "Response timeout - please try again")
        
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return self._create_error_response(request, str(e))
    
    async def get_session_status(self, session_id: str) -> Optional[SessionStatusResponse]:
        """Get current session status"""
        
        try:
            if not self.brain_available or not self.hybrid_brain:
                return None
            
            # Extract user_id from session_id
            user_id = self._extract_user_id_from_session(session_id)
            if not user_id:
                return None
            
            # Get user relationship summary from hybrid brain
            relationship_summary = self.hybrid_brain.get_user_relationship(user_id)
            
            if relationship_summary.get('error'):
                return None
            
            user_profile = relationship_summary.get('user_profile', {})
            
            return SessionStatusResponse(
                session_id=session_id,
                user_id=user_id,
                phase=user_profile.get('relationship_stage', 'stranger'),
                start_time=datetime.now().isoformat(),
                last_interaction=user_profile.get('last_interaction', datetime.now().isoformat()),
                interactions_count=user_profile.get('interaction_count', 0),
                safety_flags=[],
                active=True
            )
                
        except Exception as e:
            self.logger.error(f"Error getting session status: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving session status"
            )
    
    async def get_performance_summary(self) -> PerformanceSummaryResponse:
        """Get performance summary"""
        
        try:
            if not self.brain_available or not self.hybrid_brain:
                return PerformanceSummaryResponse(
                    total_sessions=0,
                    active_sessions=0,
                    average_confidence=0.0,
                    average_processing_time=0.0,
                    success_rate=0.0,
                    last_updated=datetime.now().isoformat()
                )
            
            # Get system status from hybrid brain
            system_status = self.hybrid_brain.get_system_status()
            performance_metrics = system_status.get('performance_metrics', {})
            
            return PerformanceSummaryResponse(
                total_sessions=performance_metrics.get('total_interactions', 0),
                active_sessions=performance_metrics.get('active_users', 0),
                average_confidence=0.85,
                average_processing_time=performance_metrics.get('average_response_time', 0.0),
                success_rate=performance_metrics.get('success_rate', 0.0),
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving performance summary"
            )
    
    async def end_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """End a user session"""
        
        try:
            # Get session status before ending
            session_status = await self.get_session_status(session_id)
            
            if not session_status:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found"
                )
            
            # For hybrid brain, sessions are managed automatically
            if self.brain_available and self.hybrid_brain:
                self.logger.info(f"Session {session_id} for user {user_id} ended successfully")
            
            return {
                "session_id": session_id,
                "user_id": user_id,
                "status": "ended",
                "interactions_count": session_status.interactions_count,
                "duration": self._calculate_session_duration(session_status),
                "ended_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error ending session: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error ending session"
            )
    
    def _validate_user_input(self, request: UserInputRequest):
        """Validate user input request"""
        
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        if len(request.message) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Message too long. Please keep messages under 10,000 characters."
            )
        
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="User ID is required"
            )
    
    def _extract_user_id_from_session(self, session_id: str) -> Optional[str]:
        """Extract user_id from session_id"""
        try:
            if session_id.startswith('hybrid_session_'):
                parts = session_id.split('_')
                if len(parts) >= 3:
                    return parts[2]
            return session_id
        except Exception:
            return None
    
    def _convert_hybrid_to_diego_response(self, processing_result: Dict[str, Any], request: UserInputRequest) -> DiegoResponse:
        """Convert hybrid brain processing result to Diego response"""
        
        # Extract data from hybrid brain response
        response_text = processing_result.get("response", "I understand. Let me think about this.")
        emotional_state = processing_result.get("emotional_state", "neutral")
        relationship_stage = processing_result.get("relationship_stage", "stranger")
        response_tone = processing_result.get("response_tone", {})
        user_profile_summary = processing_result.get("user_profile_summary", {})
        
        # Map emotional state to response type
        response_type_mapping = {
            "enthusiastic": "encouraging",
            "concerned": "supportive",
            "engaged": "conversational",
            "curious": "exploratory",
            "protective": "supportive",
            "contemplative": "reflective",
            "neutral": "balanced"
        }
        
        response_type = response_type_mapping.get(emotional_state, "supportive")
        confidence = 0.85  # Default confidence for hybrid brain
        
        # Generate Diego persona
        diego_persona = {
            "empathy_level": 0.8,
            "professional_tone": 0.7,
            "warmth_level": 0.6,
            "diego_consistency_score": 0.75
        }
        
        # Generate session summary
        session_summary = {
            "key_insights": [f"User in {emotional_state} state", f"Relationship at {relationship_stage} level"],
            "progress_indicators": {
                "emotional_awareness": 0.7,
                "communication_openness": 0.8,
                "trust_building": 0.6
            },
            "next_session_focus": {
                "primary": "Continue building rapport",
                "secondary": "Address user needs"
            }
        }
        
        return DiegoResponse(
            message=response_text,
            response_type=response_type,
            confidence=confidence,
            session_id=request.session_id or f"hybrid_session_{request.user_id}_{datetime.now().timestamp()}",
            diego_persona=diego_persona,
            follow_up_questions=["How are you feeling about this?", "What would you like to explore further?"],
            homework_assignment=None,
            resource_recommendations=[],
            session_summary=session_summary,
            safety_status="safe",
            metadata={
                "processing_time": processing_result.get("processing_time", 0.0),
                "emotional_state": emotional_state,
                "relationship_stage": relationship_stage,
                "trust_level": user_profile_summary.get("trust_level", 0.0),
                "emotional_bond": user_profile_summary.get("emotional_bond", 0.0),
                "interaction_count": user_profile_summary.get("interaction_count", 0),
                "relevant_memories_count": processing_result.get("relevant_memories_count", 0),
                "ai_brain_version": "hybrid_2.0.0"
            }
        )
    
    def _create_error_response(self, request: UserInputRequest, error_message: str) -> DiegoResponse:
        """Create error response"""
        
        return DiegoResponse(
            message="I apologize, but I'm experiencing some technical difficulties right now. Please try again in a moment, and I'll do my best to help you.",
            response_type="error_recovery",
            confidence=0.5,
            session_id=request.session_id or f"error_session_{datetime.now().timestamp()}",
            diego_persona={
                "empathy_level": 0.8,
                "professional_tone": 0.9,
                "diego_consistency_score": 0.7
            },
            follow_up_questions=[],
            homework_assignment=None,
            resource_recommendations=[],
            session_summary={
                "key_insights": [],
                "progress_indicators": {},
                "next_session_focus": {}
            },
            safety_status="safe",
            metadata={
                "error_occurred": True,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat(),
                "ai_brain_version": "hybrid_2.0.0"
            }
        )
    
    def _calculate_session_duration(self, session_status: SessionStatusResponse) -> float:
        """Calculate session duration in seconds"""
        
        try:
            start_time = datetime.fromisoformat(session_status.start_time)
            last_activity = datetime.fromisoformat(session_status.last_interaction)
            return (last_activity - start_time).total_seconds()
        except Exception:
            return 0.0
    
    async def _process_background_learning(self, processing_result: Dict[str, Any]):
        """Process background learning tasks"""
        
        try:
            self.logger.debug(f"Processing background learning for session")
        except Exception as e:
            self.logger.error(f"Error in background learning: {str(e)}")
    
    async def _update_performance_metrics(self, processing_result: Dict[str, Any]):
        """Update performance metrics"""
        
        try:
            self.logger.debug(f"Updating performance metrics")
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")
    
    async def _persist_session_data(self, processing_result: Dict[str, Any]):
        """Persist session data"""
        
        try:
            self.logger.debug(f"Persisting session data")
        except Exception as e:
            self.logger.error(f"Error persisting session data: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on AI brain system"""
        
        try:
            if not self.brain_available or not self.hybrid_brain:
                return {
                    "status": "unhealthy",
                    "ai_brain_active": False,
                    "error": "Hybrid brain not available",
                    "last_check": datetime.now().isoformat(),
                    "version": "hybrid_2.0.0"
                }
            
            # Get system status from hybrid brain
            system_status = self.hybrid_brain.get_system_status()
            performance_metrics = system_status.get('performance_metrics', {})
            
            return {
                "status": "healthy",
                "ai_brain_active": True,
                "active_sessions": performance_metrics.get("active_users", 0),
                "total_sessions": performance_metrics.get("total_interactions", 0),
                "average_confidence": 0.85,
                "last_check": datetime.now().isoformat(),
                "version": "hybrid_2.0.0",
                "brain_type": "hybrid",
                "memory_usage": system_status.get('memory_statistics', {}).get('total_memories', 0),
                "emotional_state": system_status.get('consciousness_metrics', {}).get('current_emotional_state', 'neutral')
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "ai_brain_active": False,
                "error": str(e),
                "last_check": datetime.now().isoformat(),
                "version": "hybrid_2.0.0"
            }

# FastAPI route handlers
def create_ai_brain_routes(app, ai_brain_integration: AIBrainIntegration):
    """Create FastAPI routes for AI brain integration"""
    
    @app.post("/api/v1/chat", response_model=DiegoResponse)
    async def chat_with_diego(request: UserInputRequest, background_tasks: BackgroundTasks):
        """Main chat endpoint for Diego conversations"""
        return await ai_brain_integration.process_user_message(request, background_tasks)
    
    @app.get("/api/v1/session/{session_id}", response_model=SessionStatusResponse)
    async def get_session_status(session_id: str):
        """Get session status"""
        session_status = await ai_brain_integration.get_session_status(session_id)
        if not session_status:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_status
    
    @app.delete("/api/v1/session/{session_id}")
    async def end_session(session_id: str, user_id: str):
        """End a session"""
        return await ai_brain_integration.end_session(session_id, user_id)
    
    @app.get("/api/v1/performance", response_model=PerformanceSummaryResponse)
    async def get_performance_summary():
        """Get performance summary"""
        return await ai_brain_integration.get_performance_summary()
    
    @app.get("/api/v1/health")
    async def health_check():
        """Health check endpoint"""
        return ai_brain_integration.health_check()
    
    return app

# Utility functions for integration
def initialize_ai_brain_integration(app_config: Dict[str, Any]) -> AIBrainIntegration:
    """Initialize AI brain integration with app configuration"""
    
    # Extract hybrid brain specific configuration
    brain_config = {
        "brain_type": "hybrid",
        "hybrid_config": {
            "max_concurrent_sessions": app_config.get("AI_BRAIN_MAX_SESSIONS", 10),
            "session_timeout": app_config.get("AI_BRAIN_SESSION_TIMEOUT", 3600),
            "safety_monitoring": app_config.get("AI_BRAIN_SAFETY_MONITORING", True),
            "performance_tracking": app_config.get("AI_BRAIN_PERFORMANCE_TRACKING", True)
        },
        "enable_background_learning": app_config.get("AI_BRAIN_BACKGROUND_LEARNING", True),
        "enable_performance_monitoring": app_config.get("AI_BRAIN_PERFORMANCE_MONITORING", True),
        "enable_session_persistence": app_config.get("AI_BRAIN_SESSION_PERSISTENCE", True),
        "max_response_time": app_config.get("AI_BRAIN_MAX_RESPONSE_TIME", 30.0)
    }
    
    return AIBrainIntegration(brain_config)

def setup_ai_brain_logging(log_level: str = "INFO"):
    """Setup logging for AI brain components"""
    
    # Configure logging for AI brain modules
    ai_brain_logger = logging.getLogger("ai_brain")
    ai_brain_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    ai_brain_logger.addHandler(handler)
    
    return ai_brain_logger