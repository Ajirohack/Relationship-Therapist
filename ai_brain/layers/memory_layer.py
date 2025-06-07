#!/usr/bin/env python3
"""
Memory Layer - Layer 2 of AI Brain Architecture
Handles session management, user profiles, conversation history, and knowledge retrieval
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from collections import deque

from ..core.brain_architecture import BrainLayer, LayerType, LayerInput, LayerOutput

logger = logging.getLogger(__name__)

class MemoryType:
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

@dataclass
class MemoryEntry:
    """Individual memory entry"""
    entry_id: str
    memory_type: str
    content: Dict[str, Any]
    timestamp: datetime
    importance: float  # 0.0 - 1.0
    access_count: int
    last_accessed: datetime
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: str
    personality_traits: Dict[str, float]
    communication_style: str
    attachment_style: str
    relationship_goals: List[str]
    therapy_preferences: Dict[str, Any]
    progress_metrics: Dict[str, float]
    behavioral_patterns: Dict[str, Any]
    emotional_patterns: Dict[str, Any]
    session_history: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime

@dataclass
class ConversationContext:
    """Current conversation context"""
    session_id: str
    user_id: str
    current_stage: str  # APP, FPP, RPP
    conversation_history: List[Dict[str, Any]]
    active_topics: List[str]
    emotional_trajectory: List[Dict[str, Any]]
    trust_progression: List[float]
    openness_progression: List[float]
    key_insights: List[str]
    unresolved_issues: List[str]
    session_goals: List[str]
    started_at: datetime
    last_activity: datetime

class MemoryLayer(BrainLayer):
    """Layer 2: Memory - Session management and knowledge storage"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(LayerType.MEMORY, config)
        
        # Memory storage
        self.short_term_memory: deque = deque(maxlen=config.get("short_term_limit", 50))
        self.long_term_memory: Dict[str, MemoryEntry] = {}
        self.working_memory: Dict[str, Any] = {}
        
        # User profiles
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Conversation contexts
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        # Knowledge base integration
        self.knowledge_base = None  # Will be injected
        
        # Memory management settings
        self.max_long_term_entries = config.get("max_long_term_entries", 10000)
        self.importance_threshold = config.get("importance_threshold", 0.3)
        self.cleanup_interval = config.get("cleanup_interval", 3600)  # seconds
        
        # Diego Camilleri persona integration
        self.diego_persona = self._load_diego_persona()
    
    async def process(self, input_data: LayerInput) -> LayerOutput:
        """Process input through memory layer"""
        try:
            self.logger.debug(f"Processing memory input: {input_data.layer_id}")
            
            # Extract data from previous layer
            perception_result = input_data.data.get("perception_result", {})
            raw_input = input_data.data.get("raw_input", {})
            
            # Get or create user profile
            user_id = raw_input.get("user_id", "unknown")
            user_profile = await self._get_or_create_user_profile(user_id)
            
            # Get or create conversation context
            session_id = raw_input.get("session_id", f"session_{user_id}_{datetime.now().timestamp()}")
            conversation_context = await self._get_or_create_conversation_context(session_id, user_id)
            
            # Store perception result in short-term memory
            await self._store_short_term_memory(perception_result, session_id)
            
            # Update conversation context
            await self._update_conversation_context(conversation_context, perception_result, raw_input)
            
            # Retrieve relevant memories
            relevant_memories = await self._retrieve_relevant_memories(perception_result, user_id)
            
            # Retrieve relevant knowledge
            relevant_knowledge = await self._retrieve_relevant_knowledge(perception_result)
            
            # Update user profile based on new information
            await self._update_user_profile(user_profile, perception_result, conversation_context)
            
            # Determine if memories should be consolidated to long-term
            await self._consolidate_memories(session_id)
            
            # Prepare output data
            output_data = {
                "user_profile": asdict(user_profile),
                "conversation_context": asdict(conversation_context),
                "relevant_memories": relevant_memories,
                "relevant_knowledge": relevant_knowledge,
                "diego_persona": self.diego_persona,
                "perception_result": perception_result,
                "raw_input": raw_input,
                "memory_metadata": {
                    "layer": "memory",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "user_id": user_id,
                    "short_term_count": len(self.short_term_memory),
                    "long_term_count": len(self.long_term_memory)
                }
            }
            
            return LayerOutput(
                layer_id=self.layer_id,
                data=output_data,
                timestamp=datetime.now(),
                target_layers=["understanding_reasoning", "emotional_psychological"],
                confidence=0.9,
                metadata={
                    "memory_summary": {
                        "user_stage": conversation_context.current_stage,
                        "session_length": len(conversation_context.conversation_history),
                        "trust_score": conversation_context.trust_progression[-1] if conversation_context.trust_progression else 0.0,
                        "openness_score": conversation_context.openness_progression[-1] if conversation_context.openness_progression else 0.0
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in memory processing: {str(e)}")
            raise
    
    async def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # Create new user profile
        new_profile = UserProfile(
            user_id=user_id,
            personality_traits={
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            },
            communication_style="unknown",
            attachment_style="unknown",
            relationship_goals=[],
            therapy_preferences={},
            progress_metrics={
                "trust_building": 0.0,
                "communication_skills": 0.0,
                "emotional_awareness": 0.0,
                "conflict_resolution": 0.0
            },
            behavioral_patterns={},
            emotional_patterns={},
            session_history=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.user_profiles[user_id] = new_profile
        return new_profile
    
    async def _get_or_create_conversation_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Get existing conversation context or create new one"""
        if session_id in self.conversation_contexts:
            return self.conversation_contexts[session_id]
        
        # Create new conversation context
        new_context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            current_stage="APP",  # Start with Attraction Phase
            conversation_history=[],
            active_topics=[],
            emotional_trajectory=[],
            trust_progression=[0.0],
            openness_progression=[0.0],
            key_insights=[],
            unresolved_issues=[],
            session_goals=[],
            started_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.conversation_contexts[session_id] = new_context
        return new_context
    
    async def _store_short_term_memory(self, perception_result: Dict[str, Any], session_id: str):
        """Store perception result in short-term memory"""
        memory_entry = MemoryEntry(
            entry_id=f"stm_{datetime.now().timestamp()}",
            memory_type=MemoryType.SHORT_TERM,
            content=perception_result,
            timestamp=datetime.now(),
            importance=self._calculate_importance(perception_result),
            access_count=0,
            last_accessed=datetime.now(),
            tags=perception_result.get("key_topics", []),
            metadata={"session_id": session_id}
        )
        
        self.short_term_memory.append(memory_entry)
    
    async def _update_conversation_context(self, context: ConversationContext, 
                                         perception_result: Dict[str, Any], 
                                         raw_input: Dict[str, Any]):
        """Update conversation context with new information"""
        # Add to conversation history
        context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "content": perception_result.get("content", ""),
            "sentiment": perception_result.get("sentiment", "neutral"),
            "emotions": perception_result.get("emotional_indicators", []),
            "topics": perception_result.get("key_topics", []),
            "urgency": perception_result.get("urgency_level", 1)
        })
        
        # Update active topics
        new_topics = perception_result.get("key_topics", [])
        for topic in new_topics:
            if topic not in context.active_topics:
                context.active_topics.append(topic)
        
        # Update emotional trajectory
        context.emotional_trajectory.append({
            "timestamp": datetime.now().isoformat(),
            "emotions": perception_result.get("emotional_indicators", []),
            "sentiment": perception_result.get("sentiment", "neutral")
        })
        
        # Update trust and openness scores (simplified calculation)
        current_trust = context.trust_progression[-1] if context.trust_progression else 0.0
        current_openness = context.openness_progression[-1] if context.openness_progression else 0.0
        
        # Adjust based on sentiment and topics
        trust_adjustment = self._calculate_trust_adjustment(perception_result)
        openness_adjustment = self._calculate_openness_adjustment(perception_result)
        
        new_trust = max(0.0, min(100.0, current_trust + trust_adjustment))
        new_openness = max(0.0, min(100.0, current_openness + openness_adjustment))
        
        context.trust_progression.append(new_trust)
        context.openness_progression.append(new_openness)
        
        context.last_activity = datetime.now()
    
    async def _retrieve_relevant_memories(self, perception_result: Dict[str, Any], user_id: str) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to current input"""
        relevant_memories = []
        
        # Get topics from perception result
        current_topics = perception_result.get("key_topics", [])
        
        # Search through long-term memory
        for memory in self.long_term_memory.values():
            if memory.metadata.get("user_id") == user_id:
                # Check for topic overlap
                memory_topics = memory.tags
                if any(topic in memory_topics for topic in current_topics):
                    relevant_memories.append({
                        "content": memory.content,
                        "timestamp": memory.timestamp.isoformat(),
                        "importance": memory.importance,
                        "tags": memory.tags
                    })
        
        # Sort by importance and recency
        relevant_memories.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
        
        return relevant_memories[:5]  # Return top 5 relevant memories
    
    async def _retrieve_relevant_knowledge(self, perception_result: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant knowledge from knowledge base"""
        # This would integrate with the existing knowledge base
        # For now, return basic knowledge structure
        topics = perception_result.get("key_topics", [])
        
        relevant_knowledge = {
            "diego_guidance": self._get_diego_guidance_for_topics(topics),
            "therapy_techniques": self._get_therapy_techniques_for_topics(topics),
            "stage_specific_advice": self._get_stage_specific_advice(topics)
        }
        
        return relevant_knowledge
    
    async def _update_user_profile(self, profile: UserProfile, 
                                 perception_result: Dict[str, Any], 
                                 context: ConversationContext):
        """Update user profile based on new information"""
        # Update communication style based on patterns
        content = perception_result.get("content", "")
        if len(content.split()) > 50:
            profile.communication_style = "verbose"
        elif len(content.split()) < 10:
            profile.communication_style = "concise"
        else:
            profile.communication_style = "moderate"
        
        # Update emotional patterns
        emotions = perception_result.get("emotional_indicators", [])
        for emotion in emotions:
            if emotion in profile.emotional_patterns:
                profile.emotional_patterns[emotion] += 1
            else:
                profile.emotional_patterns[emotion] = 1
        
        # Update progress metrics based on conversation
        if "trust" in perception_result.get("key_topics", []):
            profile.progress_metrics["trust_building"] += 0.1
        if "communication" in perception_result.get("key_topics", []):
            profile.progress_metrics["communication_skills"] += 0.1
        
        profile.last_updated = datetime.now()
    
    async def _consolidate_memories(self, session_id: str):
        """Consolidate important short-term memories to long-term"""
        for memory in list(self.short_term_memory):
            if (memory.importance > self.importance_threshold and 
                memory.metadata.get("session_id") == session_id):
                
                # Move to long-term memory
                self.long_term_memory[memory.entry_id] = memory
                memory.memory_type = MemoryType.LONG_TERM
    
    def _calculate_importance(self, perception_result: Dict[str, Any]) -> float:
        """Calculate importance score for memory entry"""
        importance = 0.0
        
        # Base importance on urgency
        urgency = perception_result.get("urgency_level", 1)
        importance += urgency / 10.0
        
        # Increase importance for emotional content
        emotions = perception_result.get("emotional_indicators", [])
        importance += len(emotions) * 0.1
        
        # Increase importance for relationship topics
        topics = perception_result.get("key_topics", [])
        important_topics = ["trust", "communication", "conflict", "intimacy"]
        for topic in topics:
            if topic in important_topics:
                importance += 0.2
        
        return min(1.0, importance)
    
    def _calculate_trust_adjustment(self, perception_result: Dict[str, Any]) -> float:
        """Calculate trust score adjustment"""
        adjustment = 0.0
        
        sentiment = perception_result.get("sentiment", "neutral")
        if sentiment == "positive":
            adjustment += 2.0
        elif sentiment == "negative":
            adjustment -= 1.0
        
        topics = perception_result.get("key_topics", [])
        if "trust" in topics:
            adjustment += 1.0
        if "conflict" in topics:
            adjustment -= 0.5
        
        return adjustment
    
    def _calculate_openness_adjustment(self, perception_result: Dict[str, Any]) -> float:
        """Calculate openness score adjustment"""
        adjustment = 0.0
        
        # Longer messages indicate more openness
        content = perception_result.get("content", "")
        word_count = len(content.split())
        if word_count > 30:
            adjustment += 1.5
        elif word_count > 15:
            adjustment += 1.0
        
        # Emotional sharing indicates openness
        emotions = perception_result.get("emotional_indicators", [])
        adjustment += len(emotions) * 0.5
        
        return adjustment
    
    def _load_diego_persona(self) -> Dict[str, Any]:
        """Load Diego Camilleri persona information"""
        return {
            "name": "Diego Camilleri",
            "role": "Global Diplomat and Security Consultant",
            "background": "Seasoned diplomat with over three decades of experience",
            "personality": {
                "empathetic": True,
                "wise": True,
                "patient": True,
                "understanding": True
            },
            "approach": "humanistic, prioritizing empathy and sustainable solutions",
            "philosophy": "believes in the power of dialogue and cultural understanding",
            "current_situation": "approaching retirement, focusing on relationship guidance"
        }
    
    def _get_diego_guidance_for_topics(self, topics: List[str]) -> Dict[str, str]:
        """Get Diego's guidance for specific topics"""
        guidance = {}
        
        topic_guidance = {
            "trust": "Trust is like a gemstone - it takes time to form but can shatter in an instant. Build it carefully, one honest conversation at a time.",
            "communication": "In my years of diplomacy, I've learned that listening is more powerful than speaking. Hear not just words, but the emotions behind them.",
            "conflict": "Conflict is not the enemy of relationships - it's the opportunity for deeper understanding. Approach it with curiosity, not defensiveness.",
            "intimacy": "True intimacy comes from vulnerability. Share your authentic self, and create space for your partner to do the same."
        }
        
        for topic in topics:
            if topic in topic_guidance:
                guidance[topic] = topic_guidance[topic]
        
        return guidance
    
    def _get_therapy_techniques_for_topics(self, topics: List[str]) -> List[str]:
        """Get relevant therapy techniques for topics"""
        techniques = []
        
        topic_techniques = {
            "communication": ["Active Listening", "I-Statements", "Reflective Listening"],
            "trust": ["Trust Building Exercises", "Transparency Practice", "Consistency Building"],
            "conflict": ["Conflict Resolution", "De-escalation Techniques", "Fair Fighting Rules"],
            "intimacy": ["Emotional Intimacy Building", "Vulnerability Exercises", "Connection Rituals"]
        }
        
        for topic in topics:
            if topic in topic_techniques:
                techniques.extend(topic_techniques[topic])
        
        return list(set(techniques))  # Remove duplicates
    
    def _get_stage_specific_advice(self, topics: List[str]) -> Dict[str, str]:
        """Get advice specific to current relationship stage"""
        # This would be enhanced with actual stage detection
        return {
            "APP": "Focus on building initial connection and trust",
            "FPP": "Deepen understanding and emotional intimacy",
            "RPP": "Work on long-term commitment and future planning"
        }