#!/usr/bin/env python3
"""
Test script for minimal implementation fallback
"""

import asyncio
import logging
from ai_service import AIService, AnalysisType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_local_fallback():
    """Test the local fallback implementation"""
    service = AIService()
    
    # Sample conversation
    conversation = """
Person A: I really appreciate how you've been helping with the chores lately.
Person B: Thanks! I'm trying to be better about that.
Person A: It makes me feel like we're a team.
Person B: I feel the same way. Though I was wondering if we could talk about our budget soon?
Person A: Sure, I've been meaning to bring that up too.
"""
    
    # Test sentiment analysis
    sentiment_result = await service._analyze_locally(
        conversation_text=conversation,
        analysis_type=AnalysisType.SENTIMENT
    )
    logger.info(f"Sentiment analysis: {sentiment_result.content}")
    
    # Test conflict detection
    conflict_result = await service._analyze_locally(
        conversation_text=conversation,
        analysis_type=AnalysisType.CONFLICT_DETECTION
    )
    logger.info(f"Conflict detection: {conflict_result.content}")
    
    # Test recommendation
    recommendation_result = await service._analyze_locally(
        conversation_text=conversation,
        analysis_type=AnalysisType.RECOMMENDATION
    )
    logger.info(f"Recommendation: {recommendation_result.content}")
    
    # Test pattern analysis
    pattern_result = await service._analyze_locally(
        conversation_text=conversation,
        analysis_type=AnalysisType.PATTERN_ANALYSIS
    )
    logger.info(f"Pattern analysis: {pattern_result.content}")

if __name__ == "__main__":
    asyncio.run(test_local_fallback())
