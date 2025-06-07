"""Hybrid AI Brain Implementation
Advanced emotional intelligence with practical autonomy
Integrates with the existing 7-layer AI brain architecture
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from abc import ABC, abstractmethod
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ===============================
# CORE DATA STRUCTURES
# ===============================

class EmotionalState(Enum):
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    ENGAGED = "engaged"
    CONCERNED = "concerned"
    ENTHUSIASTIC = "enthusiastic"
    FRUSTRATED = "frustrated"
    PROTECTIVE = "protective"
    CONTEMPLATIVE = "contemplative"

class RelationshipStage(Enum):
    STRANGER = "stranger"          # APP - Automated Polite Processing
    ACQUAINTANCE = "acquaintance"  # FPP - Formal Professional Processing  
    TRUSTED = "trusted"            # RPP - Relaxed Personal Processing
    INTIMATE = "intimate"          # Deep personal connection

class MemoryType(Enum):
    EPISODIC = "episodic"      # Specific events and interactions
    SEMANTIC = "semantic"      # Facts and general knowledge
    PROCEDURAL = "procedural"  # How to do things
    EMOTIONAL = "emotional"    # Emotional associations and patterns

@dataclass
class HybridMemory:
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    emotional_valence: float  # -1.0 to 1.0
    importance: float        # 0.0 to 1.0
    user_id: Optional[str] = None
    tags: List[str] = None
    associations: List[str] = None  # IDs of related memories

@dataclass
class HybridUserProfile:
    user_id: str
    name: str
    relationship_stage: RelationshipStage
    trust_level: float  # 0.0 to 1.0
    emotional_bond: float  # 0.0 to 1.0
    interaction_count: int
    last_interaction: datetime
    preferences: Dict[str, Any]
    communication_style: Dict[str, float]  # formal, casual, technical, emotional
    personality_model: Dict[str, float]    # Big Five traits

# ===============================
# HYBRID PERCEPTION LAYER
# ===============================

class HybridPerceptionLayer:
    """Enhanced perception with emotional intelligence"""

    def __init__(self):
        self.input_processors = {
            'text': self._process_text,
            'voice': self._process_voice,
            'image': self._process_image,
            'structured_data': self._process_structured_data
        }
        self.context_buffer = []
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        input_type = input_data.get('type', 'text')
        processor = self.input_processors.get(input_type, self._process_text)
        
        processed = processor(input_data)
        self.context_buffer.append(processed)
        
        # Keep only recent context
        if len(self.context_buffer) > 50:
            self.context_buffer = self.context_buffer[-50:]
            
        return processed
    
    def _process_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        text = data.get('content', '')
        return {
            'type': 'text',
            'content': text,
            'word_count': len(text.split()),
            'sentiment': self._analyze_sentiment(text),
            'intent': self._detect_intent(text),
            'entities': self._extract_entities(text),
            'urgency': self._detect_urgency(text),
            'emotional_indicators': self._detect_emotional_indicators(text),
            'relationship_cues': self._detect_relationship_cues(text),
            'timestamp': datetime.now()
        }
    
    def _analyze_sentiment(self, text: str) -> float:
        # Enhanced sentiment analysis
        positive_words = ['good', 'great', 'awesome', 'love', 'like', 'happy', 'excellent', 
                         'wonderful', 'amazing', 'fantastic', 'brilliant', 'perfect']
        negative_words = ['bad', 'terrible', 'hate', 'dislike', 'sad', 'awful', 'frustrated',
                         'horrible', 'disgusting', 'annoying', 'disappointing', 'worried']
        
        words = text.lower().split()
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        if pos_count + neg_count == 0:
            return 0.0
        return (pos_count - neg_count) / len(words)
    
    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(word in text_lower for word in ['help', 'can you', 'please', 'assist']):
            return 'request_help'
        elif any(word in text_lower for word in ['schedule', 'calendar', 'meeting', 'appointment']):
            return 'scheduling'
        elif any(word in text_lower for word in ['remember', 'note', 'save', 'store']):
            return 'memory_storage'
        elif any(word in text_lower for word in ['feel', 'emotion', 'mood', 'upset', 'happy']):
            return 'emotional_expression'
        elif '?' in text:
            return 'question'
        else:
            return 'conversation'
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        entities = []
        words = text.split()
        
        for i, word in enumerate(words):
            if word.startswith('@'):
                entities.append({'type': 'person', 'value': word[1:]})
            elif word.startswith('#'):
                entities.append({'type': 'topic', 'value': word[1:]})
        
        return entities
    
    def _detect_urgency(self, text: str) -> float:
        urgent_indicators = ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'now', 
                           'quickly', 'rush', 'deadline', 'important']
        urgency_score = sum(1 for indicator in urgent_indicators if indicator in text.lower())
        return min(urgency_score / 3.0, 1.0)
    
    def _detect_emotional_indicators(self, text: str) -> Dict[str, float]:
        """Detect emotional indicators in text"""
        emotions = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful'],
            'sadness': ['sad', 'depressed', 'down', 'blue', 'melancholy'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished'],
            'trust': ['trust', 'confident', 'secure', 'comfortable']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, words in emotions.items():
            score = sum(1 for word in words if word in text_lower)
            emotion_scores[emotion] = min(score / 3.0, 1.0)
        
        return emotion_scores
    
    def _detect_relationship_cues(self, text: str) -> Dict[str, Any]:
        """Detect cues about relationship dynamics"""
        text_lower = text.lower()
        
        intimacy_indicators = ['personal', 'private', 'secret', 'close', 'friend']
        formality_indicators = ['sir', 'madam', 'please', 'thank you', 'excuse me']
        casual_indicators = ['hey', 'hi', 'yeah', 'cool', 'awesome']
        
        return {
            'intimacy_level': sum(1 for word in intimacy_indicators if word in text_lower),
            'formality_level': sum(1 for word in formality_indicators if word in text_lower),
            'casualness_level': sum(1 for word in casual_indicators if word in text_lower)
        }
    
    def _process_voice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Enhanced voice processing with emotional tone detection
        base_result = self._process_text(data)
        base_result.update({
            'voice_tone': data.get('tone', 'neutral'),
            'speaking_rate': data.get('rate', 'normal'),
            'volume': data.get('volume', 'normal')
        })
        return base_result
    
    def _process_image(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'image',
            'description': data.get('description', 'Image uploaded'),
            'emotional_content': data.get('emotional_content', 'neutral'),
            'timestamp': datetime.now()
        }
    
    def _process_structured_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'structured_data',
            'format': data.get('format', 'unknown'),
            'content': data.get('content', {}),
            'timestamp': datetime.now()
        }

# ===============================
# HYBRID MEMORY SYSTEM
# ===============================

class HybridMemorySystem:
    """Enhanced memory system with emotional continuity"""

    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = {}
        self.user_profiles = {}
        self.memory_associations = {}
        self.consolidation_threshold = 10
        self.emotional_memory_index = {}  # Index memories by emotional content
    
    def store_memory(self, memory: HybridMemory) -> str:
        """Store a new memory with emotional indexing"""
        if not memory.id:
            memory.id = str(uuid.uuid4())
        
        # Add to short-term memory first
        self.short_term_memory.append(memory)
        
        # Index by emotional content
        self._index_emotional_memory(memory)
        
        # Check if consolidation is needed
        if len(self.short_term_memory) >= self.consolidation_threshold:
            self._consolidate_memories()
        
        return memory.id
    
    def _index_emotional_memory(self, memory: HybridMemory):
        """Index memory by emotional valence for quick retrieval"""
        valence_bucket = self._get_valence_bucket(memory.emotional_valence)
        
        if valence_bucket not in self.emotional_memory_index:
            self.emotional_memory_index[valence_bucket] = []
        
        self.emotional_memory_index[valence_bucket].append(memory.id)
    
    def _get_valence_bucket(self, valence: float) -> str:
        """Categorize emotional valence into buckets"""
        if valence > 0.5:
            return 'very_positive'
        elif valence > 0.1:
            return 'positive'
        elif valence > -0.1:
            return 'neutral'
        elif valence > -0.5:
            return 'negative'
        else:
            return 'very_negative'
    
    def retrieve_memories(self, query: str, user_id: str = None, 
                         memory_type: MemoryType = None, 
                         emotional_filter: str = None,
                         limit: int = 10) -> List[HybridMemory]:
        """Enhanced memory retrieval with emotional filtering"""
        all_memories = list(self.long_term_memory.values()) + self.short_term_memory
        
        # Filter by user_id if specified
        if user_id:
            all_memories = [m for m in all_memories if m.user_id == user_id]
        
        # Filter by memory type if specified
        if memory_type:
            all_memories = [m for m in all_memories if m.memory_type == memory_type]
        
        # Filter by emotional content if specified
        if emotional_filter:
            emotion_memory_ids = self.emotional_memory_index.get(emotional_filter, [])
            all_memories = [m for m in all_memories if m.id in emotion_memory_ids]
        
        # Enhanced relevance scoring
        scored_memories = []
        query_words = set(query.lower().split())
        
        for memory in all_memories:
            content_words = set(memory.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            
            # Base relevance score
            relevance = overlap / max(len(query_words), 1) * memory.importance
            
            # Boost recent memories
            time_factor = self._calculate_recency_boost(memory.timestamp)
            relevance *= time_factor
            
            # Boost emotionally significant memories
            emotional_boost = abs(memory.emotional_valence) * 0.2
            relevance += emotional_boost
            
            scored_memories.append((relevance, memory))
        
        # Sort by relevance and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:limit]]
    
    def _calculate_recency_boost(self, timestamp: datetime) -> float:
        """Calculate boost factor based on memory recency"""
        time_diff = datetime.now() - timestamp
        days_ago = time_diff.days
        
        if days_ago == 0:
            return 1.2
        elif days_ago <= 7:
            return 1.1
        elif days_ago <= 30:
            return 1.0
        else:
            return 0.9
    
    def get_user_profile(self, user_id: str) -> HybridUserProfile:
        """Get or create enhanced user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = HybridUserProfile(
                user_id=user_id,
                name=f"User_{user_id[:8]}",
                relationship_stage=RelationshipStage.STRANGER,
                trust_level=0.1,
                emotional_bond=0.0,
                interaction_count=0,
                last_interaction=datetime.now(),
                preferences={},
                communication_style={
                    'formal': 0.8, 'casual': 0.2, 
                    'technical': 0.5, 'emotional': 0.3
                },
                personality_model={
                    'openness': 0.5, 'conscientiousness': 0.5, 
                    'extraversion': 0.5, 'agreeableness': 0.5, 
                    'neuroticism': 0.5
                }
            )
        return self.user_profiles[user_id]
    
    def update_user_relationship(self, user_id: str, interaction_data: Dict[str, Any]):
        """Enhanced relationship updating with emotional intelligence"""
        profile = self.get_user_profile(user_id)
        profile.interaction_count += 1
        profile.last_interaction = datetime.now()
        
        # Update trust and bond based on interaction quality
        sentiment = interaction_data.get('sentiment', 0.0)
        emotional_indicators = interaction_data.get('emotional_indicators', {})
        
        # Trust building factors
        if sentiment > 0:
            profile.trust_level = min(1.0, profile.trust_level + 0.01)
            profile.emotional_bond = min(1.0, profile.emotional_bond + 0.005)
        
        # Emotional bond building
        trust_emotion = emotional_indicators.get('trust', 0.0)
        if trust_emotion > 0:
            profile.emotional_bond = min(1.0, profile.emotional_bond + trust_emotion * 0.02)
        
        # Update communication style based on relationship cues
        relationship_cues = interaction_data.get('relationship_cues', {})
        if relationship_cues:
            self._update_communication_style(profile, relationship_cues)
        
        # Update relationship stage
        self._update_relationship_stage(profile)
    
    def _update_communication_style(self, profile: HybridUserProfile, cues: Dict[str, Any]):
        """Update communication style based on user cues"""
        formality = cues.get('formality_level', 0)
        casualness = cues.get('casualness_level', 0)
        intimacy = cues.get('intimacy_level', 0)
        
        # Adjust communication style gradually
        if formality > casualness:
            profile.communication_style['formal'] = min(1.0, profile.communication_style['formal'] + 0.05)
            profile.communication_style['casual'] = max(0.0, profile.communication_style['casual'] - 0.05)
        elif casualness > formality:
            profile.communication_style['casual'] = min(1.0, profile.communication_style['casual'] + 0.05)
            profile.communication_style['formal'] = max(0.0, profile.communication_style['formal'] - 0.05)
        
        if intimacy > 0:
            profile.communication_style['emotional'] = min(1.0, profile.communication_style['emotional'] + 0.03)
    
    def _update_relationship_stage(self, profile: HybridUserProfile):
        """Update relationship stage based on multiple factors"""
        # Calculate relationship progression score
        trust_factor = profile.trust_level
        interaction_factor = min(profile.interaction_count / 100.0, 1.0)
        emotional_factor = profile.emotional_bond
        time_factor = self._calculate_time_relationship_factor(profile.last_interaction)
        
        relationship_score = (
            trust_factor * 0.4 + 
            interaction_factor * 0.3 + 
            emotional_factor * 0.2 + 
            time_factor * 0.1
        )
        
        # Update stage based on score
        if relationship_score > 0.8 and profile.interaction_count > 50:
            profile.relationship_stage = RelationshipStage.INTIMATE
        elif relationship_score > 0.6 and profile.interaction_count > 20:
            profile.relationship_stage = RelationshipStage.TRUSTED
        elif relationship_score > 0.2 and profile.interaction_count > 5:
            profile.relationship_stage = RelationshipStage.ACQUAINTANCE
        else:
            profile.relationship_stage = RelationshipStage.STRANGER
    
    def _calculate_time_relationship_factor(self, last_interaction: datetime) -> float:
        """Calculate how recent interaction affects relationship"""
        time_diff = datetime.now() - last_interaction
        days_ago = time_diff.days
        
        if days_ago == 0:
            return 1.0
        elif days_ago <= 7:
            return 0.8
        elif days_ago <= 30:
            return 0.5
        else:
            return 0.2

# ===============================
# HYBRID RELATIONSHIP ENGINE
# ===============================

class HybridRelationshipEngine:
    """Advanced emotional intelligence and relationship management"""

    def __init__(self, memory_system: HybridMemorySystem):
        self.memory_system = memory_system
        self.current_emotional_state = EmotionalState.NEUTRAL
        self.emotion_history = []
        self.trust_factors = {
            'consistency': 0.0,
            'helpfulness': 0.0,
            'honesty': 0.0,
            'understanding': 0.0
        }
        self.emotional_intelligence_model = self._initialize_ei_model()
    
    def _initialize_ei_model(self) -> Dict[str, Any]:
        """Initialize emotional intelligence model"""
        return {
            'self_awareness': 0.8,
            'self_regulation': 0.7,
            'motivation': 0.9,
            'empathy': 0.8,
            'social_skills': 0.7,
            'emotional_adaptability': 0.6
        }
    
    def evaluate_relationship_stage(self, user_id: str, interaction_context: Dict[str, Any]) -> RelationshipStage:
        """Enhanced relationship stage evaluation"""
        profile = self.memory_system.get_user_profile(user_id)
        
        # Multi-factor analysis
        trust_score = profile.trust_level
        interaction_depth = min(profile.interaction_count / 100.0, 1.0)
        emotional_connection = profile.emotional_bond
        time_factor = self._calculate_time_factor(profile.last_interaction)
        
        # Consider current interaction context
        context_intimacy = self._assess_context_intimacy(interaction_context)
        
        # Weighted combination with context
        relationship_score = (
            trust_score * 0.35 + 
            interaction_depth * 0.25 + 
            emotional_connection * 0.25 + 
            time_factor * 0.1 +
            context_intimacy * 0.05
        )
        
        # Determine stage with hysteresis (prevent rapid stage changes)
        current_stage = profile.relationship_stage
        new_stage = self._determine_stage_from_score(relationship_score, profile.interaction_count)
        
        # Apply hysteresis
        if self._should_change_stage(current_stage, new_stage, relationship_score):
            return new_stage
        else:
            return current_stage
    
    def _assess_context_intimacy(self, context: Dict[str, Any]) -> float:
        """Assess intimacy level of current interaction context"""
        emotional_indicators = context.get('emotional_indicators', {})
        relationship_cues = context.get('relationship_cues', {})
        
        intimacy_score = 0.0
        
        # Emotional openness indicators
        for emotion, score in emotional_indicators.items():
            if emotion in ['trust', 'joy'] and score > 0.5:
                intimacy_score += 0.2
        
        # Relationship cues
        intimacy_level = relationship_cues.get('intimacy_level', 0)
        intimacy_score += min(intimacy_level / 5.0, 0.3)
        
        return min(intimacy_score, 1.0)
    
    def _determine_stage_from_score(self, score: float, interaction_count: int) -> RelationshipStage:
        """Determine relationship stage from score and interaction count"""
        if score > 0.8 and interaction_count > 50:
            return RelationshipStage.INTIMATE
        elif score > 0.6 and interaction_count > 20:
            return RelationshipStage.TRUSTED
        elif score > 0.2 and interaction_count > 5:
            return RelationshipStage.ACQUAINTANCE
        else:
            return RelationshipStage.STRANGER
    
    def _should_change_stage(self, current: RelationshipStage, new: RelationshipStage, score: float) -> bool:
        """Determine if relationship stage should change (with hysteresis)"""
        stage_order = [RelationshipStage.STRANGER, RelationshipStage.ACQUAINTANCE, 
                      RelationshipStage.TRUSTED, RelationshipStage.INTIMATE]
        
        current_idx = stage_order.index(current)
        new_idx = stage_order.index(new)
        
        # Allow progression if score is strong enough
        if new_idx > current_idx:
            return score > 0.6  # Higher threshold for progression
        # Allow regression if score is low enough
        elif new_idx < current_idx:
            return score < 0.4  # Lower threshold for regression
        else:
            return False
    
    def determine_emotional_response(self, interaction_data: Dict[str, Any], 
                                   user_profile: HybridUserProfile) -> EmotionalState:
        """Enhanced emotional response determination"""
        sentiment = interaction_data.get('sentiment', 0.0)
        urgency = interaction_data.get('urgency', 0.0)
        intent = interaction_data.get('intent', 'conversation')
        emotional_indicators = interaction_data.get('emotional_indicators', {})
        
        # Base emotional response on sentiment and emotional indicators
        base_emotion = self._calculate_base_emotion(sentiment, emotional_indicators)
        
        # Modify based on urgency
        if urgency > 0.7:
            if base_emotion in [EmotionalState.NEUTRAL, EmotionalState.ENGAGED]:
                base_emotion = EmotionalState.CONCERNED
        
        # Modify based on relationship stage
        base_emotion = self._adjust_for_relationship(base_emotion, user_profile.relationship_stage)
        
        # Consider user's emotional state and respond empathetically
        base_emotion = self._apply_empathetic_response(base_emotion, emotional_indicators)
        
        # Update emotion history
        self._update_emotion_history(base_emotion, user_profile.user_id)
        
        self.current_emotional_state = base_emotion
        return base_emotion
    
    def _calculate_base_emotion(self, sentiment: float, emotional_indicators: Dict[str, float]) -> EmotionalState:
        """Calculate base emotional state from sentiment and indicators"""
        # Check for specific emotional indicators first
        max_emotion = max(emotional_indicators.items(), key=lambda x: x[1], default=('neutral', 0))
        
        if max_emotion[1] > 0.5:
            emotion_mapping = {
                'joy': EmotionalState.ENTHUSIASTIC,
                'sadness': EmotionalState.CONCERNED,
                'anger': EmotionalState.PROTECTIVE,
                'fear': EmotionalState.CONCERNED,
                'surprise': EmotionalState.CURIOUS,
                'trust': EmotionalState.ENGAGED
            }
            return emotion_mapping.get(max_emotion[0], EmotionalState.NEUTRAL)
        
        # Fall back to sentiment-based emotion
        if sentiment > 0.5:
            return EmotionalState.ENTHUSIASTIC
        elif sentiment > 0.2:
            return EmotionalState.ENGAGED
        elif sentiment < -0.3:
            return EmotionalState.CONCERNED
        else:
            return EmotionalState.NEUTRAL
    
    def _adjust_for_relationship(self, emotion: EmotionalState, stage: RelationshipStage) -> EmotionalState:
        """Adjust emotional response based on relationship stage"""
        if stage == RelationshipStage.INTIMATE:
            # More emotionally expressive with intimate relationships
            if emotion == EmotionalState.NEUTRAL:
                return EmotionalState.ENGAGED
            elif emotion == EmotionalState.ENGAGED:
                return EmotionalState.ENTHUSIASTIC
        elif stage == RelationshipStage.STRANGER:
            # More reserved with strangers
            if emotion == EmotionalState.ENTHUSIASTIC:
                return EmotionalState.ENGAGED
        
        return emotion
    
    def _apply_empathetic_response(self, base_emotion: EmotionalState, 
                                  emotional_indicators: Dict[str, float]) -> EmotionalState:
        """Apply empathetic response based on user's emotional state"""
        user_sadness = emotional_indicators.get('sadness', 0.0)
        user_fear = emotional_indicators.get('fear', 0.0)
        user_anger = emotional_indicators.get('anger', 0.0)
        
        # Respond with concern to negative emotions
        if user_sadness > 0.5 or user_fear > 0.5:
            return EmotionalState.CONCERNED
        elif user_anger > 0.5:
            return EmotionalState.PROTECTIVE
        
        return base_emotion
    
    def _update_emotion_history(self, emotion: EmotionalState, user_id: str):
        """Update emotion history with context"""
        self.emotion_history.append({
            'emotion': emotion,
            'timestamp': datetime.now(),
            'user_id': user_id,
            'context': {
                'previous_emotion': self.current_emotional_state,
                'transition_reason': 'user_interaction'
            }
        })
        
        # Keep only recent emotion history
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
    
    def generate_response_tone(self, emotional_state: EmotionalState, 
                             relationship_stage: RelationshipStage,
                             user_profile: HybridUserProfile) -> Dict[str, Any]:
        """Generate enhanced response tone with personality adaptation"""
        
        # Base tone mapping
        base_tone = self._get_base_tone_mapping(emotional_state, relationship_stage)
        
        # Adapt to user's communication style
        adapted_tone = self._adapt_to_user_style(base_tone, user_profile.communication_style)
        
        # Add personality-based adjustments
        personality_adjusted = self._apply_personality_adjustments(adapted_tone, user_profile.personality_model)
        
        return personality_adjusted
    
    def _get_base_tone_mapping(self, emotional_state: EmotionalState, 
                              relationship_stage: RelationshipStage) -> Dict[str, float]:
        """Get base tone mapping for emotion and relationship combination"""
        tone_mapping = {
            (EmotionalState.NEUTRAL, RelationshipStage.STRANGER): 
                {'formality': 0.8, 'warmth': 0.3, 'detail': 0.7, 'empathy': 0.4},
            (EmotionalState.NEUTRAL, RelationshipStage.ACQUAINTANCE): 
                {'formality': 0.6, 'warmth': 0.5, 'detail': 0.6, 'empathy': 0.5},
            (EmotionalState.NEUTRAL, RelationshipStage.TRUSTED): 
                {'formality': 0.4, 'warmth': 0.7, 'detail': 0.7, 'empathy': 0.7},
            (EmotionalState.NEUTRAL, RelationshipStage.INTIMATE): 
                {'formality': 0.2, 'warmth': 0.9, 'detail': 0.8, 'empathy': 0.8},
            
            (EmotionalState.ENTHUSIASTIC, RelationshipStage.STRANGER): 
                {'formality': 0.7, 'warmth': 0.6, 'detail': 0.7, 'empathy': 0.5},
            (EmotionalState.ENTHUSIASTIC, RelationshipStage.INTIMATE): 
                {'formality': 0.1, 'warmth': 1.0, 'detail': 0.8, 'empathy': 0.9},
            
            (EmotionalState.CONCERNED, RelationshipStage.STRANGER): 
                {'formality': 0.8, 'warmth': 0.5, 'detail': 0.9, 'empathy': 0.7},
            (EmotionalState.CONCERNED, RelationshipStage.INTIMATE): 
                {'formality': 0.2, 'warmth': 0.9, 'detail': 1.0, 'empathy': 1.0}
        }
        
        return tone_mapping.get((emotional_state, relationship_stage), 
                               {'formality': 0.5, 'warmth': 0.5, 'detail': 0.7, 'empathy': 0.6})
    
    def _adapt_to_user_style(self, base_tone: Dict[str, float], 
                           user_style: Dict[str, float]) -> Dict[str, float]:
        """Adapt tone to match user's communication style"""
        adapted = base_tone.copy()
        
        # Adjust formality based on user preference
        if user_style['formal'] > user_style['casual']:
            adapted['formality'] = min(1.0, adapted['formality'] + 0.2)
        else:
            adapted['formality'] = max(0.0, adapted['formality'] - 0.2)
        
        # Adjust emotional expression
        if user_style['emotional'] > 0.7:
            adapted['warmth'] = min(1.0, adapted['warmth'] + 0.1)
            adapted['empathy'] = min(1.0, adapted['empathy'] + 0.1)
        
        return adapted
    
    def _apply_personality_adjustments(self, tone: Dict[str, float], 
                                     personality: Dict[str, float]) -> Dict[str, float]:
        """Apply personality-based tone adjustments"""
        adjusted = tone.copy()
        
        # Extraversion affects warmth
        extraversion_factor = (personality['extraversion'] - 0.5) * 0.2
        adjusted['warmth'] = max(0.0, min(1.0, adjusted['warmth'] + extraversion_factor))
        
        # Agreeableness affects empathy
        agreeableness_factor = (personality['agreeableness'] - 0.5) * 0.2
        adjusted['empathy'] = max(0.0, min(1.0, adjusted['empathy'] + agreeableness_factor))
        
        # Conscientiousness affects detail level
        conscientiousness_factor = (personality['conscientiousness'] - 0.5) * 0.2
        adjusted['detail'] = max(0.0, min(1.0, adjusted['detail'] + conscientiousness_factor))
        
        return adjusted
    
    def _calculate_time_factor(self, last_interaction: datetime) -> float:
        """Calculate time factor for relationship evaluation"""
        time_diff = datetime.now() - last_interaction
        days_ago = time_diff.days
        
        if days_ago == 0:
            return 1.0
        elif days_ago <= 7:
            return 0.8
        elif days_ago <= 30:
            return 0.5
        else:
            return 0.2

# ===============================
# HYBRID BRAIN ORCHESTRATOR
# ===============================

class HybridBrainOrchestrator:
    """Main orchestrator for the hybrid AI brain system"""

    def __init__(self):
        self.perception = HybridPerceptionLayer()
        self.memory = HybridMemorySystem()
        self.relationship_engine = HybridRelationshipEngine(self.memory)
        self.session_data = {}
        self.performance_metrics = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'average_response_time': 0.0,
            'user_satisfaction_scores': []
        }
        
        logger.info("Hybrid AI Brain initialized successfully")
    
    async def process_interaction(self, input_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Main interaction processing pipeline"""
        start_time = time.time()
        
        try:
            # 1. Perception - Process input
            processed_input = self.perception.process_input(input_data)
            
            # 2. Memory - Retrieve context and update user profile
            user_profile = self.memory.get_user_profile(user_id)
            relevant_memories = self.memory.retrieve_memories(
                processed_input['content'], user_id=user_id, limit=5
            )
            
            # 3. Relationship - Evaluate relationship and emotional state
            relationship_stage = self.relationship_engine.evaluate_relationship_stage(
                user_id, processed_input
            )
            emotional_state = self.relationship_engine.determine_emotional_response(
                processed_input, user_profile
            )
            
            # 4. Generate response tone
            response_tone = self.relationship_engine.generate_response_tone(
                emotional_state, relationship_stage, user_profile
            )
            
            # 5. Create memory of this interaction
            interaction_memory = HybridMemory(
                id=str(uuid.uuid4()),
                content=f"User said: {processed_input['content']}",
                memory_type=MemoryType.EPISODIC,
                timestamp=datetime.now(),
                emotional_valence=processed_input.get('sentiment', 0.0),
                importance=self._calculate_interaction_importance(processed_input),
                user_id=user_id,
                tags=['interaction', intent] if (intent := processed_input.get('intent')) else ['interaction']
            )
            
            self.memory.store_memory(interaction_memory)
            
            # 6. Update user relationship
            self.memory.update_user_relationship(user_id, processed_input)
            
            # 7. Generate response
            response = await self._generate_response(
                processed_input, user_profile, relevant_memories, 
                emotional_state, response_tone
            )
            
            # 8. Update performance metrics
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, True)
            
            return {
                'response': response,
                'emotional_state': emotional_state.value,
                'relationship_stage': relationship_stage.value,
                'response_tone': response_tone,
                'processing_time': processing_time,
                'relevant_memories_count': len(relevant_memories),
                'user_profile_summary': {
                    'trust_level': user_profile.trust_level,
                    'emotional_bond': user_profile.emotional_bond,
                    'interaction_count': user_profile.interaction_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing interaction: {e}")
            self._update_performance_metrics(time.time() - start_time, False)
            return {
                'response': "I apologize, but I encountered an issue processing your request. Please try again.",
                'emotional_state': EmotionalState.CONCERNED.value,
                'error': str(e)
            }
    
    def _calculate_interaction_importance(self, processed_input: Dict[str, Any]) -> float:
        """Calculate importance score for interaction"""
        base_importance = 0.5
        
        # Increase importance for emotional content
        sentiment = abs(processed_input.get('sentiment', 0.0))
        base_importance += sentiment * 0.3
        
        # Increase importance for urgent content
        urgency = processed_input.get('urgency', 0.0)
        base_importance += urgency * 0.2
        
        # Increase importance for specific intents
        intent = processed_input.get('intent', '')
        if intent in ['emotional_expression', 'memory_storage']:
            base_importance += 0.2
        
        return min(base_importance, 1.0)
    
    async def _generate_response(self, processed_input: Dict[str, Any], 
                               user_profile: HybridUserProfile,
                               relevant_memories: List[HybridMemory],
                               emotional_state: EmotionalState,
                               response_tone: Dict[str, float]) -> str:
        """Generate contextual response based on all factors"""
        
        # Build context for response generation
        context = {
            'user_input': processed_input['content'],
            'user_relationship_stage': user_profile.relationship_stage.value,
            'emotional_state': emotional_state.value,
            'response_tone': response_tone,
            'relevant_memories': [m.content for m in relevant_memories[:3]],
            'user_preferences': user_profile.preferences,
            'communication_style': user_profile.communication_style
        }
        
        # Generate response based on intent
        intent = processed_input.get('intent', 'conversation')
        
        if intent == 'emotional_expression':
            return self._generate_empathetic_response(context)
        elif intent == 'request_help':
            return self._generate_helpful_response(context)
        elif intent == 'memory_storage':
            return self._generate_memory_confirmation_response(context)
        else:
            return self._generate_conversational_response(context)
    
    def _generate_empathetic_response(self, context: Dict[str, Any]) -> str:
        """Generate empathetic response for emotional expressions"""
        emotional_state = context['emotional_state']
        tone = context['response_tone']
        
        if emotional_state == 'concerned':
            if tone['empathy'] > 0.7:
                return "I can sense that you're going through something difficult. I'm here to listen and support you in whatever way I can. Would you like to talk about what's on your mind?"
            else:
                return "I notice you might be dealing with something challenging. How can I help you today?"
        elif emotional_state == 'enthusiastic':
            return "I love your enthusiasm! It's wonderful to see you so excited. Tell me more about what's got you feeling so positive!"
        else:
            return "I'm here and ready to listen. What would you like to share with me?"
    
    def _generate_helpful_response(self, context: Dict[str, Any]) -> str:
        """Generate helpful response for assistance requests"""
        relationship_stage = context['user_relationship_stage']
        tone = context['response_tone']
        
        if relationship_stage == 'intimate' and tone['warmth'] > 0.8:
            return "Of course! I'd be happy to help you with that. We've worked together before, so I have a good sense of what works best for you. What specifically would you like assistance with?"
        elif relationship_stage == 'stranger' and tone['formality'] > 0.7:
            return "I'd be pleased to assist you. Could you please provide more details about what you need help with so I can offer the most appropriate guidance?"
        else:
            return "I'm here to help! What can I assist you with today?"
    
    def _generate_memory_confirmation_response(self, context: Dict[str, Any]) -> str:
        """Generate response confirming memory storage"""
        return "I've made note of that information. I'll remember this for our future conversations. Is there anything specific about this that you'd like me to pay particular attention to?"
    
    def _generate_conversational_response(self, context: Dict[str, Any]) -> str:
        """Generate general conversational response"""
        relationship_stage = context['user_relationship_stage']
        relevant_memories = context['relevant_memories']
        
        if relevant_memories and relationship_stage in ['trusted', 'intimate']:
            return f"That's interesting! It reminds me of when we discussed {relevant_memories[0][:50]}... What's your perspective on this?"
        else:
            return "That's an interesting point. I'd love to hear more about your thoughts on this."
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """Update system performance metrics"""
        self.performance_metrics['total_interactions'] += 1
        
        if success:
            self.performance_metrics['successful_interactions'] += 1
        
        # Update average response time
        current_avg = self.performance_metrics['average_response_time']
        total = self.performance_metrics['total_interactions']
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        total_interactions = self.performance_metrics['total_interactions']
        successful_interactions = self.performance_metrics['successful_interactions']
        
        return {
            'performance_metrics': {
                'total_interactions': total_interactions,
                'success_rate': successful_interactions / max(total_interactions, 1),
                'average_response_time': self.performance_metrics['average_response_time'],
                'active_users': len(self.memory.user_profiles),
                'memory_utilization': {
                    'long_term_memories': len(self.memory.long_term_memory),
                    'short_term_memories': len(self.memory.short_term_memory)
                }
            },
            'emotional_intelligence': {
                'current_emotional_state': self.relationship_engine.current_emotional_state.value,
                'emotion_history_length': len(self.relationship_engine.emotion_history),
                'trust_factors': self.relationship_engine.trust_factors
            },
            'relationship_summary': {
                'total_users': len(self.memory.user_profiles),
                'relationship_stages': self._get_relationship_stage_distribution()
            }
        }
    
    def _get_relationship_stage_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship stages across users"""
        distribution = {stage.value: 0 for stage in RelationshipStage}
        
        for profile in self.memory.user_profiles.values():
            distribution[profile.relationship_stage.value] += 1
        
        return distribution
    
    def get_user_relationship_summary(self, user_id: str) -> Dict[str, Any]:
        """Get detailed relationship summary for specific user"""
        if user_id not in self.memory.user_profiles:
            return {'error': 'User not found'}
        
        profile = self.memory.user_profiles[user_id]
        user_memories = [m for m in self.memory.long_term_memory.values() if m.user_id == user_id]
        
        return {
            'user_profile': {
                'relationship_stage': profile.relationship_stage.value,
                'trust_level': profile.trust_level,
                'emotional_bond': profile.emotional_bond,
                'interaction_count': profile.interaction_count,
                'last_interaction': profile.last_interaction.isoformat(),
                'communication_style': profile.communication_style,
                'personality_model': profile.personality_model
            },
            'memory_summary': {
                'stored_memories': len(user_memories),
                'memory_types': list(set(m.memory_type.value for m in user_memories)),
                'average_importance': sum(m.importance for m in user_memories) / max(len(user_memories), 1),
                'emotional_memory_distribution': self._get_emotional_memory_distribution(user_memories)
            },
            'interaction_patterns': {
                'preferred_communication_style': max(profile.communication_style.items(), key=lambda x: x[1])[0],
                'relationship_progression': self._calculate_relationship_progression(profile)
            }
        }
    
    def _get_emotional_memory_distribution(self, memories: List[HybridMemory]) -> Dict[str, int]:
        """Get distribution of emotional valence in memories"""
        distribution = {'very_positive': 0, 'positive': 0, 'neutral': 0, 'negative': 0, 'very_negative': 0}
        
        for memory in memories:
            bucket = self.memory._get_valence_bucket(memory.emotional_valence)
            distribution[bucket] += 1
        
        return distribution
    
    def _calculate_relationship_progression(self, profile: HybridUserProfile) -> Dict[str, Any]:
        """Calculate relationship progression metrics"""
        # Simple progression calculation based on current metrics
        progression_score = (
            profile.trust_level * 0.4 +
            profile.emotional_bond * 0.3 +
            min(profile.interaction_count / 100.0, 1.0) * 0.3
        )
        
        return {
            'progression_score': progression_score,
            'next_stage_probability': self._calculate_next_stage_probability(profile),
            'relationship_health': 'excellent' if progression_score > 0.8 else 
                                 'good' if progression_score > 0.6 else 
                                 'developing' if progression_score > 0.3 else 'early'
        }
    
    def _calculate_next_stage_probability(self, profile: HybridUserProfile) -> float:
        """Calculate probability of advancing to next relationship stage"""
        current_stage = profile.relationship_stage
        
        if current_stage == RelationshipStage.INTIMATE:
            return 0.0  # Already at highest stage
        
        # Calculate based on current metrics and thresholds
        trust_factor = profile.trust_level
        interaction_factor = min(profile.interaction_count / 50.0, 1.0)
        bond_factor = profile.emotional_bond
        
        combined_factor = (trust_factor + interaction_factor + bond_factor) / 3.0
        
        # Stage-specific thresholds
        if current_stage == RelationshipStage.STRANGER:
            return max(0.0, min(1.0, (combined_factor - 0.2) / 0.3))
        elif current_stage == RelationshipStage.ACQUAINTANCE:
            return max(0.0, min(1.0, (combined_factor - 0.5) / 0.3))
        elif current_stage == RelationshipStage.TRUSTED:
            return max(0.0, min(1.0, (combined_factor - 0.7) / 0.2))
        
        return 0.0

# ===============================
# MAIN HYBRID AI BRAIN CLASS
# ===============================

class HybridAIBrain:
    """Main interface for the Hybrid AI Brain system"""

    def __init__(self):
        self.orchestrator = HybridBrainOrchestrator()
        self.is_initialized = True
        logger.info("🧠 Hybrid AI Brain initialized successfully")
    
    async def process_message(self, message: str, user_id: str, 
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message with full hybrid brain capabilities"""
        input_data = {
            'type': 'text',
            'content': message,
            'context': context or {}
        }
        
        return await self.orchestrator.process_interaction(input_data, user_id)
    
    async def chat(self, message: str, user_id: str = "default_user") -> str:
        """Simple chat interface"""
        result = await self.process_message(message, user_id)
        return result.get('response', 'I apologize, but I encountered an issue.')
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return self.orchestrator.get_system_status()
    
    def get_user_relationship(self, user_id: str) -> Dict[str, Any]:
        """Get relationship summary with user"""
        return self.orchestrator.get_user_relationship_summary(user_id)
    
    def get_emotional_state(self) -> str:
        """Get current emotional state"""
        return self.orchestrator.relationship_engine.current_emotional_state.value
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            status = self.get_system_status()
            return {
                'status': 'healthy',
                'initialized': self.is_initialized,
                'performance': status['performance_metrics'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# ===============================
# INTEGRATION UTILITIES
# ===============================

def create_hybrid_brain_instance() -> HybridAIBrain:
    """Factory function to create hybrid brain instance"""
    return HybridAIBrain()

async def demo_hybrid_brain():
    """Demonstration of hybrid brain capabilities"""
    brain = create_hybrid_brain_instance()
    
    print("\n" + "="*60)
    print("🧠 HYBRID AI BRAIN DEMONSTRATION")
    print("="*60)
    
    user_id = "demo_user"
    
    # Simulate conversation progression
    messages = [
        "Hello, I'm feeling a bit overwhelmed with work lately.",
        "Thank you for understanding. Can you help me organize my thoughts?",
        "I really appreciate your support. You're very helpful!",
        "I'm excited about a new project I'm starting. Want to hear about it?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Interaction {i} ---")
        print(f"👤 User: {message}")
        
        result = await brain.process_message(message, user_id)
        print(f"🤖 AI: {result['response']}")
        print(f"😊 Emotional State: {result['emotional_state']}")
        print(f"🤝 Relationship: {result['relationship_stage']}")
        
        if i == len(messages):
            relationship = brain.get_user_relationship(user_id)
            print(f"\n📊 Final Relationship Summary:")
            print(f"   Trust Level: {relationship['user_profile']['trust_level']:.2f}")
            print(f"   Emotional Bond: {relationship['user_profile']['emotional_bond']:.2f}")
            print(f"   Interactions: {relationship['user_profile']['interaction_count']}")
    
    # Show system status
    print("\n" + "-"*60)
    print("📈 SYSTEM STATUS")
    print("-"*60)
    status = brain.get_system_status()
    print(f"Success Rate: {status['performance_metrics']['success_rate']:.2%}")
    print(f"Active Users: {status['performance_metrics']['active_users']}")
    print(f"Current Emotional State: {status['emotional_intelligence']['current_emotional_state']}")

if __name__ == "__main__":
    asyncio.run(demo_hybrid_brain())