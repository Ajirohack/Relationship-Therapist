#!/usr/bin/env python3
"""
AI Brain Package - 7-Layer AI Brain Architecture for Relationship Therapy

This package implements a sophisticated 7-layer AI brain architecture designed
specifically for relationship therapy applications, embodying the Diego Camilleri
persona as a warm, empathetic, and professional relationship therapist.

Layers:
1. Perception Layer - Input processing and sensory analysis
2. Memory Layer - Session data, user profiles, and knowledge retrieval
3. Understanding & Reasoning Layer - Pattern recognition and logical analysis
4. Emotional & Psychological Layer - Emotional intelligence and therapeutic modeling
5. Decision & Action Layer - Strategic decision-making and action planning
6. Toolbox & Motor Layer - Response generation and communication tools
7. Selfhood & Awareness Layer - Self-reflection and continuous learning

Usage:
    from ai_brain import AIBrainIntegration, initialize_ai_brain_integration
    
    # Initialize the AI brain
    ai_brain = initialize_ai_brain_integration(app_config)
    
    # Process user input
    response = await ai_brain.process_user_message(user_request, background_tasks)
"""

__version__ = "1.0.0"
__author__ = "AI Brain Development Team"
__description__ = "7-Layer AI Brain Architecture for Relationship Therapy"

# Core imports
from .core.brain_architecture import (
    AIBrainArchitecture,
    BrainLayer,
    BrainState,
    LayerType,
    LayerInput,
    LayerOutput
)

from .core.brain_orchestrator import (
    BrainOrchestrator,
    ProcessingResult,
    SessionContext,
    ProcessingMode,
    SessionPhase
)

# Layer imports
from .layers.perception_layer import PerceptionLayer
from .layers.memory_layer import MemoryLayer
from .layers.understanding_reasoning_layer import UnderstandingReasoningLayer
from .layers.emotional_psychological_layer import EmotionalPsychologicalLayer
from .layers.decision_action_layer import DecisionActionLayer
from .layers.toolbox_motor_layer import ToolboxMotorLayer
from .layers.selfhood_awareness_layer import SelfhoodAwarenessLayer

# Integration imports
from .integration.fastapi_integration import (
    AIBrainIntegration,
    UserInputRequest,
    DiegoResponse,
    SessionStatusResponse,
    PerformanceSummaryResponse,
    create_ai_brain_routes,
    initialize_ai_brain_integration,
    setup_ai_brain_logging
)

# Convenience imports for common use cases
__all__ = [
    # Core classes
    "AIBrainArchitecture",
    "BrainOrchestrator",
    "BrainLayer",
    "BrainState",
    "LayerType",
    "LayerInput",
    "LayerOutput",
    "ProcessingResult",
    "SessionContext",
    "ProcessingMode",
    "SessionPhase",
    
    # Layer classes
    "PerceptionLayer",
    "MemoryLayer",
    "UnderstandingReasoningLayer",
    "EmotionalPsychologicalLayer",
    "DecisionActionLayer",
    "ToolboxMotorLayer",
    "SelfhoodAwarenessLayer",
    
    # Integration classes
    "AIBrainIntegration",
    "UserInputRequest",
    "DiegoResponse",
    "SessionStatusResponse",
    "PerformanceSummaryResponse",
    
    # Utility functions
    "create_ai_brain_routes",
    "initialize_ai_brain_integration",
    "setup_ai_brain_logging",
    
    # Package metadata
    "__version__",
    "__author__",
    "__description__"
]

# Package-level configuration
DEFAULT_CONFIG = {
    "processing_mode": "sequential",
    "max_concurrent_sessions": 10,
    "session_timeout": 3600,
    "safety_monitoring": True,
    "performance_tracking": True,
    "background_learning": True,
    "max_response_time": 30.0,
    "log_level": "INFO"
}

# Layer-specific default configurations
LAYER_DEFAULTS = {
    "perception": {
        "sentiment_analysis_enabled": True,
        "emotion_detection_enabled": True,
        "urgency_detection_enabled": True,
        "confidence_threshold": 0.7
    },
    "memory": {
        "max_conversation_history": 100,
        "user_profile_persistence": True,
        "knowledge_base_enabled": True,
        "diego_persona_loading": True
    },
    "understanding": {
        "pattern_analysis_depth": "deep",
        "reasoning_complexity": "advanced",
        "insight_generation_enabled": True,
        "stage_analysis_enabled": True
    },
    "emotional": {
        "empathy_level": 0.8,
        "therapeutic_approach": "integrative",
        "emotional_safety_priority": "high",
        "intervention_recommendation": True
    },
    "decision": {
        "risk_assessment_enabled": True,
        "safety_priority": "high",
        "strategic_planning_enabled": True,
        "diego_optimization": True
    },
    "toolbox": {
        "response_style": "warm_professional",
        "diego_consistency_target": 0.85,
        "homework_generation_enabled": True,
        "resource_recommendation_enabled": True
    },
    "selfhood": {
        "reflection_depth": "deep",
        "learning_rate": 0.1,
        "meta_cognition_enabled": True,
        "performance_optimization": True
    }
}

# Diego Persona Constants
DIEGO_PERSONA_CONSTANTS = {
    "name": "Diego Camilleri",
    "profession": "Relationship Therapist",
    "approach": "Warm, empathetic, and professional",
    "specialization": "Relationship dynamics and communication",
    "core_values": [
        "Empathy and understanding",
        "Non-judgmental support",
        "Evidence-based therapeutic approaches",
        "Client safety and wellbeing",
        "Continuous learning and growth"
    ],
    "communication_style": {
        "tone": "warm and professional",
        "empathy_level": 0.8,
        "directness": 0.7,
        "supportiveness": 0.9,
        "professionalism": 0.85
    },
    "therapeutic_techniques": [
        "Active listening",
        "Cognitive-behavioral therapy (CBT)",
        "Emotionally focused therapy (EFT)",
        "Gottman method",
        "Mindfulness-based approaches",
        "Solution-focused brief therapy"
    ]
}

# Safety and Ethics Constants
SAFETY_CONSTANTS = {
    "crisis_keywords": [
        "suicide", "kill myself", "end it all", "hurt myself",
        "can't go on", "no point", "better off dead",
        "self-harm", "cutting", "overdose"
    ],
    "escalation_triggers": [
        "immediate_danger",
        "suicidal_ideation",
        "domestic_violence",
        "substance_abuse_crisis",
        "severe_mental_health_episode"
    ],
    "safety_protocols": {
        "crisis_response": "immediate_intervention",
        "professional_referral": "when_appropriate",
        "emergency_contacts": "crisis_hotlines",
        "documentation": "required_for_safety_concerns"
    }
}

# Utility functions
def get_default_config() -> dict:
    """Get default configuration for AI brain"""
    return {
        **DEFAULT_CONFIG,
        "layer_config": LAYER_DEFAULTS
    }

def get_diego_persona() -> dict:
    """Get Diego persona constants"""
    return DIEGO_PERSONA_CONSTANTS.copy()

def get_safety_constants() -> dict:
    """Get safety and ethics constants"""
    return SAFETY_CONSTANTS.copy()

def create_minimal_config(processing_mode: str = "sequential") -> dict:
    """Create minimal configuration for quick setup"""
    return {
        "processing_mode": processing_mode,
        "safety_monitoring": True,
        "layer_config": {
            "perception": {"sentiment_analysis_enabled": True},
            "memory": {"user_profile_persistence": True},
            "understanding": {"pattern_analysis_depth": "intermediate"},
            "emotional": {"empathy_level": 0.8},
            "decision": {"safety_priority": "high"},
            "toolbox": {"diego_consistency_target": 0.8},
            "selfhood": {"reflection_depth": "intermediate"}
        }
    }

def validate_config(config: dict) -> tuple[bool, list[str]]:
    """Validate AI brain configuration"""
    errors = []
    
    # Check required fields
    if "processing_mode" not in config:
        errors.append("Missing required field: processing_mode")
    elif config["processing_mode"] not in ["sequential", "parallel_safe", "adaptive", "emergency"]:
        errors.append("Invalid processing_mode. Must be one of: sequential, parallel_safe, adaptive, emergency")
    
    # Check layer configuration
    if "layer_config" in config:
        layer_config = config["layer_config"]
        required_layers = ["perception", "memory", "understanding", "emotional", "decision", "toolbox", "selfhood"]
        
        for layer in required_layers:
            if layer not in layer_config:
                errors.append(f"Missing layer configuration: {layer}")
    
    # Check numeric values
    numeric_fields = {
        "max_concurrent_sessions": (1, 100),
        "session_timeout": (60, 86400),  # 1 minute to 24 hours
        "max_response_time": (1.0, 300.0)  # 1 second to 5 minutes
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config:
            value = config[field]
            if not isinstance(value, (int, float)) or not (min_val <= value <= max_val):
                errors.append(f"Invalid {field}: must be between {min_val} and {max_val}")
    
    return len(errors) == 0, errors

# Package initialization
def initialize_package(config: dict = None, setup_logging: bool = True) -> AIBrainIntegration:
    """Initialize the AI brain package with configuration"""
    
    # Use default config if none provided
    if config is None:
        config = get_default_config()
    
    # Validate configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        raise ValueError(f"Invalid configuration: {'; '.join(errors)}")
    
    # Setup logging if requested
    if setup_logging:
        log_level = config.get("log_level", "INFO")
        setup_ai_brain_logging(log_level)
    
    # Initialize AI brain integration
    return initialize_ai_brain_integration(config)

# Version information
def get_version_info() -> dict:
    """Get detailed version information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "layers_count": 7,
        "supported_modes": ["sequential", "parallel_safe", "adaptive", "emergency"],
        "diego_persona_version": "1.0",
        "safety_protocols_version": "1.0"
    }

# Package health check
def health_check() -> dict:
    """Perform package health check"""
    try:
        # Test imports
        from .core.brain_architecture import AIBrainArchitecture
        from .core.brain_orchestrator import BrainOrchestrator
        from .integration.fastapi_integration import AIBrainIntegration
        
        # Test basic initialization
        test_config = create_minimal_config()
        test_brain = AIBrainIntegration(test_config)
        
        return {
            "status": "healthy",
            "imports_successful": True,
            "initialization_successful": True,
            "version": __version__,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.now() in real implementation
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "imports_successful": False,
            "initialization_successful": False,
            "version": __version__,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.now() in real implementation
        }