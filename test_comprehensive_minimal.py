#!/usr/bin/env python3
"""
Comprehensive Test for Minimal Fallback System
Tests all aspects of the minimal implementation for relationship therapy
"""

import asyncio
import logging
import json
from ai_service import AIService, AnalysisType
from minimal_implementations import MinimalConversationAnalyzer, MinimalAITherapist

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_sentiment_analysis():
    """Test the sentiment analysis functionality"""
    analyzer = MinimalConversationAnalyzer()
    
    # Test positive sentiment
    positive_text = "I really love how we've been communicating lately. It makes me feel appreciated and understood."
    positive_result = analyzer.analyze_basic_sentiment(positive_text)
    logger.info(f"Positive sentiment test: {positive_result}")
    
    # Test negative sentiment
    negative_text = "I hate when you ignore me. It's frustrating and makes me feel worthless."
    negative_result = analyzer.analyze_basic_sentiment(negative_text)
    logger.info(f"Negative sentiment test: {negative_result}")
    
    # Test neutral sentiment
    neutral_text = "We need to discuss our schedule for next week. I have some appointments on Tuesday."
    neutral_result = analyzer.analyze_basic_sentiment(neutral_text)
    logger.info(f"Neutral sentiment test: {neutral_result}")
    
    logger.info("Sentiment analysis test completed")

async def test_conflict_pattern_detection():
    """Test conflict pattern detection"""
    analyzer = MinimalConversationAnalyzer()
    
    # Sample conversation with conflict patterns
    conflict_conversation = [
        {"text": "You never listen to what I say. You always ignore my feelings."},
        {"text": "That's not true! It's not my fault you don't communicate clearly."},
        {"text": "Whatever. This is ridiculous. I don't even want to talk about this anymore."},
        {"text": "Fine. Forget it then."}
    ]
    
    patterns = analyzer.detect_conflict_patterns(conflict_conversation)
    logger.info(f"Conflict patterns detected: {json.dumps(patterns, indent=2)}")
    
    logger.info("Conflict pattern detection test completed")

async def test_emotional_intensity_analysis():
    """Test emotional intensity analysis"""
    analyzer = MinimalConversationAnalyzer()
    
    # Sample conversation with varying emotional intensity
    emotional_conversation = [
        {"text": "I am absolutely furious about what happened yesterday!"},
        {"text": "I feel very disappointed that you didn't call me."},
        {"text": "I'm somewhat concerned about our financial situation."},
        {"text": "I love you so much and I'm extremely happy we're together."}
    ]
    
    intensity = analyzer.analyze_emotional_intensity(emotional_conversation)
    logger.info(f"Emotional intensity analysis: {json.dumps(intensity, indent=2)}")
    
    logger.info("Emotional intensity analysis test completed")

async def test_topic_detection():
    """Test topic detection"""
    analyzer = MinimalConversationAnalyzer()
    
    # Test different topics
    financial_conversation = [
        {"text": "We need to talk about our budget. I'm worried about our spending."},
        {"text": "I think we should save more money for our future."}
    ]
    
    family_conversation = [
        {"text": "Your parents are visiting next week. How should we prepare?"},
        {"text": "I think the kids need more structure and consistent rules."}
    ]
    
    communication_conversation = [
        {"text": "I feel like we don't talk enough about important things."},
        {"text": "Can we have a conversation about our relationship goals?"}
    ]
    
    financial_topics = analyzer.detect_topics(financial_conversation)
    family_topics = analyzer.detect_topics(family_conversation)
    communication_topics = analyzer.detect_topics(communication_conversation)
    
    logger.info(f"Financial conversation topics: {financial_topics}")
    logger.info(f"Family conversation topics: {family_topics}")
    logger.info(f"Communication conversation topics: {communication_topics}")
    
    logger.info("Topic detection test completed")

async def test_recommendation_generation():
    """Test recommendation generation"""
    therapist = MinimalAITherapist()
    analyzer = MinimalConversationAnalyzer()
    
    # Sample conversation
    conversation = [
        {"text": "I feel like you don't listen to me sometimes."},
        {"text": "That's not fair. I do listen, but you always criticize me."},
        {"text": "See? You're getting defensive instead of trying to understand."},
        {"text": "Fine. Whatever. I don't want to talk about this anymore."}
    ]
    
    # Analyze the conversation
    all_text = " ".join([c["text"] for c in conversation])
    sentiment = analyzer.analyze_basic_sentiment(all_text)
    red_flags = analyzer.detect_red_flags(conversation)
    positive_indicators = analyzer.detect_positive_indicators(conversation)
    topics = analyzer.detect_topics(conversation)
    emotional_intensity = analyzer.analyze_emotional_intensity(conversation)
    conflict_patterns = analyzer.detect_conflict_patterns(conversation)
    
    # Generate recommendations
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
    
    # Generate conflict recommendations
    conflict_recommendations = therapist.generate_conflict_recommendations(conflict_patterns)
    
    logger.info(f"General recommendations: {json.dumps(recommendations, indent=2)}")
    logger.info(f"Emotional intensity recommendations: {json.dumps(emotional_recommendations, indent=2)}")
    logger.info(f"Conflict recommendations: {json.dumps(conflict_recommendations, indent=2)}")
    
    logger.info("Recommendation generation test completed")

async def test_local_ai_service():
    """Test the local AI service fallback"""
    service = AIService()
    
    # Sample conversation with mixed emotions and conflicts
    conversation = """
Person A: I'm really upset that you forgot our anniversary again.
Person B: I didn't forget! I've just been extremely busy with work. You always exaggerate everything.
Person A: You never prioritize our relationship. It's always work first.
Person B: That's not fair. I'm working hard for us. You don't appreciate what I do.
Person A: Maybe if you communicated better about your schedule, I wouldn't feel so neglected.
Person B: Fine. Whatever. I don't want to talk about this anymore.
"""
    
    # Test all analysis types
    for analysis_type in [
        AnalysisType.SENTIMENT, 
        AnalysisType.CONFLICT_DETECTION, 
        AnalysisType.RECOMMENDATION,
        AnalysisType.COMMUNICATION_STYLE,
        AnalysisType.RELATIONSHIP_HEALTH
    ]:
        result = await service._analyze_locally(
            conversation_text=conversation,
            analysis_type=analysis_type
        )
        logger.info(f"{analysis_type.value} analysis: {result.content}")
    
    logger.info("Local AI service test completed")

async def main():
    """Run all tests"""
    logger.info("Starting comprehensive minimal fallback system tests")
    
    # Run all tests
    await test_sentiment_analysis()
    await test_conflict_pattern_detection()
    await test_emotional_intensity_analysis()
    await test_topic_detection()
    await test_recommendation_generation()
    await test_local_ai_service()
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    asyncio.run(main())
