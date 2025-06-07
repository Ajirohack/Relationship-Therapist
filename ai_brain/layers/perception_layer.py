#!/usr/bin/env python3
"""
Perception Layer - Layer 1 of AI Brain Architecture
Handles input processing, sensory data interpretation, and initial context extraction
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import re
from dataclasses import dataclass

from ..core.brain_architecture import BrainLayer, LayerType, LayerInput, LayerOutput

logger = logging.getLogger(__name__)

class InputType:
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    STRUCTURED = "structured"
    MULTIMODAL = "multimodal"

class SentimentType:
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class PerceptionResult:
    """Result of perception processing"""
    input_type: str
    content: str
    sentiment: str
    emotional_indicators: List[str]
    key_topics: List[str]
    urgency_level: int  # 1-10
    context_clues: Dict[str, Any]
    metadata: Dict[str, Any]

class PerceptionLayer(BrainLayer):
    """Layer 1: Perception - Input processing and sensory interpretation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(LayerType.PERCEPTION, config)
        
        # Emotional indicators patterns
        self.emotional_patterns = {
            "anger": [r"\b(angry|mad|furious|rage|hate)\b", r"!!+", r"[A-Z]{3,}"],
            "sadness": [r"\b(sad|depressed|down|hurt|cry)\b", r"\b(miss|lost|alone)\b"],
            "joy": [r"\b(happy|joy|excited|love|amazing)\b", r"😊|😄|❤️|💕"],
            "fear": [r"\b(scared|afraid|worried|anxious|panic)\b"],
            "surprise": [r"\b(wow|amazing|shocked|unexpected)\b", r"\?{2,}"],
            "disgust": [r"\b(disgusting|gross|awful|terrible)\b"]
        }
        
        # Relationship topic patterns
        self.relationship_patterns = {
            "communication": [r"\b(talk|speak|listen|understand|communicate)\b"],
            "trust": [r"\b(trust|honest|lie|secret|betray)\b"],
            "intimacy": [r"\b(close|intimate|distance|connect|bond)\b"],
            "conflict": [r"\b(fight|argue|disagree|conflict|problem)\b"],
            "commitment": [r"\b(future|marry|together|forever|commitment)\b"],
            "family": [r"\b(family|children|kids|parents|relatives)\b"]
        }
        
        # Urgency indicators
        self.urgency_patterns = {
            "high": [r"\b(emergency|urgent|crisis|help|now)\b", r"!!+"],
            "medium": [r"\b(soon|important|need|should)\b"],
            "low": [r"\b(maybe|sometime|eventually|when)\b"]
        }
    
    async def process(self, input_data: LayerInput) -> LayerOutput:
        """Process input through perception layer"""
        try:
            self.logger.debug(f"Processing perception input: {input_data.layer_id}")
            
            # Extract raw data
            raw_data = input_data.data
            
            # Determine input type
            input_type = self._determine_input_type(raw_data)
            
            # Extract content based on type
            content = self._extract_content(raw_data, input_type)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(content)
            
            # Detect emotional indicators
            emotional_indicators = self._detect_emotions(content)
            
            # Extract key topics
            key_topics = self._extract_topics(content)
            
            # Assess urgency
            urgency_level = self._assess_urgency(content)
            
            # Extract context clues
            context_clues = self._extract_context_clues(raw_data, content)
            
            # Create perception result
            perception_result = PerceptionResult(
                input_type=input_type,
                content=content,
                sentiment=sentiment,
                emotional_indicators=emotional_indicators,
                key_topics=key_topics,
                urgency_level=urgency_level,
                context_clues=context_clues,
                metadata={
                    "processing_time": datetime.now().isoformat(),
                    "confidence": self._calculate_confidence(content),
                    "word_count": len(content.split()) if isinstance(content, str) else 0
                }
            )
            
            # Prepare output for next layers
            output_data = {
                "perception_result": perception_result.__dict__,
                "raw_input": raw_data,
                "processed_content": content,
                "analysis_metadata": {
                    "layer": "perception",
                    "timestamp": datetime.now().isoformat(),
                    "input_source": input_data.source_layer
                }
            }
            
            return LayerOutput(
                layer_id=self.layer_id,
                data=output_data,
                timestamp=datetime.now(),
                target_layers=["memory", "understanding_reasoning"],
                confidence=perception_result.metadata["confidence"],
                metadata={
                    "perception_summary": {
                        "type": input_type,
                        "sentiment": sentiment,
                        "urgency": urgency_level,
                        "topics": key_topics[:3]  # Top 3 topics
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in perception processing: {str(e)}")
            raise
    
    def _determine_input_type(self, raw_data: Dict[str, Any]) -> str:
        """Determine the type of input data"""
        if "message" in raw_data or "text" in raw_data:
            return InputType.TEXT
        elif "audio" in raw_data or "voice" in raw_data:
            return InputType.AUDIO
        elif "image" in raw_data or "photo" in raw_data:
            return InputType.IMAGE
        elif isinstance(raw_data, dict) and len(raw_data) > 1:
            return InputType.STRUCTURED
        else:
            return InputType.MULTIMODAL
    
    def _extract_content(self, raw_data: Dict[str, Any], input_type: str) -> str:
        """Extract content based on input type"""
        if input_type == InputType.TEXT:
            return raw_data.get("message", raw_data.get("text", ""))
        elif input_type == InputType.STRUCTURED:
            # Convert structured data to text representation
            return json.dumps(raw_data, indent=2)
        else:
            # For other types, return string representation
            return str(raw_data)
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of the content"""
        if not content:
            return SentimentType.NEUTRAL
        
        content_lower = content.lower()
        
        # Simple sentiment analysis based on keywords
        positive_words = ["good", "great", "love", "happy", "wonderful", "amazing", "perfect"]
        negative_words = ["bad", "hate", "angry", "sad", "terrible", "awful", "horrible"]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        elif positive_count > 0 and negative_count > 0:
            return SentimentType.MIXED
        else:
            return SentimentType.NEUTRAL
    
    def _detect_emotions(self, content: str) -> List[str]:
        """Detect emotional indicators in content"""
        detected_emotions = []
        
        for emotion, patterns in self.emotional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected_emotions.append(emotion)
                    break
        
        return detected_emotions
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract relationship-related topics"""
        detected_topics = []
        
        for topic, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected_topics.append(topic)
                    break
        
        return detected_topics
    
    def _assess_urgency(self, content: str) -> int:
        """Assess urgency level of the content"""
        urgency_score = 1  # Default low urgency
        
        for urgency, patterns in self.urgency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if urgency == "high":
                        urgency_score = max(urgency_score, 8)
                    elif urgency == "medium":
                        urgency_score = max(urgency_score, 5)
                    break
        
        # Additional urgency indicators
        if "!!!" in content:
            urgency_score = max(urgency_score, 9)
        elif "!!" in content:
            urgency_score = max(urgency_score, 7)
        elif "!" in content:
            urgency_score = max(urgency_score, 4)
        
        return min(urgency_score, 10)
    
    def _extract_context_clues(self, raw_data: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract contextual information"""
        context = {
            "platform": raw_data.get("platform", "unknown"),
            "timestamp": raw_data.get("timestamp", datetime.now().isoformat()),
            "user_id": raw_data.get("user_id", "unknown"),
            "session_context": raw_data.get("context", {})
        }
        
        # Extract time references
        time_patterns = {
            "past": [r"\b(yesterday|last|ago|before|was|were)\b"],
            "present": [r"\b(now|today|currently|am|is|are)\b"],
            "future": [r"\b(tomorrow|will|going to|plan|next)\b"]
        }
        
        for time_ref, patterns in time_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    context["time_reference"] = time_ref
                    break
        
        # Extract relationship context
        if any(word in content.lower() for word in ["partner", "boyfriend", "girlfriend", "husband", "wife"]):
            context["relationship_status"] = "in_relationship"
        elif any(word in content.lower() for word in ["single", "alone", "dating"]):
            context["relationship_status"] = "single"
        
        return context
    
    def _calculate_confidence(self, content: str) -> float:
        """Calculate confidence score for perception analysis"""
        if not content:
            return 0.1
        
        # Base confidence on content length and clarity
        word_count = len(content.split())
        
        if word_count < 3:
            return 0.3
        elif word_count < 10:
            return 0.6
        elif word_count < 50:
            return 0.8
        else:
            return 0.9