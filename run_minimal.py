#!/usr/bin/env python3
"""
Minimal Test Script for Relationship Therapist System
Tests the minimal fallback implementation
"""

import logging
import json
from minimal_implementations import MinimalConversationAnalyzer, MinimalAITherapist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_minimal_test():
    """Test the minimal implementation with a sample conversation"""
    sample_conversation = """
    Person A: I really appreciate how you helped with dinner last night. It meant a lot to me.
    Person B: Of course! I know you've been working hard. I enjoy cooking with you.
    Person A: We make a good team. I was thinking we could look at our budget this weekend?
    Person B: That's a great idea. I've been meaning to discuss our savings plan for the house.
    Person A: Perfect. I love how we're on the same page about our financial goals.
    """
    
    try:
        # Initialize components
        analyzer = MinimalConversationAnalyzer()
        therapist = MinimalAITherapist()
        
        # Test sentiment analysis
        sentiment = analyzer.analyze_basic_sentiment(sample_conversation)
        logger.info(f"Sentiment analysis: {json.dumps(sentiment)}")
        
        # Test conflict detection
        conflicts = analyzer.detect_conflict_patterns([{"text": sample_conversation}])
        logger.info(f"Conflict detection: {json.dumps(conflicts)}")
        
        # Test topic detection
        topics = analyzer.detect_topics([{"text": sample_conversation}])
        
        # Test recommendations
        recommendations = therapist.generate_recommendations({
            "sentiment": sentiment,
            "text": sample_conversation,
            "topics": topics,
            "conflict_patterns": conflicts
        })
        logger.info(f"Recommendation: {json.dumps(recommendations)}")
        
        # Test communication style analysis
        messages = [
            {"text": "I really appreciate how you helped with dinner last night. It meant a lot to me.", "sender": "Person A"},
            {"text": "Of course! I know you've been working hard. I enjoy cooking with you.", "sender": "Person B"},
            {"text": "We make a good team. I was thinking we could look at our budget this weekend?", "sender": "Person A"},
            {"text": "That's a great idea. I've been meaning to discuss our savings plan for the house.", "sender": "Person B"},
            {"text": "Perfect. I love how we're on the same page about our financial goals.", "sender": "Person A"}
        ]
        style = analyzer.analyze_communication_style(messages)
        logger.info(f"Communication style analysis: {json.dumps(style)}")
        
        # Test red flag detection
        red_flags = analyzer.detect_red_flags(messages)
        logger.info(f"Red flags: {json.dumps(red_flags)}")
        
        # Test positive indicators
        positive = analyzer.detect_positive_indicators(messages)
        logger.info(f"Positive indicators: {json.dumps(positive)}")
        
        logger.info("\n✅ Minimal implementation test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting minimal implementation test...")
    run_minimal_test()
