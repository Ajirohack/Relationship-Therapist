async def test_minimal_fallback():
    """
    Test the minimal fallback implementation for when AI services are unavailable
    """
    logger.info("Testing minimal fallback implementation...")
    
    try:
        from ai_service import AIService, AnalysisType
        from minimal_implementations import MinimalConversationAnalyzer, MinimalAITherapist
        
        # Initialize components
        service = AIService()
        
        # Test sentiment analysis
        sentiment_result = await service._analyze_locally(
            conversation_text=SAMPLE_CONVERSATION,
            analysis_type=AnalysisType.SENTIMENT
        )
        logger.info(f"Minimal fallback sentiment analysis: {sentiment_result.provider}")
        
        # Verify result contains expected fields
        sentiment_data = json.loads(sentiment_result.content)
        assert "sentiment" in sentiment_data, "Missing sentiment field"
        assert "score" in sentiment_data, "Missing score field"
        
        # Test conflict detection
        conflict_result = await service._analyze_locally(
            conversation_text=SAMPLE_CONVERSATION,
            analysis_type=AnalysisType.CONFLICT_DETECTION
        )
        conflict_data = json.loads(conflict_result.content)
        assert "conflict_detected" in conflict_data, "Missing conflict_detected field"
        assert "conflict_patterns" in conflict_data, "Missing conflict_patterns field"
        
        # Test emotional analysis with the MinimalConversationAnalyzer directly
        analyzer = MinimalConversationAnalyzer()
        emotional_intensity = analyzer.analyze_emotional_intensity([{"text": SAMPLE_CONVERSATION}])
        assert "overall_intensity" in emotional_intensity, "Missing overall_intensity field"
        assert "primary_emotions" in emotional_intensity, "Missing primary_emotions field"
        
        # Test recommendation generation with advanced features
        therapist = MinimalAITherapist()
        all_text = SAMPLE_CONVERSATION
        sentiment = analyzer.analyze_basic_sentiment(all_text)
        topics = analyzer.detect_topics([{"text": all_text}])
        conflict_patterns = analyzer.detect_conflict_patterns([{"text": all_text}])
        
        recommendations = therapist.generate_recommendations({
            "sentiment": sentiment,
            "text": all_text,
            "topics": topics,
            "emotional_intensity": emotional_intensity,
            "conflict_patterns": conflict_patterns
        })
        
        assert len(recommendations) > 0, "No recommendations generated"
        
        logger.info("Minimal fallback implementation test PASSED")
        return True
    except Exception as e:
        logger.error(f"Minimal fallback implementation test FAILED: {e}")
        return False
