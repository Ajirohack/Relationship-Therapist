#!/usr/bin/env python3
"""
Emotional & Psychological Engine Layer - Layer 4 of AI Brain Architecture
Handles emotional intelligence, psychological modeling, empathy, and emotional response generation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math

from ..core.brain_architecture import BrainLayer, LayerType, LayerInput, LayerOutput

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    CALM = "calm"
    CONCERNED = "concerned"
    EMPATHETIC = "empathetic"
    ENCOURAGING = "encouraging"
    REFLECTIVE = "reflective"
    SUPPORTIVE = "supportive"
    GENTLE = "gentle"
    UNDERSTANDING = "understanding"
    HOPEFUL = "hopeful"
    PATIENT = "patient"

class PsychologicalModel(Enum):
    ATTACHMENT_THEORY = "attachment_theory"
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    EMOTIONALLY_FOCUSED = "emotionally_focused"
    GOTTMAN_METHOD = "gottman_method"
    NARRATIVE_THERAPY = "narrative_therapy"
    SOLUTION_FOCUSED = "solution_focused"

class EmotionalResponse(Enum):
    VALIDATION = "validation"
    REFLECTION = "reflection"
    REFRAME = "reframe"
    SUPPORT = "support"
    CHALLENGE = "challenge"
    NORMALIZE = "normalize"
    ENCOURAGE = "encourage"

@dataclass
class EmotionalProfile:
    """User's emotional profile and patterns"""
    primary_emotions: List[str]
    emotional_volatility: float  # 0-1 scale
    emotional_awareness: float  # 0-1 scale
    emotional_regulation: float  # 0-1 scale
    attachment_style: str
    coping_mechanisms: List[str]
    triggers: List[str]
    strengths: List[str]
    growth_areas: List[str]
    last_updated: datetime

@dataclass
class PsychologicalAssessment:
    """Psychological assessment of current state"""
    assessment_id: str
    dominant_emotions: List[str]
    emotional_intensity: float  # 0-1 scale
    psychological_safety: float  # 0-1 scale
    stress_level: float  # 0-1 scale
    resilience_indicators: List[str]
    vulnerability_indicators: List[str]
    recommended_approach: str
    therapeutic_model: str
    confidence: float
    timestamp: datetime

@dataclass
class EmotionalResponse:
    """Emotional response strategy"""
    response_id: str
    response_type: str
    emotional_tone: str
    empathy_level: float  # 0-1 scale
    validation_elements: List[str]
    reframing_suggestions: List[str]
    supportive_statements: List[str]
    diego_emotional_state: str
    confidence: float
    timestamp: datetime

@dataclass
class TherapeuticIntervention:
    """Therapeutic intervention recommendation"""
    intervention_id: str
    intervention_type: str
    psychological_model: str
    description: str
    rationale: str
    expected_outcome: str
    implementation_steps: List[str]
    timing_recommendation: str
    stage_appropriateness: List[str]
    confidence: float
    timestamp: datetime

class EmotionalPsychologicalLayer(BrainLayer):
    """Layer 4: Emotional & Psychological Engine - Emotional intelligence and psychological modeling"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(LayerType.EMOTIONAL_PSYCHOLOGICAL, config)
        
        # Emotional intelligence components
        self.emotion_detector = EmotionDetector()
        self.empathy_engine = EmpathyEngine()
        self.psychological_assessor = PsychologicalAssessor()
        self.therapeutic_advisor = TherapeuticAdvisor()
        
        # Diego's emotional characteristics
        self.diego_emotional_profile = self._initialize_diego_emotional_profile()
        
        # Psychological models and frameworks
        self.psychological_frameworks = self._load_psychological_frameworks()
        self.therapeutic_techniques = self._load_therapeutic_techniques()
        
        # Configuration
        self.empathy_sensitivity = config.get("empathy_sensitivity", 0.8)
        self.emotional_response_threshold = config.get("emotional_response_threshold", 0.6)
        self.max_interventions_per_session = config.get("max_interventions_per_session", 3)
    
    async def process(self, input_data: LayerInput) -> LayerOutput:
        """Process input through emotional and psychological layer"""
        try:
            self.logger.debug(f"Processing emotional/psychological input: {input_data.layer_id}")
            
            # Extract data from previous layers
            perception_result = input_data.data.get("perception_result", {})
            user_profile = input_data.data.get("user_profile", {})
            conversation_context = input_data.data.get("conversation_context", {})
            pattern_analysis = input_data.data.get("pattern_analysis", [])
            insights = input_data.data.get("insights", [])
            stage_analysis = input_data.data.get("stage_analysis", {})
            recommendations = input_data.data.get("recommendations", {})
            
            # Perform emotional analysis
            emotional_profile = await self._analyze_emotional_profile(
                user_profile, conversation_context, pattern_analysis
            )
            
            # Conduct psychological assessment
            psychological_assessment = await self._conduct_psychological_assessment(
                perception_result, emotional_profile, insights, conversation_context
            )
            
            # Generate empathetic response strategy
            emotional_response = await self._generate_emotional_response(
                psychological_assessment, emotional_profile, stage_analysis
            )
            
            # Recommend therapeutic interventions
            therapeutic_interventions = await self._recommend_therapeutic_interventions(
                psychological_assessment, insights, stage_analysis
            )
            
            # Update Diego's emotional state
            diego_emotional_state = await self._update_diego_emotional_state(
                psychological_assessment, emotional_response, conversation_context
            )
            
            # Generate emotional intelligence insights
            emotional_insights = await self._generate_emotional_insights(
                emotional_profile, psychological_assessment, conversation_context
            )
            
            # Assess emotional safety and readiness
            emotional_safety_assessment = await self._assess_emotional_safety(
                psychological_assessment, conversation_context, user_profile
            )
            
            # Prepare output data
            output_data = {
                "emotional_profile": asdict(emotional_profile),
                "psychological_assessment": asdict(psychological_assessment),
                "emotional_response": asdict(emotional_response),
                "therapeutic_interventions": [asdict(ti) for ti in therapeutic_interventions],
                "diego_emotional_state": diego_emotional_state,
                "emotional_insights": emotional_insights,
                "emotional_safety_assessment": emotional_safety_assessment,
                "emotional_metadata": {
                    "layer": "emotional_psychological",
                    "timestamp": datetime.now().isoformat(),
                    "empathy_level": emotional_response.empathy_level,
                    "psychological_safety": psychological_assessment.psychological_safety,
                    "recommended_therapeutic_model": psychological_assessment.therapeutic_model,
                    "diego_emotional_tone": diego_emotional_state.get("current_tone", "supportive")
                },
                # Pass through previous layer data
                "perception_result": perception_result,
                "user_profile": user_profile,
                "conversation_context": conversation_context,
                "pattern_analysis": pattern_analysis,
                "insights": insights,
                "stage_analysis": stage_analysis,
                "recommendations": recommendations
            }
            
            return LayerOutput(
                layer_id=self.layer_id,
                data=output_data,
                timestamp=datetime.now(),
                target_layers=["decision_action", "toolbox_motor"],
                confidence=self._calculate_overall_confidence(output_data),
                metadata={
                    "emotional_summary": {
                        "primary_emotion": emotional_profile.primary_emotions[0] if emotional_profile.primary_emotions else "neutral",
                        "empathy_level": emotional_response.empathy_level,
                        "psychological_safety": psychological_assessment.psychological_safety,
                        "interventions_recommended": len(therapeutic_interventions),
                        "diego_emotional_state": diego_emotional_state.get("current_state", "supportive")
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in emotional/psychological processing: {str(e)}")
            raise
    
    async def _analyze_emotional_profile(self, user_profile: Dict[str, Any],
                                       conversation_context: Dict[str, Any],
                                       pattern_analysis: List[Dict[str, Any]]) -> EmotionalProfile:
        """Analyze user's emotional profile"""
        conversation_history = conversation_context.get("conversation_history", [])
        emotional_trajectory = conversation_context.get("emotional_trajectory", [])
        
        # Extract primary emotions from recent interactions
        primary_emotions = self._extract_primary_emotions(emotional_trajectory)
        
        # Calculate emotional metrics
        emotional_volatility = self._calculate_emotional_volatility(emotional_trajectory)
        emotional_awareness = self._assess_emotional_awareness(conversation_history)
        emotional_regulation = self._assess_emotional_regulation(emotional_trajectory, pattern_analysis)
        
        # Determine attachment style
        attachment_style = self._determine_attachment_style(conversation_history, pattern_analysis)
        
        # Identify coping mechanisms and triggers
        coping_mechanisms = self._identify_coping_mechanisms(conversation_history, pattern_analysis)
        triggers = self._identify_emotional_triggers(conversation_history, pattern_analysis)
        
        # Assess strengths and growth areas
        strengths = self._identify_emotional_strengths(conversation_history, pattern_analysis)
        growth_areas = self._identify_emotional_growth_areas(pattern_analysis)
        
        return EmotionalProfile(
            primary_emotions=primary_emotions,
            emotional_volatility=emotional_volatility,
            emotional_awareness=emotional_awareness,
            emotional_regulation=emotional_regulation,
            attachment_style=attachment_style,
            coping_mechanisms=coping_mechanisms,
            triggers=triggers,
            strengths=strengths,
            growth_areas=growth_areas,
            last_updated=datetime.now()
        )
    
    async def _conduct_psychological_assessment(self, perception_result: Dict[str, Any],
                                              emotional_profile: EmotionalProfile,
                                              insights: List[Dict[str, Any]],
                                              conversation_context: Dict[str, Any]) -> PsychologicalAssessment:
        """Conduct comprehensive psychological assessment"""
        
        # Analyze dominant emotions in current context
        dominant_emotions = emotional_profile.primary_emotions[:3]
        
        # Calculate emotional intensity
        emotional_intensity = self._calculate_emotional_intensity(
            perception_result, emotional_profile
        )
        
        # Assess psychological safety
        psychological_safety = self._assess_psychological_safety(
            conversation_context, emotional_profile
        )
        
        # Evaluate stress level
        stress_level = self._evaluate_stress_level(
            emotional_profile, insights, perception_result
        )
        
        # Identify resilience and vulnerability indicators
        resilience_indicators = self._identify_resilience_indicators(
            emotional_profile, conversation_context
        )
        vulnerability_indicators = self._identify_vulnerability_indicators(
            emotional_profile, insights
        )
        
        # Recommend therapeutic approach
        recommended_approach = self._recommend_therapeutic_approach(
            emotional_profile, dominant_emotions, stress_level
        )
        
        # Select appropriate therapeutic model
        therapeutic_model = self._select_therapeutic_model(
            emotional_profile, insights, conversation_context
        )
        
        # Calculate assessment confidence
        confidence = self._calculate_assessment_confidence(
            emotional_profile, len(conversation_context.get("conversation_history", []))
        )
        
        return PsychologicalAssessment(
            assessment_id=f"psych_assessment_{datetime.now().timestamp()}",
            dominant_emotions=dominant_emotions,
            emotional_intensity=emotional_intensity,
            psychological_safety=psychological_safety,
            stress_level=stress_level,
            resilience_indicators=resilience_indicators,
            vulnerability_indicators=vulnerability_indicators,
            recommended_approach=recommended_approach,
            therapeutic_model=therapeutic_model,
            confidence=confidence,
            timestamp=datetime.now()
        )
    
    async def _generate_emotional_response(self, psychological_assessment: PsychologicalAssessment,
                                         emotional_profile: EmotionalProfile,
                                         stage_analysis: Dict[str, Any]) -> EmotionalResponse:
        """Generate empathetic emotional response strategy"""
        
        # Determine response type based on assessment
        response_type = self._determine_response_type(
            psychological_assessment, emotional_profile
        )
        
        # Set emotional tone
        emotional_tone = self._determine_emotional_tone(
            psychological_assessment.dominant_emotions,
            psychological_assessment.psychological_safety
        )
        
        # Calculate empathy level
        empathy_level = self._calculate_empathy_level(
            psychological_assessment, emotional_profile
        )
        
        # Generate validation elements
        validation_elements = self._generate_validation_elements(
            psychological_assessment.dominant_emotions,
            emotional_profile
        )
        
        # Create reframing suggestions
        reframing_suggestions = self._generate_reframing_suggestions(
            psychological_assessment, emotional_profile
        )
        
        # Develop supportive statements
        supportive_statements = self._generate_supportive_statements(
            emotional_tone, psychological_assessment
        )
        
        # Determine Diego's emotional state
        diego_emotional_state = self._determine_diego_emotional_state(
            psychological_assessment, emotional_tone
        )
        
        return EmotionalResponse(
            response_id=f"emotional_response_{datetime.now().timestamp()}",
            response_type=response_type,
            emotional_tone=emotional_tone,
            empathy_level=empathy_level,
            validation_elements=validation_elements,
            reframing_suggestions=reframing_suggestions,
            supportive_statements=supportive_statements,
            diego_emotional_state=diego_emotional_state,
            confidence=psychological_assessment.confidence,
            timestamp=datetime.now()
        )
    
    async def _recommend_therapeutic_interventions(self, psychological_assessment: PsychologicalAssessment,
                                                 insights: List[Dict[str, Any]],
                                                 stage_analysis: Dict[str, Any]) -> List[TherapeuticIntervention]:
        """Recommend appropriate therapeutic interventions"""
        interventions = []
        current_stage = stage_analysis.get("current_stage", "APP")
        
        # High-priority interventions based on psychological assessment
        if psychological_assessment.stress_level > 0.7:
            interventions.append(TherapeuticIntervention(
                intervention_id=f"intervention_{datetime.now().timestamp()}",
                intervention_type="stress_reduction",
                psychological_model=psychological_assessment.therapeutic_model,
                description="Stress reduction and emotional regulation techniques",
                rationale=f"High stress level detected ({psychological_assessment.stress_level:.2f})",
                expected_outcome="Reduced stress and improved emotional regulation",
                implementation_steps=[
                    "Introduce breathing exercises",
                    "Teach grounding techniques",
                    "Explore stress triggers",
                    "Develop coping strategies"
                ],
                timing_recommendation="immediate",
                stage_appropriateness=["APP", "FPP", "RPP"],
                confidence=0.9,
                timestamp=datetime.now()
            ))
        
        if psychological_assessment.psychological_safety < 0.5:
            interventions.append(TherapeuticIntervention(
                intervention_id=f"intervention_{datetime.now().timestamp()}",
                intervention_type="safety_building",
                psychological_model="attachment_theory",
                description="Build psychological safety and trust",
                rationale=f"Low psychological safety ({psychological_assessment.psychological_safety:.2f})",
                expected_outcome="Increased sense of safety and trust",
                implementation_steps=[
                    "Validate emotions and experiences",
                    "Establish clear boundaries",
                    "Demonstrate consistency and reliability",
                    "Use gentle, non-threatening language"
                ],
                timing_recommendation="immediate",
                stage_appropriateness=["APP"],
                confidence=0.85,
                timestamp=datetime.now()
            ))
        
        # Stage-specific interventions
        if current_stage == "FPP" and psychological_assessment.emotional_intensity > 0.6:
            interventions.append(TherapeuticIntervention(
                intervention_id=f"intervention_{datetime.now().timestamp()}",
                intervention_type="emotional_processing",
                psychological_model="emotionally_focused",
                description="Deep emotional processing and exploration",
                rationale="High emotional intensity in FPP stage",
                expected_outcome="Better emotional understanding and processing",
                implementation_steps=[
                    "Explore underlying emotions",
                    "Identify emotional patterns",
                    "Process difficult feelings",
                    "Connect emotions to relationship dynamics"
                ],
                timing_recommendation="within_session",
                stage_appropriateness=["FPP"],
                confidence=0.8,
                timestamp=datetime.now()
            ))
        
        # Limit number of interventions
        return interventions[:self.max_interventions_per_session]
    
    async def _update_diego_emotional_state(self, psychological_assessment: PsychologicalAssessment,
                                          emotional_response: EmotionalResponse,
                                          conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Update Diego's emotional state based on assessment"""
        
        # Diego's emotional responsiveness
        base_empathy = self.diego_emotional_profile.get("base_empathy", 0.8)
        emotional_sensitivity = self.diego_emotional_profile.get("emotional_sensitivity", 0.7)
        
        # Adjust Diego's emotional state based on user's state
        if psychological_assessment.stress_level > 0.7:
            current_state = EmotionalState.CONCERNED.value
            current_tone = "gentle_concern"
        elif psychological_assessment.psychological_safety < 0.5:
            current_state = EmotionalState.SUPPORTIVE.value
            current_tone = "warm_supportive"
        elif "sadness" in psychological_assessment.dominant_emotions:
            current_state = EmotionalState.EMPATHETIC.value
            current_tone = "compassionate"
        elif "anxiety" in psychological_assessment.dominant_emotions:
            current_state = EmotionalState.CALM.value
            current_tone = "reassuring"
        else:
            current_state = EmotionalState.UNDERSTANDING.value
            current_tone = "balanced_supportive"
        
        # Calculate emotional resonance
        emotional_resonance = min(1.0, base_empathy * emotional_response.empathy_level)
        
        return {
            "current_state": current_state,
            "current_tone": current_tone,
            "empathy_level": base_empathy,
            "emotional_resonance": emotional_resonance,
            "responsiveness": emotional_sensitivity,
            "emotional_adjustments": {
                "patience_level": 0.9 if psychological_assessment.stress_level > 0.6 else 0.7,
                "gentleness": 0.9 if psychological_assessment.psychological_safety < 0.6 else 0.7,
                "encouragement": 0.8 if "hopelessness" in psychological_assessment.dominant_emotions else 0.6
            },
            "last_updated": datetime.now().isoformat()
        }
    
    async def _generate_emotional_insights(self, emotional_profile: EmotionalProfile,
                                         psychological_assessment: PsychologicalAssessment,
                                         conversation_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate emotional intelligence insights"""
        insights = []
        
        # Emotional awareness insight
        if emotional_profile.emotional_awareness < 0.5:
            insights.append({
                "type": "emotional_awareness",
                "title": "Developing Emotional Awareness",
                "description": "User shows limited emotional awareness, which may impact relationship communication",
                "recommendations": [
                    "Practice emotional check-ins",
                    "Use emotion identification exercises",
                    "Encourage journaling about feelings"
                ],
                "priority": "medium"
            })
        
        # Emotional regulation insight
        if emotional_profile.emotional_regulation < 0.6:
            insights.append({
                "type": "emotional_regulation",
                "title": "Emotional Regulation Challenges",
                "description": "User may benefit from developing better emotional regulation skills",
                "recommendations": [
                    "Teach breathing techniques",
                    "Introduce mindfulness practices",
                    "Explore triggers and responses"
                ],
                "priority": "high" if emotional_profile.emotional_regulation < 0.4 else "medium"
            })
        
        # Attachment style insight
        if emotional_profile.attachment_style in ["anxious", "avoidant", "disorganized"]:
            insights.append({
                "type": "attachment_pattern",
                "title": f"Attachment Style: {emotional_profile.attachment_style.title()}",
                "description": f"User's {emotional_profile.attachment_style} attachment style may influence relationship dynamics",
                "recommendations": self._get_attachment_recommendations(emotional_profile.attachment_style),
                "priority": "medium"
            })
        
        return insights
    
    async def _assess_emotional_safety(self, psychological_assessment: PsychologicalAssessment,
                                     conversation_context: Dict[str, Any],
                                     user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess emotional safety and readiness for deeper work"""
        
        safety_indicators = {
            "psychological_safety": psychological_assessment.psychological_safety,
            "stress_level": psychological_assessment.stress_level,
            "emotional_stability": 1.0 - psychological_assessment.emotional_intensity,
            "trust_level": conversation_context.get("trust_progression", [0])[-1] / 100.0 if conversation_context.get("trust_progression") else 0.5
        }
        
        # Calculate overall safety score
        safety_weights = {
            "psychological_safety": 0.4,
            "stress_level": -0.3,  # Negative because high stress reduces safety
            "emotional_stability": 0.2,
            "trust_level": 0.3
        }
        
        overall_safety = sum(
            safety_indicators[key] * weight 
            for key, weight in safety_weights.items()
        )
        overall_safety = max(0.0, min(1.0, overall_safety))
        
        # Determine readiness for different types of work
        readiness_assessment = {
            "basic_conversation": overall_safety > 0.3,
            "emotional_exploration": overall_safety > 0.5,
            "deep_processing": overall_safety > 0.7,
            "challenging_topics": overall_safety > 0.8
        }
        
        # Safety recommendations
        safety_recommendations = []
        if overall_safety < 0.5:
            safety_recommendations.extend([
                "Focus on building trust and safety",
                "Use gentle, non-threatening approaches",
                "Validate emotions frequently"
            ])
        if psychological_assessment.stress_level > 0.7:
            safety_recommendations.append("Address stress and anxiety before deeper work")
        
        return {
            "overall_safety_score": overall_safety,
            "safety_indicators": safety_indicators,
            "readiness_assessment": readiness_assessment,
            "safety_recommendations": safety_recommendations,
            "cautions": self._generate_safety_cautions(psychological_assessment),
            "green_lights": self._generate_safety_green_lights(psychological_assessment)
        }
    
    # Helper methods for emotional analysis
    def _extract_primary_emotions(self, emotional_trajectory: List[Dict[str, Any]]) -> List[str]:
        """Extract primary emotions from emotional trajectory"""
        if not emotional_trajectory:
            return ["neutral"]
        
        emotion_counts = {}
        for entry in emotional_trajectory[-10:]:  # Last 10 entries
            emotions = entry.get("emotions", [])
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Sort by frequency and return top 3
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        return [emotion for emotion, count in sorted_emotions[:3]] or ["neutral"]
    
    def _calculate_emotional_volatility(self, emotional_trajectory: List[Dict[str, Any]]) -> float:
        """Calculate emotional volatility score"""
        if len(emotional_trajectory) < 3:
            return 0.5  # Default moderate volatility
        
        # Calculate sentiment changes
        sentiments = [entry.get("sentiment", "neutral") for entry in emotional_trajectory]
        sentiment_values = {"positive": 1, "neutral": 0, "negative": -1}
        
        changes = 0
        for i in range(1, len(sentiments)):
            if sentiment_values.get(sentiments[i], 0) != sentiment_values.get(sentiments[i-1], 0):
                changes += 1
        
        volatility = changes / (len(sentiments) - 1) if len(sentiments) > 1 else 0
        return min(1.0, volatility)
    
    def _assess_emotional_awareness(self, conversation_history: List[Dict[str, Any]]) -> float:
        """Assess emotional awareness from conversation"""
        if not conversation_history:
            return 0.5
        
        emotional_language_count = 0
        total_messages = len(conversation_history)
        
        emotional_keywords = [
            "feel", "feeling", "emotion", "angry", "sad", "happy", "frustrated",
            "anxious", "worried", "excited", "disappointed", "hurt", "love", "fear"
        ]
        
        for message in conversation_history:
            content = message.get("content", "").lower()
            if any(keyword in content for keyword in emotional_keywords):
                emotional_language_count += 1
        
        awareness_score = emotional_language_count / total_messages if total_messages > 0 else 0
        return min(1.0, awareness_score * 2)  # Scale up to make it more sensitive
    
    def _assess_emotional_regulation(self, emotional_trajectory: List[Dict[str, Any]],
                                   pattern_analysis: List[Dict[str, Any]]) -> float:
        """Assess emotional regulation capabilities"""
        base_score = 0.6  # Default moderate regulation
        
        # Check for regulation patterns in analysis
        regulation_patterns = [
            p for p in pattern_analysis 
            if p.get("pattern_type") == "emotional_regulation"
        ]
        
        if regulation_patterns:
            # If poor regulation detected, lower score
            poor_regulation = any(
                "volatility" in p.get("description", "").lower() or
                "dysregulation" in p.get("description", "").lower()
                for p in regulation_patterns
            )
            if poor_regulation:
                base_score = 0.3
        
        # Adjust based on emotional volatility
        volatility = self._calculate_emotional_volatility(emotional_trajectory)
        regulation_score = base_score * (1 - volatility * 0.5)
        
        return max(0.1, min(1.0, regulation_score))
    
    def _determine_attachment_style(self, conversation_history: List[Dict[str, Any]],
                                  pattern_analysis: List[Dict[str, Any]]) -> str:
        """Determine attachment style from conversation patterns"""
        # Look for attachment-related patterns
        attachment_indicators = {
            "secure": ["trust", "comfortable", "open", "balanced"],
            "anxious": ["worry", "need", "fear", "abandonment", "clingy"],
            "avoidant": ["independent", "distance", "alone", "self-reliant"],
            "disorganized": ["confused", "conflicted", "unpredictable"]
        }
        
        style_scores = {style: 0 for style in attachment_indicators}
        
        # Analyze conversation content
        all_content = " ".join([msg.get("content", "") for msg in conversation_history]).lower()
        
        for style, indicators in attachment_indicators.items():
            for indicator in indicators:
                style_scores[style] += all_content.count(indicator)
        
        # Check pattern analysis for attachment-related patterns
        for pattern in pattern_analysis:
            description = pattern.get("description", "").lower()
            if "avoidance" in description or "distance" in description:
                style_scores["avoidant"] += 2
            elif "anxiety" in description or "worry" in description:
                style_scores["anxious"] += 2
            elif "volatility" in description or "unpredictable" in description:
                style_scores["disorganized"] += 2
        
        # Return style with highest score, default to secure
        max_style = max(style_scores, key=style_scores.get)
        return max_style if style_scores[max_style] > 0 else "secure"
    
    def _identify_coping_mechanisms(self, conversation_history: List[Dict[str, Any]],
                                  pattern_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify coping mechanisms from conversation"""
        coping_mechanisms = []
        
        # Common coping mechanism indicators
        coping_keywords = {
            "problem_solving": ["plan", "solve", "figure out", "strategy"],
            "social_support": ["talk to", "friends", "family", "support"],
            "avoidance": ["ignore", "avoid", "distract", "busy"],
            "emotional_expression": ["cry", "vent", "express", "share"],
            "self_care": ["exercise", "relax", "meditate", "sleep"],
            "substance_use": ["drink", "alcohol", "smoke", "drugs"]
        }
        
        all_content = " ".join([msg.get("content", "") for msg in conversation_history]).lower()
        
        for mechanism, keywords in coping_keywords.items():
            if any(keyword in all_content for keyword in keywords):
                coping_mechanisms.append(mechanism)
        
        return coping_mechanisms or ["unknown"]
    
    def _identify_emotional_triggers(self, conversation_history: List[Dict[str, Any]],
                                   pattern_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify emotional triggers"""
        triggers = []
        
        # Common trigger categories
        trigger_keywords = {
            "conflict": ["argument", "fight", "disagree", "conflict"],
            "criticism": ["criticize", "judge", "blame", "fault"],
            "abandonment": ["leave", "abandon", "alone", "reject"],
            "control": ["control", "manipulate", "force", "pressure"],
            "intimacy": ["close", "intimate", "vulnerable", "open"]
        }
        
        all_content = " ".join([msg.get("content", "") for msg in conversation_history]).lower()
        
        for trigger, keywords in trigger_keywords.items():
            if any(keyword in all_content for keyword in keywords):
                triggers.append(trigger)
        
        return triggers
    
    def _identify_emotional_strengths(self, conversation_history: List[Dict[str, Any]],
                                    pattern_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify emotional strengths"""
        strengths = []
        
        # Look for positive patterns
        for pattern in pattern_analysis:
            if pattern.get("severity") == "low" and "positive" in pattern.get("implications", []):
                if "engagement" in pattern.get("pattern_type", ""):
                    strengths.append("high_engagement")
                elif "communication" in pattern.get("pattern_type", ""):
                    strengths.append("good_communication")
        
        # Default strengths if none identified
        if not strengths:
            strengths = ["willingness_to_engage", "seeking_help"]
        
        return strengths
    
    def _identify_emotional_growth_areas(self, pattern_analysis: List[Dict[str, Any]]) -> List[str]:
        """Identify areas for emotional growth"""
        growth_areas = []
        
        for pattern in pattern_analysis:
            if pattern.get("severity") in ["medium", "high"]:
                pattern_type = pattern.get("pattern_type", "")
                if "emotional" in pattern_type:
                    growth_areas.append("emotional_regulation")
                elif "communication" in pattern_type:
                    growth_areas.append("communication_skills")
                elif "engagement" in pattern_type:
                    growth_areas.append("relationship_engagement")
        
        return list(set(growth_areas)) or ["general_relationship_skills"]
    
    # Additional helper methods
    def _initialize_diego_emotional_profile(self) -> Dict[str, Any]:
        """Initialize Diego's emotional characteristics"""
        return {
            "base_empathy": 0.85,
            "emotional_sensitivity": 0.8,
            "patience_level": 0.9,
            "warmth": 0.8,
            "understanding": 0.9,
            "emotional_stability": 0.85,
            "responsiveness": 0.8
        }
    
    def _load_psychological_frameworks(self) -> Dict[str, Any]:
        """Load psychological frameworks and models"""
        return {
            "attachment_theory": {
                "focus": "attachment patterns and relationship security",
                "techniques": ["attachment exploration", "security building"]
            },
            "cognitive_behavioral": {
                "focus": "thoughts, feelings, and behaviors",
                "techniques": ["cognitive restructuring", "behavioral experiments"]
            },
            "emotionally_focused": {
                "focus": "emotional awareness and expression",
                "techniques": ["emotion identification", "emotional processing"]
            }
        }
    
    def _load_therapeutic_techniques(self) -> Dict[str, Any]:
        """Load therapeutic techniques"""
        return {
            "validation": ["reflect emotions", "normalize experiences", "acknowledge struggles"],
            "reframing": ["alternative perspectives", "strength identification", "growth mindset"],
            "grounding": ["breathing exercises", "mindfulness", "present moment awareness"]
        }
    
    def _calculate_overall_confidence(self, output_data: Dict[str, Any]) -> float:
        """Calculate overall confidence for the layer output"""
        psychological_assessment = output_data.get("psychological_assessment", {})
        emotional_response = output_data.get("emotional_response", {})
        
        assessment_confidence = psychological_assessment.get("confidence", 0.7)
        response_confidence = emotional_response.get("confidence", 0.7)
        
        return (assessment_confidence + response_confidence) / 2
    
    # Additional helper methods for psychological assessment
    def _calculate_emotional_intensity(self, perception_result: Dict[str, Any],
                                     emotional_profile: EmotionalProfile) -> float:
        """Calculate current emotional intensity"""
        base_intensity = perception_result.get("emotional_intensity", 0.5)
        volatility_factor = emotional_profile.emotional_volatility
        
        # Adjust intensity based on volatility
        adjusted_intensity = base_intensity * (1 + volatility_factor * 0.3)
        return min(1.0, adjusted_intensity)
    
    def _assess_psychological_safety(self, conversation_context: Dict[str, Any],
                                   emotional_profile: EmotionalProfile) -> float:
        """Assess psychological safety level"""
        trust_score = conversation_context.get("trust_progression", [50])[-1] / 100.0
        openness_score = conversation_context.get("openness_progression", [30])[-1] / 100.0
        
        # Factor in emotional regulation
        regulation_factor = emotional_profile.emotional_regulation
        
        safety_score = (trust_score * 0.4 + openness_score * 0.3 + regulation_factor * 0.3)
        return min(1.0, max(0.0, safety_score))
    
    def _evaluate_stress_level(self, emotional_profile: EmotionalProfile,
                             insights: List[Dict[str, Any]],
                             perception_result: Dict[str, Any]) -> float:
        """Evaluate current stress level"""
        base_stress = 0.3  # Default moderate stress
        
        # Increase stress based on emotional volatility
        volatility_stress = emotional_profile.emotional_volatility * 0.4
        
        # Increase stress based on negative emotions
        negative_emotions = ["anxiety", "stress", "overwhelm", "frustration"]
        emotion_stress = 0.0
        for emotion in emotional_profile.primary_emotions:
            if emotion in negative_emotions:
                emotion_stress += 0.2
        
        # Factor in urgency from perception
        urgency_stress = perception_result.get("urgency", 0.0) * 0.3
        
        total_stress = base_stress + volatility_stress + emotion_stress + urgency_stress
        return min(1.0, total_stress)
    
    def _identify_resilience_indicators(self, emotional_profile: EmotionalProfile,
                                      conversation_context: Dict[str, Any]) -> List[str]:
        """Identify resilience indicators"""
        indicators = []
        
        if emotional_profile.emotional_regulation > 0.6:
            indicators.append("good_emotional_regulation")
        
        if emotional_profile.emotional_awareness > 0.6:
            indicators.append("emotional_self_awareness")
        
        if "problem_solving" in emotional_profile.coping_mechanisms:
            indicators.append("problem_solving_skills")
        
        if "social_support" in emotional_profile.coping_mechanisms:
            indicators.append("social_support_utilization")
        
        if len(conversation_context.get("conversation_history", [])) > 5:
            indicators.append("engagement_persistence")
        
        return indicators or ["basic_resilience"]
    
    def _identify_vulnerability_indicators(self, emotional_profile: EmotionalProfile,
                                         insights: List[Dict[str, Any]]) -> List[str]:
        """Identify vulnerability indicators"""
        indicators = []
        
        if emotional_profile.emotional_volatility > 0.7:
            indicators.append("emotional_volatility")
        
        if emotional_profile.emotional_regulation < 0.4:
            indicators.append("poor_emotional_regulation")
        
        if emotional_profile.attachment_style in ["anxious", "disorganized"]:
            indicators.append("insecure_attachment")
        
        if "substance_use" in emotional_profile.coping_mechanisms:
            indicators.append("maladaptive_coping")
        
        # Check insights for high-priority concerns
        high_priority_insights = [i for i in insights if i.get("priority") == "high"]
        if len(high_priority_insights) > 2:
            indicators.append("multiple_concerns")
        
        return indicators
    
    def _recommend_therapeutic_approach(self, emotional_profile: EmotionalProfile,
                                      dominant_emotions: List[str],
                                      stress_level: float) -> str:
        """Recommend therapeutic approach"""
        if stress_level > 0.7:
            return "stabilization_first"
        elif emotional_profile.attachment_style in ["anxious", "avoidant", "disorganized"]:
            return "attachment_focused"
        elif emotional_profile.emotional_regulation < 0.5:
            return "emotion_regulation_focused"
        elif "anxiety" in dominant_emotions or "worry" in dominant_emotions:
            return "anxiety_management"
        else:
            return "relationship_focused"
    
    def _select_therapeutic_model(self, emotional_profile: EmotionalProfile,
                                insights: List[Dict[str, Any]],
                                conversation_context: Dict[str, Any]) -> str:
        """Select appropriate therapeutic model"""
        if emotional_profile.attachment_style != "secure":
            return PsychologicalModel.ATTACHMENT_THEORY.value
        elif emotional_profile.emotional_regulation < 0.5:
            return PsychologicalModel.EMOTIONALLY_FOCUSED.value
        elif any("communication" in i.get("type", "") for i in insights):
            return PsychologicalModel.GOTTMAN_METHOD.value
        else:
            return PsychologicalModel.COGNITIVE_BEHAVIORAL.value
    
    def _calculate_assessment_confidence(self, emotional_profile: EmotionalProfile,
                                       conversation_length: int) -> float:
        """Calculate confidence in psychological assessment"""
        base_confidence = 0.6
        
        # Increase confidence with more conversation data
        length_factor = min(0.3, conversation_length * 0.02)
        
        # Increase confidence if clear patterns emerge
        pattern_clarity = 0.1 if emotional_profile.emotional_volatility > 0.7 or emotional_profile.emotional_volatility < 0.3 else 0.05
        
        total_confidence = base_confidence + length_factor + pattern_clarity
        return min(1.0, total_confidence)
    
    # Methods for emotional response generation
    def _determine_response_type(self, psychological_assessment: PsychologicalAssessment,
                               emotional_profile: EmotionalProfile) -> str:
        """Determine appropriate response type"""
        if psychological_assessment.stress_level > 0.7:
            return EmotionalResponse.SUPPORT.value
        elif psychological_assessment.psychological_safety < 0.5:
            return EmotionalResponse.VALIDATION.value
        elif "sadness" in psychological_assessment.dominant_emotions:
            return EmotionalResponse.REFLECTION.value
        elif emotional_profile.emotional_awareness < 0.5:
            return EmotionalResponse.NORMALIZE.value
        else:
            return EmotionalResponse.ENCOURAGE.value
    
    def _determine_emotional_tone(self, dominant_emotions: List[str],
                                psychological_safety: float) -> str:
        """Determine appropriate emotional tone"""
        if psychological_safety < 0.4:
            return "gentle_supportive"
        elif "anxiety" in dominant_emotions or "worry" in dominant_emotions:
            return "calm_reassuring"
        elif "sadness" in dominant_emotions or "grief" in dominant_emotions:
            return "compassionate_understanding"
        elif "anger" in dominant_emotions or "frustration" in dominant_emotions:
            return "patient_validating"
        else:
            return "warm_encouraging"
    
    def _calculate_empathy_level(self, psychological_assessment: PsychologicalAssessment,
                               emotional_profile: EmotionalProfile) -> float:
        """Calculate appropriate empathy level"""
        base_empathy = self.empathy_sensitivity
        
        # Increase empathy for vulnerable states
        if psychological_assessment.stress_level > 0.6:
            base_empathy += 0.1
        
        if psychological_assessment.psychological_safety < 0.5:
            base_empathy += 0.1
        
        if emotional_profile.emotional_volatility > 0.7:
            base_empathy += 0.05
        
        return min(1.0, base_empathy)
    
    def _generate_validation_elements(self, dominant_emotions: List[str],
                                    emotional_profile: EmotionalProfile) -> List[str]:
        """Generate validation elements"""
        validations = []
        
        for emotion in dominant_emotions[:2]:  # Top 2 emotions
            if emotion == "sadness":
                validations.append("It's completely understandable to feel sad about this situation")
            elif emotion == "anxiety":
                validations.append("Your anxiety makes perfect sense given what you're experiencing")
            elif emotion == "anger":
                validations.append("Your anger is a valid response to feeling hurt or frustrated")
            elif emotion == "frustration":
                validations.append("It's natural to feel frustrated when things aren't going as hoped")
            else:
                validations.append(f"Your feelings of {emotion} are completely valid")
        
        # Add general validation
        validations.append("Your emotions are important and deserve to be heard")
        
        return validations[:3]  # Limit to 3 validations
    
    def _generate_reframing_suggestions(self, psychological_assessment: PsychologicalAssessment,
                                      emotional_profile: EmotionalProfile) -> List[str]:
        """Generate reframing suggestions"""
        suggestions = []
        
        if psychological_assessment.stress_level > 0.6:
            suggestions.append("This challenging time could be an opportunity for growth and learning")
        
        if "hopelessness" in psychological_assessment.dominant_emotions:
            suggestions.append("Even small steps forward can lead to meaningful change")
        
        if emotional_profile.emotional_volatility > 0.6:
            suggestions.append("Your emotional sensitivity can be a strength in building deeper connections")
        
        # Default reframing
        suggestions.append("Every relationship challenge is a chance to build stronger communication skills")
        
        return suggestions[:2]  # Limit to 2 suggestions
    
    def _generate_supportive_statements(self, emotional_tone: str,
                                      psychological_assessment: PsychologicalAssessment) -> List[str]:
        """Generate supportive statements"""
        statements = []
        
        if emotional_tone == "gentle_supportive":
            statements.extend([
                "I'm here to support you through this",
                "You're taking a brave step by reaching out",
                "We can work through this together at your pace"
            ])
        elif emotional_tone == "calm_reassuring":
            statements.extend([
                "Take a deep breath - we'll figure this out together",
                "It's okay to feel uncertain; that's part of the process",
                "You have more strength than you realize"
            ])
        elif emotional_tone == "compassionate_understanding":
            statements.extend([
                "I can hear how much pain you're in right now",
                "Your feelings are so important and valid",
                "It takes courage to be vulnerable about your struggles"
            ])
        else:
            statements.extend([
                "You're doing important work by being here",
                "I believe in your ability to create positive change",
                "Every step you take matters"
            ])
        
        return statements[:3]  # Limit to 3 statements
    
    def _determine_diego_emotional_state(self, psychological_assessment: PsychologicalAssessment,
                                       emotional_tone: str) -> str:
        """Determine Diego's emotional state"""
        if psychological_assessment.stress_level > 0.7:
            return EmotionalState.CONCERNED.value
        elif psychological_assessment.psychological_safety < 0.5:
            return EmotionalState.GENTLE.value
        elif "sadness" in psychological_assessment.dominant_emotions:
            return EmotionalState.EMPATHETIC.value
        elif "anxiety" in psychological_assessment.dominant_emotions:
            return EmotionalState.CALM.value
        else:
            return EmotionalState.SUPPORTIVE.value
    
    def _get_attachment_recommendations(self, attachment_style: str) -> List[str]:
        """Get recommendations based on attachment style"""
        recommendations = {
            "anxious": [
                "Practice self-soothing techniques",
                "Work on building secure base within yourself",
                "Explore fears of abandonment"
            ],
            "avoidant": [
                "Practice emotional expression",
                "Explore benefits of emotional intimacy",
                "Work on trust-building gradually"
            ],
            "disorganized": [
                "Focus on emotional regulation skills",
                "Build consistent, safe relationships",
                "Process past relationship experiences"
            ]
        }
        return recommendations.get(attachment_style, ["Continue building secure attachment patterns"])
    
    def _generate_safety_cautions(self, psychological_assessment: PsychologicalAssessment) -> List[str]:
        """Generate safety cautions"""
        cautions = []
        
        if psychological_assessment.stress_level > 0.8:
            cautions.append("High stress level - proceed with extra gentleness")
        
        if psychological_assessment.psychological_safety < 0.3:
            cautions.append("Low psychological safety - focus on trust building first")
        
        if "overwhelm" in psychological_assessment.dominant_emotions:
            cautions.append("User may be overwhelmed - simplify and slow down")
        
        return cautions
    
    def _generate_safety_green_lights(self, psychological_assessment: PsychologicalAssessment) -> List[str]:
        """Generate safety green lights"""
        green_lights = []
        
        if psychological_assessment.psychological_safety > 0.7:
            green_lights.append("Good psychological safety - can explore deeper topics")
        
        if psychological_assessment.stress_level < 0.4:
            green_lights.append("Low stress level - good time for growth work")
        
        if len(psychological_assessment.resilience_indicators) > 2:
            green_lights.append("Multiple resilience indicators - user has good coping resources")
        
        return green_lights

# Helper classes
class EmotionDetector:
    """Detects and analyzes emotions"""
    pass

class EmpathyEngine:
    """Generates empathetic responses"""
    pass

class PsychologicalAssessor:
    """Conducts psychological assessments"""
    pass

class TherapeuticAdvisor:
    """Provides therapeutic recommendations"""
    pass