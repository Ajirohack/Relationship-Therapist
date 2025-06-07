#!/usr/bin/env python3
"""
AI Brain Architecture - 7-Layer Design Framework
Core architecture for the relationship therapist AI system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class LayerType(Enum):
    PERCEPTION = "perception"
    MEMORY = "memory"
    UNDERSTANDING_REASONING = "understanding_reasoning"
    EMOTIONAL_PSYCHOLOGICAL = "emotional_psychological"
    DECISION_ACTION = "decision_action"
    TOOLBOX_MOTOR = "toolbox_motor"
    SELFHOOD_AWARENESS = "selfhood_awareness"
    META = "meta"

class ProcessingState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class LayerInput:
    """Input data structure for brain layers"""
    layer_id: str
    data: Dict[str, Any]
    timestamp: datetime
    source_layer: Optional[str] = None
    priority: int = 1  # 1-10, 10 being highest
    metadata: Dict[str, Any] = None

@dataclass
class LayerOutput:
    """Output data structure from brain layers"""
    layer_id: str
    data: Dict[str, Any]
    timestamp: datetime
    target_layers: List[str]
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

@dataclass
class BrainState:
    """Current state of the AI brain"""
    session_id: str
    user_id: str
    current_stage: str  # APP, FPP, RPP
    trust_score: float
    openness_score: float
    emotional_state: Dict[str, float]
    conversation_context: List[Dict[str, Any]]
    active_goals: List[str]
    personality_profile: Dict[str, Any]
    last_updated: datetime

class BrainLayer(ABC):
    """Abstract base class for all brain layers"""
    
    def __init__(self, layer_type: LayerType, config: Dict[str, Any] = None):
        self.layer_type = layer_type
        self.layer_id = f"{layer_type.value}_{id(self)}"
        self.config = config or {}
        self.state = ProcessingState.IDLE
        self.input_queue: List[LayerInput] = []
        self.output_queue: List[LayerOutput] = []
        self.logger = logging.getLogger(f"brain.{layer_type.value}")
        
    @abstractmethod
    async def process(self, input_data: LayerInput) -> LayerOutput:
        """Process input data and return output"""
        pass
    
    async def receive_input(self, input_data: LayerInput):
        """Receive input from other layers"""
        self.input_queue.append(input_data)
        self.logger.debug(f"Received input from {input_data.source_layer}")
    
    async def send_output(self, output_data: LayerOutput):
        """Send output to target layers"""
        self.output_queue.append(output_data)
        self.logger.debug(f"Sending output to {output_data.target_layers}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current layer status"""
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type.value,
            "state": self.state.value,
            "input_queue_size": len(self.input_queue),
            "output_queue_size": len(self.output_queue)
        }

class AIBrainArchitecture:
    """Main AI Brain Architecture orchestrator"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.layers: Dict[LayerType, BrainLayer] = {}
        self.brain_state: Optional[BrainState] = None
        self.message_bus: Dict[str, List[LayerOutput]] = {}
        self.processing_pipeline: List[LayerType] = [
            LayerType.PERCEPTION,
            LayerType.MEMORY,
            LayerType.UNDERSTANDING_REASONING,
            LayerType.EMOTIONAL_PSYCHOLOGICAL,
            LayerType.DECISION_ACTION,
            LayerType.TOOLBOX_MOTOR,
            LayerType.SELFHOOD_AWARENESS
        ]
        self.meta_layer_enabled = self.config.get("enable_meta_layer", False)
        self.logger = logging.getLogger("brain.architecture")
        
    def register_layer(self, layer: BrainLayer):
        """Register a brain layer"""
        self.layers[layer.layer_type] = layer
        self.logger.info(f"Registered layer: {layer.layer_type.value}")
    
    def initialize_brain_state(self, session_id: str, user_id: str, 
                             initial_stage: str = "APP") -> BrainState:
        """Initialize brain state for a new session"""
        self.brain_state = BrainState(
            session_id=session_id,
            user_id=user_id,
            current_stage=initial_stage,
            trust_score=0.0,
            openness_score=0.0,
            emotional_state={"neutral": 1.0},
            conversation_context=[],
            active_goals=[],
            personality_profile={},
            last_updated=datetime.now()
        )
        return self.brain_state
    
    async def process_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the entire brain architecture"""
        if not self.brain_state:
            raise ValueError("Brain state not initialized")
        
        self.logger.info(f"Processing input for session {self.brain_state.session_id}")
        
        # Create initial input for perception layer
        perception_input = LayerInput(
            layer_id="external_input",
            data=raw_input,
            timestamp=datetime.now(),
            source_layer="external",
            metadata={"session_id": self.brain_state.session_id}
        )
        
        # Process through pipeline
        current_output = None
        for layer_type in self.processing_pipeline:
            if layer_type not in self.layers:
                self.logger.warning(f"Layer {layer_type.value} not registered, skipping")
                continue
            
            layer = self.layers[layer_type]
            
            # Use previous output as input, or initial input for first layer
            if current_output is None:
                layer_input = perception_input
            else:
                layer_input = LayerInput(
                    layer_id=current_output.layer_id,
                    data=current_output.data,
                    timestamp=datetime.now(),
                    source_layer=current_output.layer_id,
                    metadata=current_output.metadata
                )
            
            try:
                current_output = await layer.process(layer_input)
                self.logger.debug(f"Layer {layer_type.value} processed successfully")
            except Exception as e:
                self.logger.error(f"Error in layer {layer_type.value}: {str(e)}")
                raise
        
        # Process through meta layer if enabled
        if self.meta_layer_enabled and LayerType.META in self.layers:
            meta_layer = self.layers[LayerType.META]
            meta_input = LayerInput(
                layer_id=current_output.layer_id if current_output else "pipeline_output",
                data=current_output.data if current_output else {},
                timestamp=datetime.now(),
                source_layer="pipeline",
                metadata={"brain_state": asdict(self.brain_state)}
            )
            current_output = await meta_layer.process(meta_input)
        
        # Update brain state
        self.brain_state.last_updated = datetime.now()
        
        return current_output.data if current_output else {}
    
    def get_brain_status(self) -> Dict[str, Any]:
        """Get comprehensive brain status"""
        layer_statuses = {}
        for layer_type, layer in self.layers.items():
            layer_statuses[layer_type.value] = layer.get_status()
        
        return {
            "brain_state": asdict(self.brain_state) if self.brain_state else None,
            "layers": layer_statuses,
            "pipeline": [lt.value for lt in self.processing_pipeline],
            "meta_layer_enabled": self.meta_layer_enabled
        }
    
    async def shutdown(self):
        """Gracefully shutdown the brain architecture"""
        self.logger.info("Shutting down AI Brain Architecture")
        # Cleanup layers if needed
        for layer in self.layers.values():
            if hasattr(layer, 'cleanup'):
                await layer.cleanup()