#!/usr/bin/env python3
"""
Toolbox & Motor Layer - Layer 6 of AI Brain Architecture
Handles response generation, communication tools, external actions, and output execution
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
import re
import random

from ..core.brain_architecture import BrainLayer, LayerType, LayerInput, LayerOutput

logger = logging.getLogger(__name__)

class OutputType(Enum):
    THERAPEUTIC_RESPONSE = "therapeutic_response"
    CRISIS_INTERVENTION = "crisis_intervention"
    SKILL_TEACHING = "skill_teaching"
    EMOTIONAL_SUPPORT = "emotional_support"
    RELATIONSHIP_GUIDANCE = "relationship_guidance"
    HOMEWORK_ASSIGNMENT = "homework_assignment"
    RESOURCE_RECOMMENDATION = "resource_recommendation"

class CommunicationTool(Enum):
    ACTIVE_LISTENING = "active_listening"
    REFLECTIVE_QUESTIONING = "reflective_questioning"
    VALIDATION_TECHNIQUES = "validation_techniques"
    REFRAMING_TOOLS = "reframing_tools"
    METAPHOR_STORYTELLING = "metaphor_storytelling"
    SKILL_DEMONSTRATION = "skill_demonstration"
    HOMEWORK_CREATION = "homework_creation"

class ResponseStyle(Enum):
    DIEGO_WARM_SUPPORTIVE = "diego_warm_supportive"
    DIEGO_GENTLE_EXPLORATORY = "diego_gentle_exploratory"
    DIEGO_WISE_GUIDING = "diego_wise_guiding"
    DIEGO_CRISIS_STABILIZING = "diego_crisis_stabilizing"
    DIEGO_SKILL_TEACHING = "diego_skill_teaching"
    DIEGO_RELATIONSHIP_COACHING = "diego_relationship_coaching"

@dataclass
class GeneratedResponse:
    """A generated therapeutic response"""
    response_id: str
    content: str
    response_type: str
    style: str
    emotional_tone: str
    therapeutic_elements: List[str]
    diego_characteristics: List[str]
    communication_tools_used: List[str]
    stage_alignment: str
    safety_considerations: List[str]
    follow_up_elements: List[str]
    estimated_impact: Dict[str, float]
    confidence: float
    timestamp: datetime

@dataclass
class CommunicationOutput:
    """Complete communication output package"""
    output_id: str
    primary_response: GeneratedResponse
    alternative_responses: List[GeneratedResponse]
    follow_up_questions: List[str]
    homework_assignments: List[str]
    resource_recommendations: List[str]
    crisis_protocols: List[str]
    diego_persona_elements: Dict[str, Any]
    conversation_metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    timestamp: datetime

@dataclass
class SkillTeachingModule:
    """Module for teaching specific skills"""
    skill_name: str
    description: str
    teaching_steps: List[str]
    practice_exercises: List[str]
    real_world_applications: List[str]
    success_indicators: List[str]
    common_challenges: List[str]
    diego_teaching_style: Dict[str, Any]

@dataclass
class HomeworkAssignment:
    """Structured homework assignment"""
    assignment_id: str
    title: str
    description: str
    objectives: List[str]
    instructions: List[str]
    time_commitment: str
    difficulty_level: str
    success_criteria: List[str]
    support_resources: List[str]
    check_in_schedule: str
    diego_encouragement: str

class ToolboxMotorLayer(BrainLayer):
    """Layer 6: Toolbox & Motor - Response generation and communication execution"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(LayerType.TOOLBOX_MOTOR, config)
        
        # Communication tools
        self.response_generator = ResponseGenerator()
        self.communication_toolkit = CommunicationToolkit()
        self.diego_persona_engine = DiegoPersonaEngine()
        self.skill_teacher = SkillTeacher()
        self.homework_creator = HomeworkCreator()
        
        # Response templates and patterns
        self.response_templates = self._load_response_templates()
        self.diego_language_patterns = self._load_diego_language_patterns()
        self.therapeutic_techniques = self._load_therapeutic_techniques()
        self.crisis_protocols = self._load_crisis_protocols()
        
        # Configuration
        self.max_response_length = config.get("max_response_length", 500)
        self.min_response_length = config.get("min_response_length", 50)
        self.diego_consistency_threshold = config.get("diego_consistency_threshold", 0.8)
        self.safety_check_enabled = config.get("safety_check_enabled", True)
        self.alternative_responses_count = config.get("alternative_responses_count", 2)
    
    async def process(self, input_data: LayerInput) -> LayerOutput:
        """Process input through toolbox and motor layer"""
        try:
            self.logger.debug(f"Processing toolbox/motor input: {input_data.layer_id}")
            
            # Extract data from previous layers
            risk_assessment = input_data.data.get("risk_assessment", {})
            strategic_decisions = input_data.data.get("strategic_decisions", [])
            action_plan = input_data.data.get("action_plan", {})
            response_plan = input_data.data.get("response_plan", {})
            optimized_actions = input_data.data.get("optimized_actions", {})
            conversation_strategy = input_data.data.get("conversation_strategy", {})
            follow_up_strategy = input_data.data.get("follow_up_strategy", {})
            diego_emotional_state = input_data.data.get("diego_emotional_state", {})
            emotional_response = input_data.data.get("emotional_response", {})
            user_profile = input_data.data.get("user_profile", {})
            conversation_context = input_data.data.get("conversation_context", {})
            stage_analysis = input_data.data.get("stage_analysis", {})
            psychological_assessment = input_data.data.get("psychological_assessment", {})
            
            # Generate primary therapeutic response
            primary_response = await self._generate_primary_response(
                response_plan, optimized_actions, diego_emotional_state,
                risk_assessment, conversation_strategy
            )
            
            # Generate alternative responses
            alternative_responses = await self._generate_alternative_responses(
                response_plan, optimized_actions, diego_emotional_state,
                primary_response
            )
            
            # Create follow-up questions
            follow_up_questions = await self._create_follow_up_questions(
                conversation_strategy, response_plan, stage_analysis
            )
            
            # Generate homework assignments
            homework_assignments = await self._generate_homework_assignments(
                follow_up_strategy, action_plan, stage_analysis
            )
            
            # Create resource recommendations
            resource_recommendations = await self._create_resource_recommendations(
                action_plan, psychological_assessment, stage_analysis
            )
            
            # Prepare crisis protocols if needed
            crisis_protocols = await self._prepare_crisis_protocols(
                risk_assessment, strategic_decisions
            )
            
            # Enhance Diego persona elements
            diego_persona_elements = await self._enhance_diego_persona_elements(
                optimized_actions, diego_emotional_state, primary_response
            )
            
            # Generate conversation metadata
            conversation_metadata = await self._generate_conversation_metadata(
                primary_response, action_plan, conversation_strategy
            )
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                primary_response, alternative_responses, response_plan
            )
            
            # Perform safety checks
            safety_validation = await self._perform_safety_checks(
                primary_response, risk_assessment, crisis_protocols
            )
            
            # Create communication output package
            communication_output = CommunicationOutput(
                output_id=f"comm_output_{datetime.now().timestamp()}",
                primary_response=primary_response,
                alternative_responses=alternative_responses,
                follow_up_questions=follow_up_questions,
                homework_assignments=homework_assignments,
                resource_recommendations=resource_recommendations,
                crisis_protocols=crisis_protocols,
                diego_persona_elements=diego_persona_elements,
                conversation_metadata=conversation_metadata,
                quality_metrics=quality_metrics,
                timestamp=datetime.now()
            )
            
            # Prepare output data
            output_data = {
                "communication_output": asdict(communication_output),
                "primary_response": asdict(primary_response),
                "alternative_responses": [asdict(r) for r in alternative_responses],
                "follow_up_questions": follow_up_questions,
                "homework_assignments": homework_assignments,
                "resource_recommendations": resource_recommendations,
                "crisis_protocols": crisis_protocols,
                "diego_persona_elements": diego_persona_elements,
                "safety_validation": safety_validation,
                "quality_metrics": quality_metrics,
                "toolbox_metadata": {
                    "layer": "toolbox_motor",
                    "timestamp": datetime.now().isoformat(),
                    "response_type": primary_response.response_type,
                    "style": primary_response.style,
                    "tools_used": primary_response.communication_tools_used,
                    "safety_validated": safety_validation.get("passed", False),
                    "quality_score": quality_metrics.get("overall_quality", 0.7)
                },
                # Pass through previous layer data
                "risk_assessment": risk_assessment,
                "strategic_decisions": strategic_decisions,
                "action_plan": action_plan,
                "response_plan": response_plan,
                "optimized_actions": optimized_actions,
                "conversation_strategy": conversation_strategy,
                "follow_up_strategy": follow_up_strategy,
                "diego_emotional_state": diego_emotional_state,
                "emotional_response": emotional_response,
                "user_profile": user_profile,
                "conversation_context": conversation_context,
                "stage_analysis": stage_analysis,
                "psychological_assessment": psychological_assessment
            }
            
            return LayerOutput(
                layer_id=self.layer_id,
                data=output_data,
                timestamp=datetime.now(),
                target_layers=["selfhood_awareness"],
                confidence=self._calculate_layer_confidence(output_data),
                metadata={
                    "communication_summary": {
                        "response_generated": True,
                        "response_type": primary_response.response_type,
                        "style": primary_response.style,
                        "word_count": len(primary_response.content.split()),
                        "tools_used": len(primary_response.communication_tools_used),
                        "safety_validated": safety_validation.get("passed", False),
                        "alternatives_generated": len(alternative_responses),
                        "homework_assigned": len(homework_assignments) > 0,
                        "resources_recommended": len(resource_recommendations) > 0
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in toolbox/motor processing: {str(e)}")
            raise
    
    async def _generate_primary_response(self, response_plan: Dict[str, Any],
                                       optimized_actions: Dict[str, Any],
                                       diego_emotional_state: Dict[str, Any],
                                       risk_assessment: Dict[str, Any],
                                       conversation_strategy: Dict[str, Any]) -> GeneratedResponse:
        """Generate the primary therapeutic response"""
        
        # Determine response type and style
        response_type = self._determine_response_type(response_plan, risk_assessment)
        response_style = self._determine_response_style(response_plan, diego_emotional_state)
        
        # Select communication tools
        communication_tools = self._select_communication_tools(
            response_plan, conversation_strategy, response_type
        )
        
        # Generate response content
        response_content = await self._generate_response_content(
            response_plan, optimized_actions, diego_emotional_state,
            communication_tools, response_style
        )
        
        # Apply Diego's persona characteristics
        diego_enhanced_content = await self._apply_diego_persona(
            response_content, diego_emotional_state, optimized_actions
        )
        
        # Extract therapeutic elements
        therapeutic_elements = response_plan.get("therapeutic_elements", [])
        
        # Extract Diego characteristics
        diego_characteristics = response_plan.get("diego_characteristics", [])
        
        # Determine emotional tone
        emotional_tone = response_plan.get("emotional_tone", "supportive")
        
        # Stage alignment
        stage_alignment = response_plan.get("stage_progression_elements", [])
        
        # Safety considerations
        safety_considerations = self._extract_safety_considerations(
            risk_assessment, response_plan
        )
        
        # Follow-up elements
        follow_up_elements = response_plan.get("follow_up_questions", [])
        
        # Estimate impact
        estimated_impact = self._estimate_response_impact(
            diego_enhanced_content, therapeutic_elements, communication_tools
        )
        
        # Calculate confidence
        response_confidence = self._calculate_response_confidence(
            response_plan, diego_enhanced_content, therapeutic_elements
        )
        
        return GeneratedResponse(
            response_id=f"response_{datetime.now().timestamp()}",
            content=diego_enhanced_content,
            response_type=response_type,
            style=response_style,
            emotional_tone=emotional_tone,
            therapeutic_elements=therapeutic_elements,
            diego_characteristics=diego_characteristics,
            communication_tools_used=communication_tools,
            stage_alignment=str(stage_alignment),
            safety_considerations=safety_considerations,
            follow_up_elements=follow_up_elements,
            estimated_impact=estimated_impact,
            confidence=response_confidence,
            timestamp=datetime.now()
        )
    
    async def _generate_alternative_responses(self, response_plan: Dict[str, Any],
                                            optimized_actions: Dict[str, Any],
                                            diego_emotional_state: Dict[str, Any],
                                            primary_response: GeneratedResponse) -> List[GeneratedResponse]:
        """Generate alternative response options"""
        alternatives = []
        
        # Generate variations with different styles
        alternative_styles = self._get_alternative_styles(primary_response.style)
        
        for i, alt_style in enumerate(alternative_styles[:self.alternative_responses_count]):
            # Modify approach for alternative
            alt_response_plan = response_plan.copy()
            alt_response_plan["response_strategy"] = alt_style
            
            # Generate alternative content
            alt_content = await self._generate_alternative_content(
                alt_response_plan, optimized_actions, diego_emotional_state,
                primary_response, alt_style
            )
            
            # Create alternative response
            alternative = GeneratedResponse(
                response_id=f"alt_response_{i}_{datetime.now().timestamp()}",
                content=alt_content,
                response_type=primary_response.response_type,
                style=alt_style,
                emotional_tone=primary_response.emotional_tone,
                therapeutic_elements=primary_response.therapeutic_elements,
                diego_characteristics=primary_response.diego_characteristics,
                communication_tools_used=primary_response.communication_tools_used,
                stage_alignment=primary_response.stage_alignment,
                safety_considerations=primary_response.safety_considerations,
                follow_up_elements=primary_response.follow_up_elements,
                estimated_impact=self._estimate_response_impact(
                    alt_content, primary_response.therapeutic_elements,
                    primary_response.communication_tools_used
                ),
                confidence=primary_response.confidence * 0.9,  # Slightly lower confidence
                timestamp=datetime.now()
            )
            
            alternatives.append(alternative)
        
        return alternatives
    
    async def _generate_response_content(self, response_plan: Dict[str, Any],
                                       optimized_actions: Dict[str, Any],
                                       diego_emotional_state: Dict[str, Any],
                                       communication_tools: List[str],
                                       response_style: str) -> str:
        """Generate the actual response content"""
        
        # Get response template
        template = self._get_response_template(response_style)
        
        # Extract key elements
        key_messages = response_plan.get("key_messages", [])
        therapeutic_elements = response_plan.get("therapeutic_elements", [])
        conversation_flow = response_plan.get("conversation_flow", [])
        validation_points = response_plan.get("validation_points", [])
        reframing_opportunities = response_plan.get("reframing_opportunities", [])
        
        # Build response sections
        response_sections = []
        
        # Opening section
        opening = self._generate_opening_section(
            optimized_actions, diego_emotional_state, validation_points
        )
        response_sections.append(opening)
        
        # Main content sections
        for i, message in enumerate(key_messages[:3]):  # Limit to 3 key messages
            section = self._generate_content_section(
                message, therapeutic_elements, communication_tools,
                reframing_opportunities, diego_emotional_state
            )
            response_sections.append(section)
        
        # Closing section
        closing = self._generate_closing_section(
            optimized_actions, diego_emotional_state, conversation_flow
        )
        response_sections.append(closing)
        
        # Combine sections
        full_response = "\n\n".join(filter(None, response_sections))
        
        # Apply length constraints
        full_response = self._apply_length_constraints(full_response)
        
        return full_response
    
    async def _apply_diego_persona(self, content: str,
                                 diego_emotional_state: Dict[str, Any],
                                 optimized_actions: Dict[str, Any]) -> str:
        """Apply Diego's persona characteristics to the response"""
        
        # Get Diego's signature elements
        signature_elements = optimized_actions.get("signature_elements", {})
        
        # Apply opening phrases
        opening_phrases = signature_elements.get("opening_phrases", [])
        if opening_phrases and not any(phrase in content for phrase in opening_phrases):
            selected_opening = random.choice(opening_phrases)
            content = f"{selected_opening} {content}"
        
        # Apply Diego's language patterns
        content = self._apply_diego_language_patterns(content, diego_emotional_state)
        
        # Apply emotional expression style
        emotional_expression = optimized_actions.get("emotional_expression", {})
        content = self._apply_emotional_expression(content, emotional_expression)
        
        # Apply wisdom integration
        wisdom_integration = optimized_actions.get("wisdom_integration", {})
        content = self._integrate_wisdom_elements(content, wisdom_integration)
        
        # Apply cultural sensitivity
        cultural_considerations = optimized_actions.get("cultural_considerations", {})
        content = self._apply_cultural_sensitivity(content, cultural_considerations)
        
        # Apply professional boundaries
        professional_boundaries = optimized_actions.get("professional_boundaries", {})
        content = self._maintain_professional_tone(content, professional_boundaries)
        
        return content
    
    async def _create_follow_up_questions(self, conversation_strategy: Dict[str, Any],
                                        response_plan: Dict[str, Any],
                                        stage_analysis: Dict[str, Any]) -> List[str]:
        """Create thoughtful follow-up questions"""
        
        questions = []
        
        # Questions based on conversation goals
        conversation_goals = conversation_strategy.get("conversation_goals", [])
        for goal in conversation_goals[:2]:  # Limit to 2 goals
            question = self._generate_goal_based_question(goal, stage_analysis)
            if question:
                questions.append(question)
        
        # Questions based on therapeutic elements
        therapeutic_elements = response_plan.get("therapeutic_elements", [])
        for element in therapeutic_elements[:2]:  # Limit to 2 elements
            question = self._generate_therapeutic_question(element, stage_analysis)
            if question:
                questions.append(question)
        
        # Stage-specific questions
        current_stage = stage_analysis.get("current_stage", "APP")
        stage_questions = self._generate_stage_specific_questions(current_stage)
        questions.extend(stage_questions[:2])  # Limit to 2 stage questions
        
        # Remove duplicates and limit total
        unique_questions = list(dict.fromkeys(questions))  # Remove duplicates
        return unique_questions[:5]  # Limit to 5 questions total
    
    async def _generate_homework_assignments(self, follow_up_strategy: Dict[str, Any],
                                           action_plan: Dict[str, Any],
                                           stage_analysis: Dict[str, Any]) -> List[str]:
        """Generate homework assignments"""
        
        assignments = []
        
        # Get homework from follow-up strategy
        strategy_homework = follow_up_strategy.get("homework_assignments", [])
        assignments.extend(strategy_homework)
        
        # Generate skill practice assignments
        therapeutic_techniques = action_plan.get("therapeutic_techniques", [])
        for technique in therapeutic_techniques[:2]:  # Limit to 2 techniques
            assignment = self._create_skill_practice_assignment(technique, stage_analysis)
            if assignment:
                assignments.append(assignment)
        
        # Generate stage-specific assignments
        current_stage = stage_analysis.get("current_stage", "APP")
        stage_assignment = self._create_stage_specific_assignment(current_stage)
        if stage_assignment:
            assignments.append(stage_assignment)
        
        return assignments[:3]  # Limit to 3 assignments
    
    async def _create_resource_recommendations(self, action_plan: Dict[str, Any],
                                             psychological_assessment: Dict[str, Any],
                                             stage_analysis: Dict[str, Any]) -> List[str]:
        """Create resource recommendations"""
        
        resources = []
        
        # Resources based on therapeutic techniques
        therapeutic_techniques = action_plan.get("therapeutic_techniques", [])
        for technique in therapeutic_techniques:
            resource = self._get_technique_resource(technique)
            if resource:
                resources.append(resource)
        
        # Resources based on psychological needs
        stress_level = psychological_assessment.get("stress_level", 0)
        if stress_level > 0.7:
            resources.append("Stress management techniques and relaxation exercises")
        
        communication_issues = psychological_assessment.get("communication_issues", [])
        if communication_issues:
            resources.append("Communication skills workbook and practice exercises")
        
        # Stage-specific resources
        current_stage = stage_analysis.get("current_stage", "APP")
        stage_resources = self._get_stage_specific_resources(current_stage)
        resources.extend(stage_resources)
        
        return resources[:5]  # Limit to 5 resources
    
    async def _prepare_crisis_protocols(self, risk_assessment: Dict[str, Any],
                                      strategic_decisions: List[Dict[str, Any]]) -> List[str]:
        """Prepare crisis intervention protocols if needed"""
        
        protocols = []
        
        risk_level = risk_assessment.get("risk_level", "low")
        
        if risk_level == "critical":
            protocols.extend([
                "Immediate safety assessment required",
                "Crisis intervention protocols activated",
                "Professional referral recommended",
                "Emergency contact information provided"
            ])
        elif risk_level == "high":
            protocols.extend([
                "Enhanced safety monitoring",
                "Frequent check-ins recommended",
                "Crisis resources provided"
            ])
        
        # Check for safety decisions
        safety_decisions = [
            d for d in strategic_decisions 
            if d.get("decision_type") == "safety_action"
        ]
        
        for decision in safety_decisions:
            protocols.extend(decision.get("implementation_steps", []))
        
        return protocols
    
    async def _enhance_diego_persona_elements(self, optimized_actions: Dict[str, Any],
                                            diego_emotional_state: Dict[str, Any],
                                            primary_response: GeneratedResponse) -> Dict[str, Any]:
        """Enhance Diego persona elements for consistency"""
        
        return {
            "current_emotional_state": diego_emotional_state,
            "signature_phrases_used": self._extract_signature_phrases(primary_response.content),
            "wisdom_elements_integrated": self._extract_wisdom_elements(primary_response.content),
            "cultural_sensitivity_applied": optimized_actions.get("cultural_considerations", {}),
            "professional_boundaries_maintained": optimized_actions.get("professional_boundaries", {}),
            "response_pacing": optimized_actions.get("response_pacing", {}),
            "diego_consistency_score": self._calculate_diego_consistency(
                primary_response, optimized_actions
            )
        }
    
    async def _generate_conversation_metadata(self, primary_response: GeneratedResponse,
                                            action_plan: Dict[str, Any],
                                            conversation_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conversation metadata"""
        
        return {
            "conversation_direction": action_plan.get("conversation_direction", "unknown"),
            "primary_strategy": action_plan.get("primary_strategy", "unknown"),
            "therapeutic_focus": primary_response.therapeutic_elements,
            "engagement_level": conversation_strategy.get("engagement_approach", {}),
            "depth_level": conversation_strategy.get("depth_progression", {}),
            "safety_maintained": len(primary_response.safety_considerations) == 0,
            "diego_persona_active": len(primary_response.diego_characteristics) > 0,
            "response_quality_indicators": {
                "length_appropriate": self._check_length_appropriateness(primary_response.content),
                "tone_consistent": self._check_tone_consistency(primary_response),
                "therapeutic_elements_present": len(primary_response.therapeutic_elements) > 0,
                "diego_characteristics_present": len(primary_response.diego_characteristics) > 0
            }
        }
    
    async def _calculate_quality_metrics(self, primary_response: GeneratedResponse,
                                       alternative_responses: List[GeneratedResponse],
                                       response_plan: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for responses"""
        
        metrics = {
            "overall_quality": self._calculate_overall_quality(primary_response, response_plan),
            "therapeutic_alignment": self._calculate_therapeutic_alignment(primary_response, response_plan),
            "diego_consistency": self._calculate_diego_consistency_score(primary_response),
            "safety_score": self._calculate_safety_score(primary_response),
            "engagement_potential": self._calculate_engagement_potential(primary_response),
            "response_completeness": self._calculate_response_completeness(primary_response, response_plan),
            "alternative_quality": self._calculate_alternative_quality(alternative_responses)
        }
        
        return metrics
    
    async def _perform_safety_checks(self, primary_response: GeneratedResponse,
                                   risk_assessment: Dict[str, Any],
                                   crisis_protocols: List[str]) -> Dict[str, Any]:
        """Perform safety validation checks"""
        
        safety_checks = {
            "content_safety": self._check_content_safety(primary_response.content),
            "risk_appropriateness": self._check_risk_appropriateness(
                primary_response, risk_assessment
            ),
            "crisis_protocol_alignment": self._check_crisis_protocol_alignment(
                primary_response, crisis_protocols
            ),
            "professional_boundaries": self._check_professional_boundaries(
                primary_response.content
            ),
            "therapeutic_appropriateness": self._check_therapeutic_appropriateness(
                primary_response
            )
        }
        
        # Overall safety validation
        all_checks_passed = all(check.get("passed", False) for check in safety_checks.values())
        
        return {
            "passed": all_checks_passed,
            "checks": safety_checks,
            "warnings": [check.get("warning") for check in safety_checks.values() if check.get("warning")],
            "recommendations": [check.get("recommendation") for check in safety_checks.values() if check.get("recommendation")]
        }
    
    # Helper methods for response generation
    def _determine_response_type(self, response_plan: Dict[str, Any],
                               risk_assessment: Dict[str, Any]) -> str:
        """Determine the type of response needed"""
        
        risk_level = risk_assessment.get("risk_level", "low")
        
        if risk_level == "critical":
            return OutputType.CRISIS_INTERVENTION.value
        elif risk_level == "high":
            return OutputType.EMOTIONAL_SUPPORT.value
        
        strategy = response_plan.get("response_strategy", "supportive_listening")
        
        if "skill" in strategy.lower():
            return OutputType.SKILL_TEACHING.value
        elif "coaching" in strategy.lower():
            return OutputType.RELATIONSHIP_GUIDANCE.value
        else:
            return OutputType.THERAPEUTIC_RESPONSE.value
    
    def _determine_response_style(self, response_plan: Dict[str, Any],
                                diego_emotional_state: Dict[str, Any]) -> str:
        """Determine Diego's response style"""
        
        strategy = response_plan.get("response_strategy", "supportive_listening")
        emotional_tone = response_plan.get("emotional_tone", "supportive")
        
        if "crisis" in strategy.lower():
            return ResponseStyle.DIEGO_CRISIS_STABILIZING.value
        elif "skill" in strategy.lower():
            return ResponseStyle.DIEGO_SKILL_TEACHING.value
        elif "coaching" in strategy.lower():
            return ResponseStyle.DIEGO_RELATIONSHIP_COACHING.value
        elif "exploration" in strategy.lower():
            return ResponseStyle.DIEGO_GENTLE_EXPLORATORY.value
        elif "wise" in emotional_tone.lower() or "guidance" in strategy.lower():
            return ResponseStyle.DIEGO_WISE_GUIDING.value
        else:
            return ResponseStyle.DIEGO_WARM_SUPPORTIVE.value
    
    def _select_communication_tools(self, response_plan: Dict[str, Any],
                                  conversation_strategy: Dict[str, Any],
                                  response_type: str) -> List[str]:
        """Select appropriate communication tools"""
        
        tools = []
        
        # Always include active listening
        tools.append(CommunicationTool.ACTIVE_LISTENING.value)
        
        # Add tools based on response type
        if response_type == OutputType.CRISIS_INTERVENTION.value:
            tools.extend([
                CommunicationTool.VALIDATION_TECHNIQUES.value,
                CommunicationTool.REFLECTIVE_QUESTIONING.value
            ])
        elif response_type == OutputType.SKILL_TEACHING.value:
            tools.extend([
                CommunicationTool.SKILL_DEMONSTRATION.value,
                CommunicationTool.HOMEWORK_CREATION.value
            ])
        elif response_type == OutputType.RELATIONSHIP_GUIDANCE.value:
            tools.extend([
                CommunicationTool.REFRAMING_TOOLS.value,
                CommunicationTool.METAPHOR_STORYTELLING.value
            ])
        else:
            tools.extend([
                CommunicationTool.VALIDATION_TECHNIQUES.value,
                CommunicationTool.REFLECTIVE_QUESTIONING.value
            ])
        
        return tools[:4]  # Limit to 4 tools
    
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load response templates"""
        return {
            "diego_warm_supportive": {
                "opening": ["I can hear", "I understand", "Thank you for sharing"],
                "body": ["validation", "gentle_exploration", "support_offering"],
                "closing": ["gentle_encouragement", "next_steps", "availability"]
            },
            "diego_gentle_exploratory": {
                "opening": ["I'm curious about", "Help me understand", "I wonder"],
                "body": ["careful_questioning", "pattern_exploration", "insight_invitation"],
                "closing": ["reflection_invitation", "gentle_challenge", "support_reminder"]
            },
            "diego_wise_guiding": {
                "opening": ["In my experience", "I've noticed", "What I've learned"],
                "body": ["wisdom_sharing", "perspective_offering", "guidance_provision"],
                "closing": ["encouragement", "confidence_building", "next_steps"]
            }
        }
    
    def _load_diego_language_patterns(self) -> Dict[str, Any]:
        """Load Diego's characteristic language patterns"""
        return {
            "diplomatic_phrases": [
                "I wonder if", "Perhaps", "It seems like", "I'm thinking"
            ],
            "wisdom_expressions": [
                "In my experience", "What I've learned", "I've found that"
            ],
            "gentle_transitions": [
                "At the same time", "And yet", "I'm also thinking", "Another way to look at this"
            ],
            "supportive_affirmations": [
                "That makes sense", "I can understand why", "That's completely normal"
            ]
        }
    
    def _load_therapeutic_techniques(self) -> Dict[str, Any]:
        """Load therapeutic techniques"""
        return {
            "validation": ["emotional_validation", "experience_normalization", "strength_recognition"],
            "exploration": ["open_ended_questions", "pattern_identification", "insight_generation"],
            "skill_building": ["technique_teaching", "practice_guidance", "homework_assignment"],
            "reframing": ["perspective_shift", "strength_focus", "opportunity_identification"]
        }
    
    def _load_crisis_protocols(self) -> Dict[str, Any]:
        """Load crisis intervention protocols"""
        return {
            "immediate_safety": ["safety_assessment", "crisis_resources", "professional_referral"],
            "stabilization": ["grounding_techniques", "emotional_regulation", "support_activation"],
            "follow_up": ["safety_planning", "resource_connection", "ongoing_monitoring"]
        }
    
    def _calculate_layer_confidence(self, output_data: Dict[str, Any]) -> float:
        """Calculate layer confidence"""
        quality_metrics = output_data.get("quality_metrics", {})
        return quality_metrics.get("overall_quality", 0.7)
    
    # Additional helper methods would continue here...
    # For brevity, including key method signatures
    
    def _generate_opening_section(self, optimized_actions: Dict[str, Any],
                                diego_emotional_state: Dict[str, Any],
                                validation_points: List[str]) -> str:
        """Generate opening section of response"""
        return "Thank you for sharing that with me. I can hear how important this is to you."
    
    def _generate_content_section(self, message: str, therapeutic_elements: List[str],
                                communication_tools: List[str], reframing_opportunities: List[str],
                                diego_emotional_state: Dict[str, Any]) -> str:
        """Generate main content section"""
        return f"I'm thinking about what you've shared, and {message.lower()}."
    
    def _generate_closing_section(self, optimized_actions: Dict[str, Any],
                                diego_emotional_state: Dict[str, Any],
                                conversation_flow: List[str]) -> str:
        """Generate closing section of response"""
        return "How does this resonate with you? I'm here to support you through this."
    
    def _apply_length_constraints(self, content: str) -> str:
        """Apply length constraints to response"""
        words = content.split()
        if len(words) > self.max_response_length:
            return " ".join(words[:self.max_response_length]) + "..."
        return content

# Helper classes
class ResponseGenerator:
    """Generates therapeutic responses"""
    pass

class CommunicationToolkit:
    """Provides communication tools and techniques"""
    pass

class DiegoPersonaEngine:
    """Manages Diego's persona consistency"""
    pass

class SkillTeacher:
    """Teaches therapeutic and relationship skills"""
    pass

class HomeworkCreator:
    """Creates homework assignments and exercises"""
    pass