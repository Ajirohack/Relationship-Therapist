"""Enhanced AI Service with OpenAI and Anthropic integration"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

from config import settings, AIProvider

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    SENTIMENT = "sentiment"
    COMMUNICATION_STYLE = "communication_style"
    RELATIONSHIP_HEALTH = "relationship_health"
    CONFLICT_DETECTION = "conflict_detection"
    RECOMMENDATION = "recommendation"
    PATTERN_ANALYSIS = "pattern_analysis"

@dataclass
class AIResponse:
    content: str
    confidence: float
    metadata: Dict[str, Any]
    provider: str
    model: str
    timestamp: datetime

class AIService:
    """Enhanced AI service with multiple provider support"""
    
    def __init__(self):
        self.provider = settings.ai_provider
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI provider clients"""
        try:
            if self.provider == AIProvider.OPENAI and openai and settings.openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            
            if self.provider == AIProvider.ANTHROPIC and anthropic and settings.anthropic_api_key:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
                
        except Exception as e:
            logger.warning(f"Failed to initialize AI clients: {e}")
            self.provider = AIProvider.LOCAL
    
    async def analyze_conversation(self, 
                                 conversation_text: str, 
                                 analysis_type: AnalysisType,
                                 context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze conversation using the configured AI provider"""
        
        if self.provider == AIProvider.OPENAI and self.openai_client:
            return await self._analyze_with_openai(conversation_text, analysis_type, context)
        elif self.provider == AIProvider.ANTHROPIC and self.anthropic_client:
            return await self._analyze_with_anthropic(conversation_text, analysis_type, context)
        else:
            return await self._analyze_locally(conversation_text, analysis_type, context)
    
    async def _analyze_with_openai(self, 
                                  conversation_text: str, 
                                  analysis_type: AnalysisType,
                                  context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze using OpenAI API"""
        try:
            prompt = self._build_analysis_prompt(conversation_text, analysis_type, context)
            
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(analysis_type)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            return AIResponse(
                content=content,
                confidence=0.9,  # OpenAI doesn't provide confidence scores
                metadata={"model": response.model, "usage": response.usage.dict() if hasattr(response.usage, "dict") else vars(response.usage)},
                provider="openai",
                model=response.model,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return await self._analyze_locally(conversation_text, analysis_type, context)
    
    async def _analyze_with_anthropic(self, 
                                     conversation_text: str, 
                                     analysis_type: AnalysisType,
                                     context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze using Anthropic API"""
        try:
            prompt = self._build_analysis_prompt(conversation_text, analysis_type, context)
            system_prompt = self._get_system_prompt(analysis_type)
            
            response = await self.anthropic_client.messages.create(
                model=settings.anthropic_model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.content[0].text
            
            return AIResponse(
                content=content,
                confidence=0.85,  # Anthropic doesn't provide confidence scores
                metadata={"model": response.model},
                provider="anthropic",
                model=response.model,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Anthropic analysis failed: {e}")
            return await self._analyze_locally(conversation_text, analysis_type, context)
    
    async def _analyze_locally(self, 
                              conversation_text: str, 
                              analysis_type: AnalysisType,
                              context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Fallback to local analysis when AI services are unavailable"""
        from minimal_implementations import MinimalConversationAnalyzer, MinimalAITherapist
        
        try:
            analyzer = MinimalConversationAnalyzer()
            therapist = MinimalAITherapist()
            
            # Extract conversation as list if it's in text form
            if isinstance(conversation_text, str):
                # Simple conversation parser - assumes format like "Person A: text\nPerson B: response"
                lines = conversation_text.strip().split('\n')
                conversations = []
                
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            speaker = parts[0].strip()
                            text = parts[1].strip()
                            conversations.append({"speaker": speaker, "text": text})
            else:
                conversations = conversation_text
            
            if analysis_type == AnalysisType.SENTIMENT:
                # Use VADER for sentiment analysis
                all_text = " ".join([c.get("text", "") for c in conversations]) if isinstance(conversations, list) else conversation_text
                result = analyzer.analyze_basic_sentiment(all_text)
                content = json.dumps({
                    "sentiment": result["sentiment_label"],
                    "score": result["compound"],
                    "details": {
                        "positive_score": result["positive"],
                        "negative_score": result["negative"],
                        "neutral_score": result["neutral"]
                    }
                })
                confidence = 0.7
                
            elif analysis_type == AnalysisType.COMMUNICATION_STYLE:
                result = analyzer.analyze_communication_style(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                content = json.dumps({
                    "style": result["style"],
                    "metrics": {
                        "question_ratio": result["question_ratio"],
                        "exclamation_ratio": result["exclamation_ratio"],
                        "avg_message_length": result["avg_message_length"]
                    }
                })
                confidence = result["confidence"]
                
            elif analysis_type == AnalysisType.RELATIONSHIP_HEALTH:
                # Basic health assessment using sentiment and patterns
                red_flags = analyzer.detect_red_flags(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                positive_indicators = analyzer.detect_positive_indicators(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                health_score = 0.5  # neutral starting point
                
                # Adjust based on positive and negative indicators
                health_score += len(positive_indicators) * 0.1
                health_score -= len(red_flags) * 0.15
                
                # Clamp to [0,1] range
                health_score = max(0.0, min(1.0, health_score))
                
                content = json.dumps({
                    "health_score": health_score,
                    "level": self._health_level_from_score(health_score),
                    "red_flags": red_flags,
                    "positive_indicators": positive_indicators
                })
                confidence = 0.6
                
            elif analysis_type == AnalysisType.CONFLICT_DETECTION:
                all_text = " ".join([c.get("text", "") for c in conversations]) if isinstance(conversations, list) else conversation_text
                sentiment = analyzer.analyze_basic_sentiment(all_text)
                red_flags = analyzer.detect_red_flags(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Basic conflict detection
                conflict_words = ["disagree", "argument", "fight", "issue", "problem", "angry", "upset"]
                conflict_count = sum(1 for word in conflict_words if word in all_text.lower())
                
                conflict_level = 0.0
                if sentiment["compound"] < -0.2:
                    conflict_level += 0.3
                    
                conflict_level += min(0.7, conflict_count * 0.1)
                conflict_level += min(0.3, len(red_flags) * 0.1)
                
                # Clamp to [0,1]
                conflict_level = max(0.0, min(1.0, conflict_level))
                
                # Detect conflict patterns with enhanced detection
                conflict_patterns = analyzer.detect_conflict_patterns(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Detect conflict types
                conflict_types = []
                
                # Common conflict types
                conflict_type_indicators = {
                    "communication": ["misunderstand", "unclear", "not listening", "didn't hear"],
                    "values": ["believe", "important", "value", "principle", "disagree with"],
                    "boundary": ["space", "privacy", "control", "freedom", "decision"],
                    "expectation": ["expect", "should", "supposed to", "disappointed"],
                    "trust": ["trust", "suspicious", "doubt", "believe you"],
                }
                
                for conflict_type, indicators in conflict_type_indicators.items():
                    if any(indicator in all_text.lower() for indicator in indicators):
                        conflict_types.append(conflict_type)
                
                content = json.dumps({
                    "conflict_detected": conflict_level > 0.4,
                    "conflict_level": conflict_level,
                    "intensity": self._intensity_from_conflict(conflict_level),
                    "topics": self._extract_conflict_topics(all_text),
                    "conflict_types": conflict_types,
                    "detected_issues": red_flags,
                    "conflict_patterns": conflict_patterns
                })
                confidence = 0.65
                
            elif analysis_type == AnalysisType.RECOMMENDATION:
                # Generate simple recommendations
                all_text = " ".join([c.get("text", "") for c in conversations]) if isinstance(conversations, list) else conversation_text
                sentiment = analyzer.analyze_basic_sentiment(all_text)
                red_flags = analyzer.detect_red_flags(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                positive_indicators = analyzer.detect_positive_indicators(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Detect topics for targeted recommendations
                topics = analyzer.detect_topics(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Analyze emotional intensity
                emotional_intensity = analyzer.analyze_emotional_intensity(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Detect conflict patterns
                conflict_patterns = analyzer.detect_conflict_patterns(conversations if isinstance(conversations, list) else [{"text": conversation_text}])
                
                # Pass to therapist for recommendations
                recommendations = therapist.generate_recommendations({
                    "sentiment": sentiment,
                    "red_flags": red_flags,
                    "positive_indicators": positive_indicators,
                    "text": all_text,
                    "topics": topics,
                    "emotional_intensity": emotional_intensity,
                    "conflict_patterns": conflict_patterns
                })
                
                # Generate emotional intensity recommendations
                emotional_recommendations = therapist.generate_emotional_intensity_recommendations(emotional_intensity)
                
                # Generate conflict-specific recommendations if conflicts are detected
                conflict_recommendations = []
                if conflict_patterns and len(conflict_patterns.get('patterns_detected', [])) > 0:
                    conflict_recommendations = therapist.generate_conflict_recommendations(conflict_patterns)
                
                # Generate strengths and areas for improvement
                strengths = therapist._identify_strengths({
                    "sentiment": sentiment,
                    "positive_indicators": positive_indicators
                })
                
                improvements = therapist._identify_improvements({
                    "sentiment": sentiment,
                    "red_flags": red_flags
                })
                
                content = json.dumps({
                    "recommendations": recommendations,
                    "emotion_specific_recommendations": emotional_recommendations,
                    "conflict_specific_recommendations": conflict_recommendations,
                    "strengths": strengths,
                    "improvements": improvements,
                    "based_on": {
                        "sentiment": sentiment["sentiment_label"],
                        "issues_detected": len(red_flags) > 0,
                        "strengths_detected": len(positive_indicators) > 0,
                        "topics_detected": topics,
                        "emotional_intensity": emotional_intensity.get("overall_intensity", "medium"),
                        "conflict_patterns_detected": len(conflict_patterns.get("patterns_detected", [])) > 0
                    }
                })
                confidence = 0.7
                
            elif analysis_type == AnalysisType.PATTERN_ANALYSIS:
                # Basic pattern analysis
                if not isinstance(conversations, list) or len(conversations) < 3:
                    content = json.dumps({"error": "Insufficient conversation data for pattern analysis"})
                    confidence = 0.3
                else:
                    # Analyze basic response patterns
                    response_times = []
                    message_lengths = []
                    
                    for i in range(1, len(conversations)):
                        if "timestamp" in conversations[i] and "timestamp" in conversations[i-1]:
                            try:
                                t1 = datetime.fromisoformat(conversations[i-1]["timestamp"])
                                t2 = datetime.fromisoformat(conversations[i]["timestamp"])
                                response_times.append((t2 - t1).total_seconds())
                            except:
                                pass
                        
                        message_lengths.append(len(conversations[i].get("text", "")))
                    
                    avg_response_time = sum(response_times) / len(response_times) if response_times else None
                    avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
                    
                    content = json.dumps({
                        "patterns": {
                            "avg_response_time_seconds": avg_response_time,
                            "avg_message_length": avg_message_length,
                            "conversation_balance": self._calculate_conversation_balance(conversations),
                            "recurring_topics": self._extract_recurring_topics(conversations),
                            "conversation_depth": "shallow" if avg_message_length < 50 else "moderate" if avg_message_length < 150 else "deep"
                        }
                    })
                    confidence = 0.7
            else:
                content = json.dumps({"error": f"Analysis type {analysis_type} not supported in local mode"})
                confidence = 0.3
                
            return AIResponse(
                content=content,
                confidence=confidence,
                metadata={"analysis_type": analysis_type},
                provider="local",
                model="minimal_implementation",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Local analysis failed: {e}")
            return AIResponse(
                content=json.dumps({"error": f"Analysis failed: {str(e)}"}),
                confidence=0.1,
                metadata={"error": str(e)},
                provider="local",
                model="error_fallback",
                timestamp=datetime.now()
            )
    
    def _build_analysis_prompt(self, 
                              conversation_text: str, 
                              analysis_type: AnalysisType,
                              context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for AI analysis"""
        
        # Convert context to formatted string if provided
        context_str = ""
        if context:
            context_str = "Additional context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            context_str += "\n"
            
        # Build specific prompts based on analysis type
        if analysis_type == AnalysisType.SENTIMENT:
            return f"""
{context_str}
Analyze the sentiment in the following conversation. Provide a comprehensive 
analysis of the emotional tone, identifying positive, negative, and neutral 
elements. Quantify the overall sentiment on a scale from -1 (very negative) 
to +1 (very positive).

Conversation:
{conversation_text}

Provide your analysis in JSON format with the following structure:
{{
  "sentiment": "positive/negative/neutral/mixed",
  "score": float,
  "details": {{
    "positive_elements": [list of positive elements found],
    "negative_elements": [list of negative elements found],
    "neutral_elements": [list of neutral elements found]
  }},
  "explanation": "brief explanation of your analysis"
}}
"""
        elif analysis_type == AnalysisType.COMMUNICATION_STYLE:
            return f"""
{context_str}
Analyze the communication style in the following conversation. Focus on patterns 
such as directness vs. indirectness, assertiveness vs. passivity, emotional expression,
listening behavior, and question-asking patterns.

Conversation:
{conversation_text}

Provide your analysis in JSON format with the following structure:
{{
  "primary_style": "descriptive label for the overall style",
  "components": {{
    "directness": float (0-1 scale),
    "assertiveness": float (0-1 scale),
    "emotional_expressiveness": float (0-1 scale),
    "active_listening": float (0-1 scale),
    "inquiry_level": float (0-1 scale)
  }},
  "patterns": [list of specific communication patterns observed],
  "suggestions": [list of suggestions for improvement]
}}
"""
        elif analysis_type == AnalysisType.RELATIONSHIP_HEALTH:
            return f"""
{context_str}
Assess the overall health of the relationship based on the following conversation.
Consider factors such as mutual respect, emotional safety, conflict resolution skills,
trust indicators, and balance in the relationship.

Conversation:
{conversation_text}

Provide your analysis in JSON format with the following structure:
{{
  "health_score": float (0-1 scale),
  "level": "descriptive label (e.g., healthy, concerning, needs work)",
  "strengths": [list of relationship strengths observed],
  "concerns": [list of relationship concerns observed],
  "recommendations": [list of specific recommendations]
}}
"""
        elif analysis_type == AnalysisType.CONFLICT_DETECTION:
            return f"""
{context_str}
Analyze the following conversation for signs of conflict. Identify the nature of any conflicts,
their intensity, potential causes, and whether they are being addressed constructively.

Conversation:
{conversation_text}

Provide your analysis in JSON format with the following structure:
{{
  "conflict_detected": boolean,
  "conflict_level": float (0-1 scale, indicating intensity),
  "topics": [list of conflict topics],
  "dynamics": [list of observed conflict dynamics],
  "resolution_attempts": [list of any resolution attempts observed],
  "recommendations": [list of conflict resolution recommendations]
}}
"""
        elif analysis_type == AnalysisType.RECOMMENDATION:
            return f"""
{context_str}
Based on the following conversation, provide specific, actionable recommendations
to improve the relationship. Consider communication patterns, emotional dynamics,
and any potential issues or strengths you observe.

Conversation:
{conversation_text}

Provide your recommendations in JSON format with the following structure:
{{
  "immediate_actions": [list of immediate steps to take],
  "communication_improvements": [list of ways to improve communication],
  "relationship_building": [list of relationship-strengthening activities],
  "individual_growth": [list of personal development suggestions],
  "reasoning": "brief explanation of the basis for these recommendations"
}}
"""
        elif analysis_type == AnalysisType.PATTERN_ANALYSIS:
            return f"""
{context_str}
Analyze the following conversation to identify recurring patterns in communication,
behavior, and emotional responses. Look for both productive and problematic patterns.

Conversation:
{conversation_text}

Provide your analysis in JSON format with the following structure:
{{
  "communication_patterns": [list of identified communication patterns],
  "emotional_patterns": [list of identified emotional response patterns],
  "behavioral_patterns": [list of identified behavioral patterns],
  "recurring_themes": [list of recurring conversation themes],
  "pattern_impact": "assessment of how these patterns affect the relationship",
  "recommendations": [list of recommendations based on pattern analysis]
}}
"""
        else:
            return f"""
{context_str}
Analyze the following conversation and provide insights:

Conversation:
{conversation_text}

Please provide a thorough analysis with specific observations and recommendations.
"""
    
    def _get_system_prompt(self, analysis_type: AnalysisType) -> str:
        """Get the appropriate system prompt for the AI"""
        
        base_prompt = """You are an expert relationship therapist AI with extensive training in psychology, 
        communication analysis, and relationship dynamics. Your task is to analyze conversations 
        and provide insightful, professional, and helpful feedback."""
        
        if analysis_type == AnalysisType.SENTIMENT:
            return base_prompt + """
            Focus on emotional content and sentiment analysis. Be precise in identifying emotional
            states, underlying feelings, and the overall emotional tone of the conversation.
            Maintain objectivity and avoid assumptions beyond what the text directly supports.
            """
        elif analysis_type == AnalysisType.COMMUNICATION_STYLE:
            return base_prompt + """
            Focus on communication patterns, styles, and effectiveness. Identify conversation dynamics,
            listening behaviors, expression clarity, and overall communication health.
            Provide specific observations about what communication approaches are working well
            and what could be improved.
            """
        elif analysis_type == AnalysisType.RELATIONSHIP_HEALTH:
            return base_prompt + """
            Assess the overall health of the relationship. Look for indicators of respect, trust,
            emotional safety, balance, and mutual support. Also identify potential red flags or
            concerning patterns that might need attention. Provide a balanced view that acknowledges
            both strengths and areas for growth.
            """
        elif analysis_type == AnalysisType.CONFLICT_DETECTION:
            return base_prompt + """
            Focus on identifying, analyzing, and providing guidance on resolving conflicts.
            Detect both explicit and implicit conflicts, assess their nature and intensity,
            and evaluate how effectively they are being addressed. Provide constructive guidance
            on healthy conflict resolution strategies.
            """
        elif analysis_type == AnalysisType.RECOMMENDATION:
            return base_prompt + """
            Your primary goal is to provide specific, actionable recommendations to improve
            the relationship. Base your recommendations on evidence from the conversation,
            and prioritize suggestions that are realistic, specific, and tailored to the
            situation. Include a mix of immediate actions and longer-term strategies.
            """
        elif analysis_type == AnalysisType.PATTERN_ANALYSIS:
            return base_prompt + """
            Focus on identifying recurring patterns in communication, behavior, and emotional
            responses. Look for both productive patterns to reinforce and problematic patterns
            that may need intervention. Consider how these patterns may have developed over time
            and how they impact the relationship dynamics.
            """
        else:
            return base_prompt
    
    def _health_level_from_score(self, score: float) -> str:
        """Convert numerical health score to descriptive level"""
        if score >= 0.8:
            return "very healthy"
        elif score >= 0.6:
            return "healthy"
        elif score >= 0.4:
            return "moderately healthy"
        elif score >= 0.2:
            return "needs attention"
        else:
            return "concerning"
    
    def _intensity_from_conflict(self, level: float) -> str:
        """Convert numerical conflict level to descriptive intensity"""
        if level >= 0.8:
            return "severe"
        elif level >= 0.6:
            return "significant"
        elif level >= 0.4:
            return "moderate"
        elif level >= 0.2:
            return "mild"
        else:
            return "minimal"
    
    def _extract_conflict_topics(self, text: str) -> List[str]:
        """Extract potential conflict topics from text"""
        topics = []
        
        # Dictionary of common relationship conflict topics and their keywords
        conflict_topics = {
            "communication": ["misunderstanding", "unclear", "didn't say", "miscommunication"],
            "trust": ["trust", "suspicious", "privacy", "secret", "honest"],
            "boundaries": ["space", "boundary", "too much", "controlling", "freedom"],
            "expectations": ["expect", "should have", "disappointed", "promised"],
            "time": ["time", "busy", "prioritize", "attention", "neglect"],
            "intimacy": ["affection", "intimate", "close", "distant", "cold"],
            "finance": ["money", "spend", "expensive", "budget", "afford"],
            "household": ["chores", "clean", "responsibility", "household", "lazy"]
        }
        
        # Check for topic keywords in the text
        for topic, keywords in conflict_topics.items():
            if any(keyword in text.lower() for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_conversation_balance(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate the balance of conversation between participants"""
        speakers = {}
        
        # Count messages and total length for each speaker
        for conv in conversations:
            speaker = conv.get("speaker", "unknown")
            text = conv.get("text", "")
            
            if speaker not in speakers:
                speakers[speaker] = {"message_count": 0, "total_length": 0}
                
            speakers[speaker]["message_count"] += 1
            speakers[speaker]["total_length"] += len(text)
        
        # Calculate percentages and average message lengths
        total_messages = sum(data["message_count"] for data in speakers.values())
        total_length = sum(data["total_length"] for data in speakers.values())
        
        result = {}
        for speaker, data in speakers.items():
            result[speaker] = {
                "message_count": data["message_count"],
                "message_percentage": data["message_count"] / total_messages if total_messages > 0 else 0,
                "avg_message_length": data["total_length"] / data["message_count"] if data["message_count"] > 0 else 0,
                "total_content_percentage": data["total_length"] / total_length if total_length > 0 else 0
            }
            
        # Calculate overall balance metrics
        if len(speakers) >= 2:
            message_counts = [data["message_count"] for data in speakers.values()]
            content_lengths = [data["total_length"] for data in speakers.values()]
            
            # Simple ratio between highest and lowest contributor
            message_ratio = max(message_counts) / min(message_counts) if min(message_counts) > 0 else float('inf')
            content_ratio = max(content_lengths) / min(content_lengths) if min(content_lengths) > 0 else float('inf')
            
            result["overall"] = {
                "message_ratio": message_ratio,
                "content_ratio": content_ratio,
                "balance_assessment": "balanced" if message_ratio < 2 and content_ratio < 3 else "somewhat imbalanced" if message_ratio < 4 and content_ratio < 6 else "highly imbalanced"
            }
        
        return result
    
    def _extract_recurring_topics(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Extract recurring topics from conversations"""
        # Combine all text
        all_text = " ".join([conv.get("text", "") for conv in conversations])
        
        # Common relationship topics and their keywords
        topics = {
            "communication": ["talk", "communication", "express", "listen", "understand"],
            "trust": ["trust", "honest", "truth", "believe", "faith"],
            "time together": ["time", "together", "spend", "activity", "date"],
            "future": ["future", "plan", "goal", "dream", "long-term"],
            "intimacy": ["love", "affection", "intimate", "close", "physical"],
            "family": ["family", "parent", "child", "relative", "in-law"],
            "friends": ["friend", "social", "hang out", "buddy", "people"],
            "work": ["work", "job", "career", "busy", "stress"],
            "finance": ["money", "financial", "spend", "save", "afford"],
            "home": ["home", "house", "chore", "clean", "space"]
        }
        
        # Check for topic prevalence
        recurring = []
        for topic, keywords in topics.items():
            # Count occurrences of keywords
            count = sum(all_text.lower().count(keyword) for keyword in keywords)
            
            # Normalize by conversation length
            frequency = count / (len(all_text) / 100)  # per 100 characters
            
            if frequency > 0.2:  # Arbitrary threshold for "recurring"
                recurring.append(topic)
        
        return recurring


# Global AI service instance
ai_service = AIService()