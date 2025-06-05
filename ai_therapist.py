#!/usr/bin/env python3
"""
AI Therapist Module
Core AI intelligence for relationship therapy and guidance
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
# import numpy as np  # Not available in minimal setup
from pathlib import Path

# Heavy AI and ML libraries not available in minimal setup
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
# import openai
# from anthropic import Anthropic
# import google.generativeai as genai

# Heavy text processing dependencies not available in minimal setup
# from textblob import TextBlob
# import spacy
# from sentence_transformers import SentenceTransformer

# Local imports
from conversation_analyzer import ConversationAnalyzer, AnalysisResult
from knowledge_base import KnowledgeBase
from data_processor import DataProcessor
from real_time_monitor import RealTimeMonitor

logger = logging.getLogger(__name__)

class TherapyApproach(Enum):
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    EMOTIONALLY_FOCUSED = "emotionally_focused"
    GOTTMAN_METHOD = "gottman_method"
    SOLUTION_FOCUSED = "solution_focused"
    NARRATIVE_THERAPY = "narrative_therapy"
    SYSTEMIC_THERAPY = "systemic_therapy"

class InterventionType(Enum):
    IMMEDIATE_RESPONSE = "immediate_response"
    COMMUNICATION_COACHING = "communication_coaching"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMOTIONAL_REGULATION = "emotional_regulation"
    RELATIONSHIP_BUILDING = "relationship_building"
    BOUNDARY_SETTING = "boundary_setting"

@dataclass
class TherapeuticInsight:
    insight_id: str
    user_id: str
    insight_type: str
    content: str
    confidence_score: float
    supporting_evidence: List[str]
    recommendations: List[str]
    therapy_approach: str
    created_at: datetime
    priority: str  # high, medium, low
    actionable_steps: List[str]
    expected_outcomes: List[str]

@dataclass
class TherapeuticIntervention:
    intervention_id: str
    user_id: str
    intervention_type: str
    trigger_context: Dict[str, Any]
    recommended_actions: List[str]
    scripts: List[str]
    timing: str  # immediate, within_hour, within_day
    success_metrics: List[str]
    follow_up_actions: List[str]
    created_at: datetime

@dataclass
class UserTherapyProfile:
    user_id: str
    personality_traits: Dict[str, float]
    communication_style: str
    attachment_style: str
    relationship_goals: List[str]
    therapy_preferences: Dict[str, Any]
    progress_metrics: Dict[str, float]
    session_history: List[Dict[str, Any]]
    last_updated: datetime

class AITherapist:
    def __init__(self, conversation_analyzer: ConversationAnalyzer = None,
                 knowledge_base: KnowledgeBase = None,
                 data_processor: DataProcessor = None,
                 real_time_monitor: RealTimeMonitor = None):
        
        self.conversation_analyzer = conversation_analyzer
        self.knowledge_base = knowledge_base
        self.data_processor = data_processor
        self.real_time_monitor = real_time_monitor
        
        # AI Models
        self.llm_client = None
        self.embedding_model = None
        self.emotion_classifier = None
        self.personality_analyzer = None
        
        # User profiles and session data
        self.user_profiles: Dict[str, UserTherapyProfile] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.intervention_history: Dict[str, List[TherapeuticIntervention]] = {}
        
        # Therapy frameworks and approaches
        self.therapy_frameworks = self._initialize_therapy_frameworks()
        self.intervention_strategies = self._initialize_intervention_strategies()
        
        # Initialize AI components
        self._initialize_ai_models()
        
        logger.info("AI Therapist initialized")
    
    def _initialize_ai_models(self):
        """
        Initialize AI models and clients
        """
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize emotion classifier
            try:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    return_all_scores=True
                )
            except Exception as e:
                logger.warning(f"Could not load emotion classifier: {str(e)}")
            
            # Initialize personality analyzer
            try:
                self.personality_analyzer = pipeline(
                    "text-classification",
                    model="martin-ha/toxic-comment-model"
                )
            except Exception as e:
                logger.warning(f"Could not load personality analyzer: {str(e)}")
            
            # Initialize LLM client (placeholder - configure with your preferred LLM)
            # self.llm_client = openai.OpenAI(api_key="your-api-key")
            # self.anthropic_client = Anthropic(api_key="your-api-key")
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
    
    def _initialize_therapy_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize therapy frameworks and methodologies
        """
        frameworks = {
            TherapyApproach.COGNITIVE_BEHAVIORAL.value: {
                "description": "Focus on identifying and changing negative thought patterns and behaviors",
                "techniques": [
                    "thought_challenging",
                    "behavioral_experiments",
                    "cognitive_restructuring",
                    "mindfulness_exercises"
                ],
                "assessment_areas": [
                    "automatic_thoughts",
                    "cognitive_distortions",
                    "behavioral_patterns",
                    "emotional_responses"
                ]
            },
            TherapyApproach.EMOTIONALLY_FOCUSED.value: {
                "description": "Focus on emotional awareness, expression, and attachment patterns",
                "techniques": [
                    "emotion_identification",
                    "attachment_exploration",
                    "emotional_expression",
                    "empathy_building"
                ],
                "assessment_areas": [
                    "emotional_awareness",
                    "attachment_style",
                    "emotional_regulation",
                    "intimacy_patterns"
                ]
            },
            TherapyApproach.GOTTMAN_METHOD.value: {
                "description": "Research-based approach focusing on relationship dynamics and communication",
                "techniques": [
                    "four_horsemen_assessment",
                    "love_maps",
                    "conflict_resolution",
                    "positive_sentiment_override"
                ],
                "assessment_areas": [
                    "communication_patterns",
                    "conflict_styles",
                    "emotional_connection",
                    "relationship_satisfaction"
                ]
            },
            TherapyApproach.SOLUTION_FOCUSED.value: {
                "description": "Focus on solutions and strengths rather than problems",
                "techniques": [
                    "miracle_question",
                    "scaling_questions",
                    "exception_finding",
                    "strength_identification"
                ],
                "assessment_areas": [
                    "existing_strengths",
                    "successful_strategies",
                    "goal_clarity",
                    "motivation_levels"
                ]
            }
        }
        
        return frameworks
    
    def _initialize_intervention_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize intervention strategies for different situations
        """
        strategies = {
            InterventionType.IMMEDIATE_RESPONSE.value: {
                "description": "Immediate guidance for ongoing conversations",
                "triggers": [
                    "high_conflict_detected",
                    "emotional_escalation",
                    "communication_breakdown",
                    "opportunity_for_connection"
                ],
                "response_types": [
                    "de_escalation",
                    "empathy_building",
                    "clarification_request",
                    "positive_reframing"
                ]
            },
            InterventionType.COMMUNICATION_COACHING.value: {
                "description": "Coaching for better communication skills",
                "focus_areas": [
                    "active_listening",
                    "assertive_communication",
                    "emotional_expression",
                    "nonviolent_communication"
                ],
                "techniques": [
                    "i_statements",
                    "reflective_listening",
                    "validation_techniques",
                    "boundary_setting"
                ]
            },
            InterventionType.CONFLICT_RESOLUTION.value: {
                "description": "Strategies for resolving relationship conflicts",
                "stages": [
                    "de_escalation",
                    "understanding_perspectives",
                    "finding_common_ground",
                    "solution_generation",
                    "agreement_implementation"
                ],
                "tools": [
                    "perspective_taking",
                    "compromise_strategies",
                    "win_win_solutions",
                    "repair_attempts"
                ]
            }
        }
        
        return strategies
    
    async def analyze_user_conversation(self, user_id: str, conversation_data: str,
                                      analysis_type: str = "comprehensive") -> TherapeuticInsight:
        """
        Analyze user conversation and provide therapeutic insights
        """
        try:
            # Get or create user profile
            user_profile = await self.get_user_profile(user_id)
            
            # Perform conversation analysis
            if self.conversation_analyzer:
                analysis_result = await self.conversation_analyzer.analyze_comprehensive(
                    conversation_data, user_id
                )
            else:
                # Fallback analysis
                analysis_result = await self._fallback_analysis(conversation_data)
            
            # Get relevant knowledge base context
            context = {}
            if self.knowledge_base:
                context = await self.knowledge_base.get_context_for_analysis(
                    analysis_type, {"user_id": user_id, "conversation": conversation_data}
                )
            
            # Generate therapeutic insights
            insight = await self._generate_therapeutic_insight(
                user_id, analysis_result, context, user_profile
            )
            
            # Update user profile based on insights
            await self._update_user_profile_from_analysis(user_id, analysis_result, insight)
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing user conversation: {str(e)}")
            raise
    
    async def generate_real_time_intervention(self, user_id: str, current_message: str,
                                            conversation_context: Dict[str, Any]) -> TherapeuticIntervention:
        """
        Generate real-time therapeutic intervention
        """
        try:
            # Analyze current message for emotional state and communication patterns
            message_analysis = await self._analyze_message_urgency(current_message)
            
            # Get user profile for personalized intervention
            user_profile = await self.get_user_profile(user_id)
            
            # Determine intervention type based on analysis
            intervention_type = await self._determine_intervention_type(
                message_analysis, conversation_context, user_profile
            )
            
            # Generate specific intervention
            intervention = await self._generate_intervention(
                user_id, intervention_type, current_message, conversation_context, user_profile
            )
            
            # Store intervention for tracking
            if user_id not in self.intervention_history:
                self.intervention_history[user_id] = []
            self.intervention_history[user_id].append(intervention)
            
            return intervention
            
        except Exception as e:
            logger.error(f"Error generating real-time intervention: {str(e)}")
            raise
    
    async def provide_communication_coaching(self, user_id: str, communication_issue: str,
                                           relationship_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide communication coaching based on specific issues
        """
        try:
            # Analyze the communication issue
            issue_analysis = await self._analyze_communication_issue(communication_issue)
            
            # Get user profile and communication style
            user_profile = await self.get_user_profile(user_id)
            
            # Get relevant coaching strategies from knowledge base
            coaching_context = {}
            if self.knowledge_base:
                coaching_context = await self.knowledge_base.search(
                    query=f"communication coaching {issue_analysis['issue_type']}",
                    document_types=["guidance", "instruction"],
                    limit=5
                )
            
            # Generate personalized coaching advice
            coaching_advice = await self._generate_communication_coaching(
                user_id, issue_analysis, relationship_context, user_profile, coaching_context
            )
            
            return coaching_advice
            
        except Exception as e:
            logger.error(f"Error providing communication coaching: {str(e)}")
            raise
    
    async def assess_relationship_health(self, user_id: str, 
                                       conversation_history: List[str]) -> Dict[str, Any]:
        """
        Assess overall relationship health based on conversation patterns
        """
        try:
            # Analyze conversation patterns over time
            health_metrics = {
                "communication_quality": 0.0,
                "emotional_connection": 0.0,
                "conflict_resolution": 0.0,
                "trust_indicators": 0.0,
                "growth_potential": 0.0,
                "overall_health": 0.0
            }
            
            # Analyze each conversation for health indicators
            for conversation in conversation_history:
                if self.conversation_analyzer:
                    analysis = await self.conversation_analyzer.analyze_comprehensive(
                        conversation, user_id
                    )
                    
                    # Update health metrics based on analysis
                    health_metrics["communication_quality"] += analysis.metrics.communication_effectiveness
                    health_metrics["emotional_connection"] += analysis.metrics.emotional_intelligence_score
                    health_metrics["conflict_resolution"] += analysis.metrics.conflict_resolution_score
            
            # Calculate averages
            num_conversations = len(conversation_history)
            if num_conversations > 0:
                for metric in health_metrics:
                    if metric != "overall_health":
                        health_metrics[metric] /= num_conversations
            
            # Calculate overall health score
            health_metrics["overall_health"] = np.mean([
                health_metrics["communication_quality"],
                health_metrics["emotional_connection"],
                health_metrics["conflict_resolution"],
                health_metrics["trust_indicators"],
                health_metrics["growth_potential"]
            ])
            
            # Generate health assessment report
            health_report = await self._generate_health_assessment_report(
                user_id, health_metrics, conversation_history
            )
            
            return {
                "metrics": health_metrics,
                "report": health_report,
                "recommendations": await self._generate_health_recommendations(health_metrics),
                "assessment_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing relationship health: {str(e)}")
            raise
    
    async def generate_analysis_report(self, user_id: str, report_type: str, 
                                     time_period: str = "last_week") -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        """
        try:
            # Get user profile and session history
            user_profile = await self.get_user_profile(user_id)
            
            # Calculate time range
            end_date = datetime.now()
            if time_period == "last_week":
                start_date = end_date - timedelta(weeks=1)
            elif time_period == "last_month":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_3_months":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(weeks=1)
            
            # Get relevant data for the time period
            session_data = self._get_session_data_for_period(user_id, start_date, end_date)
            
            # Generate report based on type
            if report_type == "relationship_health":
                report = await self._generate_relationship_health_report(
                    user_id, session_data, user_profile
                )
            elif report_type == "communication_patterns":
                report = await self._generate_communication_patterns_report(
                    user_id, session_data, user_profile
                )
            elif report_type == "compatibility_analysis":
                report = await self._generate_compatibility_analysis_report(
                    user_id, session_data, user_profile
                )
            elif report_type == "progress_report":
                report = await self._generate_progress_report(
                    user_id, session_data, user_profile
                )
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Add metadata
            report["metadata"] = {
                "user_id": user_id,
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": datetime.now().isoformat(),
                "data_points": len(session_data)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: str) -> UserTherapyProfile:
        """
        Get or create user therapy profile
        """
        if user_id not in self.user_profiles:
            # Create new profile
            self.user_profiles[user_id] = UserTherapyProfile(
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
                progress_metrics={},
                session_history=[],
                last_updated=datetime.now()
            )
        
        return self.user_profiles[user_id]
    
    async def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]) -> bool:
        """
        Update user therapy profile
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update profile fields
            for key, value in profile_updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.last_updated = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    async def _generate_therapeutic_insight(self, user_id: str, analysis_result: AnalysisResult,
                                          context: Dict[str, Any], 
                                          user_profile: UserTherapyProfile) -> TherapeuticInsight:
        """
        Generate therapeutic insight from analysis
        """
        try:
            # Determine primary insight type based on analysis
            insight_type = self._determine_insight_type(analysis_result)
            
            # Generate insight content using AI or rule-based approach
            insight_content = await self._generate_insight_content(
                analysis_result, context, user_profile, insight_type
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                analysis_result, user_profile, insight_type
            )
            
            # Determine therapy approach
            therapy_approach = self._select_therapy_approach(analysis_result, user_profile)
            
            # Create insight object
            insight = TherapeuticInsight(
                insight_id=f"insight_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                insight_type=insight_type,
                content=insight_content,
                confidence_score=analysis_result.confidence_score,
                supporting_evidence=self._extract_supporting_evidence(analysis_result),
                recommendations=recommendations,
                therapy_approach=therapy_approach,
                created_at=datetime.now(),
                priority=self._determine_priority(analysis_result),
                actionable_steps=await self._generate_actionable_steps(recommendations),
                expected_outcomes=await self._generate_expected_outcomes(recommendations)
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generating therapeutic insight: {str(e)}")
            raise
    
    async def _generate_intervention(self, user_id: str, intervention_type: str,
                                   current_message: str, conversation_context: Dict[str, Any],
                                   user_profile: UserTherapyProfile) -> TherapeuticIntervention:
        """
        Generate specific therapeutic intervention
        """
        try:
            # Get intervention strategy
            strategy = self.intervention_strategies.get(intervention_type, {})
            
            # Generate recommended actions based on intervention type
            recommended_actions = await self._generate_intervention_actions(
                intervention_type, current_message, conversation_context, user_profile
            )
            
            # Generate conversation scripts
            scripts = await self._generate_conversation_scripts(
                intervention_type, current_message, user_profile
            )
            
            # Determine timing
            timing = self._determine_intervention_timing(current_message, conversation_context)
            
            # Create intervention object
            intervention = TherapeuticIntervention(
                intervention_id=f"intervention_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                intervention_type=intervention_type,
                trigger_context={
                    "current_message": current_message,
                    "conversation_context": conversation_context,
                    "timestamp": datetime.now().isoformat()
                },
                recommended_actions=recommended_actions,
                scripts=scripts,
                timing=timing,
                success_metrics=strategy.get("success_metrics", []),
                follow_up_actions=await self._generate_follow_up_actions(intervention_type),
                created_at=datetime.now()
            )
            
            return intervention
            
        except Exception as e:
            logger.error(f"Error generating intervention: {str(e)}")
            raise
    
    async def _fallback_analysis(self, conversation_data: str) -> AnalysisResult:
        """
        Fallback analysis when conversation analyzer is not available
        """
        # Simple text analysis
        blob = TextBlob(conversation_data)
        sentiment = blob.sentiment
        
        # Create basic analysis result
        from conversation_analyzer import ConversationMetrics
        
        metrics = ConversationMetrics(
            total_messages=len(conversation_data.split('\n')),
            average_message_length=len(conversation_data) / max(len(conversation_data.split('\n')), 1),
            sentiment_score=sentiment.polarity,
            emotional_intelligence_score=0.5,
            communication_effectiveness=0.5,
            conflict_resolution_score=0.5,
            empathy_indicators=0.5,
            active_listening_score=0.5,
            response_time_analysis={},
            topic_coherence=0.5,
            relationship_stage_indicators={}
        )
        
        return AnalysisResult(
            analysis_id=f"fallback_{datetime.now().timestamp()}",
            user_id="unknown",
            analysis_type="basic",
            metrics=metrics,
            insights=["Basic sentiment analysis performed"],
            recommendations=["Consider using full conversation analyzer for detailed insights"],
            emotional_patterns={"overall_sentiment": sentiment.polarity},
            communication_patterns={"basic_analysis": True},
            red_flags=[],
            positive_indicators=[],
            confidence_score=0.3,
            created_at=datetime.now()
        )
    
    def _determine_insight_type(self, analysis_result: AnalysisResult) -> str:
        """
        Determine the primary insight type from analysis
        """
        # Simple rule-based approach
        if analysis_result.red_flags:
            return "warning"
        elif analysis_result.metrics.emotional_intelligence_score < 0.3:
            return "emotional_development"
        elif analysis_result.metrics.communication_effectiveness < 0.3:
            return "communication_improvement"
        elif analysis_result.metrics.conflict_resolution_score < 0.3:
            return "conflict_resolution"
        else:
            return "relationship_enhancement"
    
    async def _generate_insight_content(self, analysis_result: AnalysisResult,
                                      context: Dict[str, Any], user_profile: UserTherapyProfile,
                                      insight_type: str) -> str:
        """
        Generate insight content using AI or templates
        """
        # Template-based approach (can be enhanced with LLM)
        templates = {
            "warning": "Based on the conversation analysis, there are some concerning patterns that need attention: {red_flags}. It's important to address these issues to maintain a healthy relationship.",
            "emotional_development": "The analysis shows opportunities for emotional growth. Your emotional intelligence score is {ei_score:.2f}, which suggests room for improvement in emotional awareness and expression.",
            "communication_improvement": "Your communication effectiveness score is {comm_score:.2f}. This indicates there are opportunities to enhance how you express yourself and connect with your partner.",
            "conflict_resolution": "The analysis reveals a conflict resolution score of {conflict_score:.2f}. Developing better conflict resolution skills could significantly improve your relationship dynamics.",
            "relationship_enhancement": "Your relationship shows positive indicators: {positive_indicators}. Building on these strengths can lead to even deeper connection and satisfaction."
        }
        
        template = templates.get(insight_type, "General relationship insights based on conversation analysis.")
        
        # Format template with analysis data
        try:
            content = template.format(
                red_flags=", ".join(analysis_result.red_flags),
                positive_indicators=", ".join(analysis_result.positive_indicators),
                ei_score=analysis_result.metrics.emotional_intelligence_score,
                comm_score=analysis_result.metrics.communication_effectiveness,
                conflict_score=analysis_result.metrics.conflict_resolution_score
            )
        except KeyError:
            content = template
        
        return content
    
    async def _generate_recommendations(self, analysis_result: AnalysisResult,
                                      user_profile: UserTherapyProfile, 
                                      insight_type: str) -> List[str]:
        """
        Generate specific recommendations based on analysis
        """
        recommendations = []
        
        # Rule-based recommendations
        if analysis_result.metrics.emotional_intelligence_score < 0.5:
            recommendations.append("Practice emotional awareness exercises daily")
            recommendations.append("Use 'I' statements to express feelings")
        
        if analysis_result.metrics.communication_effectiveness < 0.5:
            recommendations.append("Practice active listening techniques")
            recommendations.append("Ask clarifying questions before responding")
        
        if analysis_result.metrics.conflict_resolution_score < 0.5:
            recommendations.append("Take breaks during heated discussions")
            recommendations.append("Focus on finding solutions rather than blame")
        
        if analysis_result.red_flags:
            recommendations.append("Consider seeking professional relationship counseling")
            recommendations.append("Address concerning patterns immediately")
        
        # Add positive reinforcement
        if analysis_result.positive_indicators:
            recommendations.append(f"Continue building on your strengths: {', '.join(analysis_result.positive_indicators[:2])}")
        
        return recommendations
    
    def _select_therapy_approach(self, analysis_result: AnalysisResult, 
                               user_profile: UserTherapyProfile) -> str:
        """
        Select appropriate therapy approach based on analysis
        """
        # Simple rule-based selection
        if analysis_result.metrics.emotional_intelligence_score < 0.3:
            return TherapyApproach.EMOTIONALLY_FOCUSED.value
        elif analysis_result.metrics.communication_effectiveness < 0.3:
            return TherapyApproach.GOTTMAN_METHOD.value
        elif analysis_result.red_flags:
            return TherapyApproach.COGNITIVE_BEHAVIORAL.value
        else:
            return TherapyApproach.SOLUTION_FOCUSED.value
    
    def _extract_supporting_evidence(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Extract supporting evidence from analysis
        """
        evidence = []
        
        if analysis_result.insights:
            evidence.extend(analysis_result.insights[:3])
        
        if analysis_result.emotional_patterns:
            evidence.append(f"Emotional patterns: {list(analysis_result.emotional_patterns.keys())[:3]}")
        
        if analysis_result.communication_patterns:
            evidence.append(f"Communication patterns: {list(analysis_result.communication_patterns.keys())[:3]}")
        
        return evidence
    
    def _determine_priority(self, analysis_result: AnalysisResult) -> str:
        """
        Determine priority level of insight
        """
        if analysis_result.red_flags:
            return "high"
        elif (analysis_result.metrics.emotional_intelligence_score < 0.3 or 
              analysis_result.metrics.communication_effectiveness < 0.3):
            return "medium"
        else:
            return "low"
    
    async def _generate_actionable_steps(self, recommendations: List[str]) -> List[str]:
        """
        Generate specific actionable steps from recommendations
        """
        actionable_steps = []
        
        for recommendation in recommendations:
            if "emotional awareness" in recommendation.lower():
                actionable_steps.append("Set aside 10 minutes daily for emotion journaling")
                actionable_steps.append("Practice naming emotions as they arise")
            elif "active listening" in recommendation.lower():
                actionable_steps.append("Maintain eye contact during conversations")
                actionable_steps.append("Summarize what you heard before responding")
            elif "conflict resolution" in recommendation.lower():
                actionable_steps.append("Use the 24-hour rule before discussing heated topics")
                actionable_steps.append("Practice the XYZ formula: 'In situation X, when you do Y, I feel Z'")
        
        return actionable_steps
    
    async def _generate_expected_outcomes(self, recommendations: List[str]) -> List[str]:
        """
        Generate expected outcomes from following recommendations
        """
        outcomes = [
            "Improved emotional connection with partner",
            "Reduced frequency and intensity of conflicts",
            "Better understanding of each other's needs",
            "Increased relationship satisfaction",
            "Enhanced communication skills"
        ]
        
        return outcomes[:3]  # Return top 3 expected outcomes
    
    async def _analyze_message_urgency(self, message: str) -> Dict[str, Any]:
        """
        Analyze message for urgency and emotional state
        """
        analysis = {
            "urgency_level": "low",
            "emotional_state": "neutral",
            "intervention_needed": False,
            "key_indicators": []
        }
        
        # Simple keyword-based analysis
        urgent_keywords = ["angry", "furious", "hate", "never", "always", "done", "over"]
        emotional_keywords = ["hurt", "sad", "frustrated", "confused", "scared"]
        
        message_lower = message.lower()
        
        # Check for urgent indicators
        for keyword in urgent_keywords:
            if keyword in message_lower:
                analysis["urgency_level"] = "high"
                analysis["intervention_needed"] = True
                analysis["key_indicators"].append(f"urgent_keyword: {keyword}")
        
        # Check for emotional indicators
        for keyword in emotional_keywords:
            if keyword in message_lower:
                analysis["emotional_state"] = "distressed"
                analysis["key_indicators"].append(f"emotional_keyword: {keyword}")
        
        # Use AI emotion classifier if available
        if self.emotion_classifier:
            try:
                emotions = self.emotion_classifier(message)
                if emotions:
                    top_emotion = max(emotions[0], key=lambda x: x['score'])
                    analysis["emotional_state"] = top_emotion['label']
                    analysis["key_indicators"].append(f"ai_emotion: {top_emotion['label']}")
            except Exception as e:
                logger.warning(f"Error in emotion classification: {str(e)}")
        
        return analysis
    
    async def _determine_intervention_type(self, message_analysis: Dict[str, Any],
                                         conversation_context: Dict[str, Any],
                                         user_profile: UserTherapyProfile) -> str:
        """
        Determine the type of intervention needed
        """
        if message_analysis["urgency_level"] == "high":
            return InterventionType.IMMEDIATE_RESPONSE.value
        elif message_analysis["emotional_state"] == "distressed":
            return InterventionType.EMOTIONAL_REGULATION.value
        elif "conflict" in str(conversation_context).lower():
            return InterventionType.CONFLICT_RESOLUTION.value
        else:
            return InterventionType.COMMUNICATION_COACHING.value
    
    async def _generate_intervention_actions(self, intervention_type: str, current_message: str,
                                           conversation_context: Dict[str, Any],
                                           user_profile: UserTherapyProfile) -> List[str]:
        """
        Generate specific intervention actions
        """
        actions = []
        
        if intervention_type == InterventionType.IMMEDIATE_RESPONSE.value:
            actions = [
                "Take a deep breath before responding",
                "Acknowledge your partner's feelings",
                "Use a calm, non-defensive tone",
                "Focus on understanding rather than being right"
            ]
        elif intervention_type == InterventionType.EMOTIONAL_REGULATION.value:
            actions = [
                "Validate your own emotions first",
                "Use 'I feel' statements",
                "Ask for what you need clearly",
                "Take a break if emotions are too intense"
            ]
        elif intervention_type == InterventionType.CONFLICT_RESOLUTION.value:
            actions = [
                "Identify the core issue beneath the conflict",
                "Listen to understand your partner's perspective",
                "Look for common ground",
                "Propose a specific solution"
            ]
        else:  # Communication coaching
            actions = [
                "Practice active listening",
                "Ask open-ended questions",
                "Reflect back what you heard",
                "Express appreciation for your partner"
            ]
        
        return actions
    
    async def _generate_conversation_scripts(self, intervention_type: str, current_message: str,
                                           user_profile: UserTherapyProfile) -> List[str]:
        """
        Generate conversation scripts for the intervention
        """
        scripts = []
        
        if intervention_type == InterventionType.IMMEDIATE_RESPONSE.value:
            scripts = [
                "I can see this is really important to you. Help me understand...",
                "I want to make sure I'm hearing you correctly. Are you saying...",
                "I care about how you're feeling. Can we talk about this?"
            ]
        elif intervention_type == InterventionType.EMOTIONAL_REGULATION.value:
            scripts = [
                "I'm feeling [emotion] right now, and I need [specific need].",
                "This is bringing up some strong feelings for me. Can we pause for a moment?",
                "I want to respond thoughtfully. Give me a moment to process this."
            ]
        elif intervention_type == InterventionType.CONFLICT_RESOLUTION.value:
            scripts = [
                "It seems like we both want [common goal]. How can we work together on this?",
                "I think I understand your concern about [issue]. My perspective is [perspective].",
                "What would need to happen for both of us to feel good about this?"
            ]
        else:  # Communication coaching
            scripts = [
                "Tell me more about that. I want to understand your experience.",
                "What I'm hearing is [reflection]. Is that right?",
                "I appreciate you sharing that with me. It helps me understand."
            ]
        
        return scripts
    
    def _determine_intervention_timing(self, current_message: str, 
                                     conversation_context: Dict[str, Any]) -> str:
        """
        Determine when the intervention should be applied
        """
        # Simple rule-based timing
        urgent_indicators = ["angry", "furious", "done", "over", "never", "always"]
        
        if any(indicator in current_message.lower() for indicator in urgent_indicators):
            return "immediate"
        elif "conflict" in str(conversation_context).lower():
            return "within_hour"
        else:
            return "within_day"
    
    async def _generate_follow_up_actions(self, intervention_type: str) -> List[str]:
        """
        Generate follow-up actions for the intervention
        """
        follow_ups = [
            "Check in with your partner about how the conversation went",
            "Reflect on what worked well and what could be improved",
            "Practice the suggested techniques in low-stakes conversations",
            "Schedule a follow-up discussion if needed"
        ]
        
        return follow_ups
    
    def _get_session_data_for_period(self, user_id: str, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get session data for a specific time period
        """
        # Placeholder implementation
        # In a real system, this would query a database
        user_profile = self.user_profiles.get(user_id)
        if user_profile:
            return [
                session for session in user_profile.session_history
                if start_date <= datetime.fromisoformat(session.get('timestamp', datetime.now().isoformat())) <= end_date
            ]
        return []
    
    async def _generate_relationship_health_report(self, user_id: str, session_data: List[Dict[str, Any]],
                                                 user_profile: UserTherapyProfile) -> Dict[str, Any]:
        """
        Generate relationship health report
        """
        report = {
            "title": "Relationship Health Assessment",
            "summary": "Overall relationship health analysis based on recent interactions",
            "health_score": 0.75,  # Placeholder
            "key_strengths": [
                "Good emotional awareness",
                "Effective conflict resolution",
                "Strong communication foundation"
            ],
            "areas_for_improvement": [
                "Increase frequency of positive interactions",
                "Develop better listening skills",
                "Practice expressing appreciation more often"
            ],
            "recommendations": [
                "Schedule weekly relationship check-ins",
                "Practice gratitude exercises together",
                "Consider couples therapy for additional support"
            ],
            "trend_analysis": {
                "communication_trend": "improving",
                "conflict_frequency": "stable",
                "emotional_connection": "strong"
            }
        }
        
        return report
    
    async def _generate_communication_patterns_report(self, user_id: str, session_data: List[Dict[str, Any]],
                                                    user_profile: UserTherapyProfile) -> Dict[str, Any]:
        """
        Generate communication patterns report
        """
        report = {
            "title": "Communication Patterns Analysis",
            "summary": "Analysis of communication styles and effectiveness",
            "communication_style": user_profile.communication_style,
            "effectiveness_score": 0.68,  # Placeholder
            "patterns_identified": [
                "Tendency to interrupt during emotional discussions",
                "Strong use of 'I' statements",
                "Good at asking clarifying questions"
            ],
            "improvement_areas": [
                "Active listening during conflicts",
                "Emotional regulation during stress",
                "Nonverbal communication awareness"
            ],
            "success_indicators": [
                "Increased use of validation techniques",
                "Reduced defensive responses",
                "Better timing of difficult conversations"
            ]
        }
        
        return report
    
    async def _generate_compatibility_analysis_report(self, user_id: str, session_data: List[Dict[str, Any]],
                                                    user_profile: UserTherapyProfile) -> Dict[str, Any]:
        """
        Generate compatibility analysis report
        """
        report = {
            "title": "Relationship Compatibility Analysis",
            "summary": "Assessment of compatibility factors and relationship dynamics",
            "compatibility_score": 0.72,  # Placeholder
            "compatible_areas": [
                "Shared values and life goals",
                "Complementary communication styles",
                "Similar conflict resolution approaches"
            ],
            "challenging_areas": [
                "Different emotional expression styles",
                "Varying needs for personal space",
                "Different approaches to decision-making"
            ],
            "growth_opportunities": [
                "Develop appreciation for differences",
                "Create compromise strategies",
                "Build on shared strengths"
            ]
        }
        
        return report
    
    async def _generate_progress_report(self, user_id: str, session_data: List[Dict[str, Any]],
                                      user_profile: UserTherapyProfile) -> Dict[str, Any]:
        """
        Generate progress report
        """
        report = {
            "title": "Relationship Progress Report",
            "summary": "Progress tracking and goal achievement analysis",
            "overall_progress": "positive",
            "goals_achieved": [
                "Improved active listening skills",
                "Reduced frequency of arguments",
                "Increased emotional intimacy"
            ],
            "goals_in_progress": [
                "Better conflict resolution",
                "More frequent quality time",
                "Enhanced emotional expression"
            ],
            "next_steps": [
                "Continue practicing communication techniques",
                "Set new relationship goals",
                "Maintain progress momentum"
            ],
            "metrics_improvement": {
                "communication_effectiveness": "+15%",
                "emotional_intelligence": "+12%",
                "conflict_resolution": "+8%"
            }
        }
        
        return report
    
    async def _analyze_communication_issue(self, communication_issue: str) -> Dict[str, Any]:
        """
        Analyze a specific communication issue
        """
        analysis = {
            "issue_type": "general",
            "severity": "medium",
            "root_causes": [],
            "impact_areas": [],
            "intervention_priority": "medium"
        }
        
        # Simple keyword-based analysis
        issue_lower = communication_issue.lower()
        
        if any(word in issue_lower for word in ["listen", "hearing", "understand"]):
            analysis["issue_type"] = "listening"
        elif any(word in issue_lower for word in ["express", "say", "tell", "communicate"]):
            analysis["issue_type"] = "expression"
        elif any(word in issue_lower for word in ["argue", "fight", "conflict", "disagree"]):
            analysis["issue_type"] = "conflict"
        elif any(word in issue_lower for word in ["emotion", "feel", "emotional"]):
            analysis["issue_type"] = "emotional"
        
        return analysis
    
    async def _generate_communication_coaching(self, user_id: str, issue_analysis: Dict[str, Any],
                                             relationship_context: Dict[str, Any],
                                             user_profile: UserTherapyProfile,
                                             coaching_context: List) -> Dict[str, Any]:
        """
        Generate personalized communication coaching
        """
        coaching = {
            "issue_type": issue_analysis["issue_type"],
            "personalized_strategies": [],
            "practice_exercises": [],
            "conversation_starters": [],
            "warning_signs": [],
            "success_indicators": []
        }
        
        # Generate strategies based on issue type
        if issue_analysis["issue_type"] == "listening":
            coaching["personalized_strategies"] = [
                "Practice the SOLER technique (Square shoulders, Open posture, Lean in, Eye contact, Relax)",
                "Use reflective listening: 'What I hear you saying is...'",
                "Ask clarifying questions before responding"
            ]
            coaching["practice_exercises"] = [
                "Daily 10-minute listening practice with partner",
                "Summarize conversations before giving your opinion",
                "Practice mindful listening meditation"
            ]
        elif issue_analysis["issue_type"] == "expression":
            coaching["personalized_strategies"] = [
                "Use 'I' statements to express feelings and needs",
                "Practice the XYZ formula: 'In situation X, when you do Y, I feel Z'",
                "Be specific about what you need from your partner"
            ]
            coaching["practice_exercises"] = [
                "Write down feelings before important conversations",
                "Practice expressing needs clearly and directly",
                "Role-play difficult conversations"
            ]
        
        return coaching
    
    async def _generate_health_assessment_report(self, user_id: str, health_metrics: Dict[str, float],
                                               conversation_history: List[str]) -> Dict[str, Any]:
        """
        Generate health assessment report
        """
        report = {
            "overall_assessment": "healthy" if health_metrics["overall_health"] > 0.7 else "needs_attention",
            "key_findings": [],
            "strengths": [],
            "concerns": [],
            "recommendations": []
        }
        
        # Analyze metrics and generate findings
        for metric, score in health_metrics.items():
            if metric != "overall_health":
                if score > 0.7:
                    report["strengths"].append(f"Strong {metric.replace('_', ' ')}: {score:.2f}")
                elif score < 0.4:
                    report["concerns"].append(f"Low {metric.replace('_', ' ')}: {score:.2f}")
        
        return report
    
    async def _generate_health_recommendations(self, health_metrics: Dict[str, float]) -> List[str]:
        """
        Generate health-based recommendations
        """
        recommendations = []
        
        for metric, score in health_metrics.items():
            if metric != "overall_health" and score < 0.5:
                if metric == "communication_quality":
                    recommendations.append("Focus on improving communication skills through active listening and clear expression")
                elif metric == "emotional_connection":
                    recommendations.append("Invest time in emotional intimacy through sharing and vulnerability")
                elif metric == "conflict_resolution":
                    recommendations.append("Learn and practice healthy conflict resolution techniques")
        
        if not recommendations:
            recommendations.append("Continue maintaining your healthy relationship patterns")
        
        return recommendations
    
    async def _update_user_profile_from_analysis(self, user_id: str, analysis_result: AnalysisResult,
                                               insight: TherapeuticInsight):
        """
        Update user profile based on analysis insights
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update progress metrics
            profile.progress_metrics.update({
                "last_communication_score": analysis_result.metrics.communication_effectiveness,
                "last_emotional_score": analysis_result.metrics.emotional_intelligence_score,
                "last_conflict_score": analysis_result.metrics.conflict_resolution_score
            })
            
            # Add session to history
            session_record = {
                "timestamp": datetime.now().isoformat(),
                "analysis_id": analysis_result.analysis_id,
                "insight_id": insight.insight_id,
                "insight_type": insight.insight_type,
                "confidence_score": insight.confidence_score
            }
            
            profile.session_history.append(session_record)
            
            # Keep only last 50 sessions
            if len(profile.session_history) > 50:
                profile.session_history = profile.session_history[-50:]
            
            profile.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating user profile from analysis: {str(e)}")