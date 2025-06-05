#!/usr/bin/env python3
"""
Test System for Relationship Therapist AI
Basic functionality tests and system validation
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
SAMPLE_CONVERSATION = """
User: Hey, I've been feeling like we don't communicate well lately.
Partner: What do you mean? I think we talk all the time.
User: But when we talk about serious things, it feels like you don't really listen.
Partner: That's not true. I always listen to you.
User: See, you're getting defensive right now instead of trying to understand.
Partner: I'm not being defensive, I'm just explaining my side.
User: This is exactly what I'm talking about. Can we please just try to work on this together?
Partner: Fine, what do you want me to do?
User: I want us to both try to really hear each other when we're discussing important things.
Partner: Okay, I can try to do that. I want us to communicate better too.
"""

SAMPLE_USER_PROFILE = {
    "user_id": "test_user_123",
    "name": "Test User",
    "age": 28,
    "relationship_status": "in_relationship",
    "relationship_duration": "2_years",
    "communication_style": "direct",
    "therapy_goals": ["improve_communication", "resolve_conflicts", "build_trust"]
}

SAMPLE_KNOWLEDGE_DOCUMENT = """
Communication Best Practices for Relationships

1. Active Listening
- Give your full attention to your partner
- Avoid interrupting or planning your response while they speak
- Reflect back what you heard to ensure understanding
- Ask clarifying questions when needed

2. Use "I" Statements
- Express your feelings without blaming
- Example: "I feel hurt when..." instead of "You always..."
- Take responsibility for your emotions

3. Timing Matters
- Choose appropriate times for serious conversations
- Avoid discussing important issues when stressed or tired
- Create a safe space for dialogue

4. Validate Emotions
- Acknowledge your partner's feelings even if you disagree
- Show empathy and understanding
- Avoid dismissing or minimizing their concerns

5. Focus on Solutions
- Work together to find compromises
- Be willing to change and grow
- Celebrate progress and improvements
"""

async def test_conversation_analyzer():
    """
    Test the conversation analyzer functionality
    """
    logger.info("Testing Conversation Analyzer...")
    
    try:
        from conversation_analyzer import ConversationAnalyzer, AnalysisType
        
        analyzer = ConversationAnalyzer()
        
        # Test comprehensive analysis
        result = await analyzer.analyze_conversation(
            text=SAMPLE_CONVERSATION,
            analysis_type=AnalysisType.COMPREHENSIVE,
            user_id="test_user_123"
        )
        
        logger.info(f"Analysis completed with confidence: {result.confidence_score:.2f}")
        logger.info(f"Communication score: {result.metrics.communication_effectiveness:.2f}")
        logger.info(f"Emotional intelligence: {result.metrics.emotional_intelligence:.2f}")
        logger.info(f"Detected patterns: {len(result.patterns)}")
        
        if result.recommendations:
            logger.info("Top recommendations:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                logger.info(f"  {i}. {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"Conversation Analyzer test failed: {str(e)}")
        return False

async def test_ai_therapist():
    """
    Test the AI therapist functionality
    """
    logger.info("Testing AI Therapist...")
    
    try:
        from ai_therapist import AITherapist, TherapyApproach
        
        therapist = AITherapist()
        
        # Create user profile
        await therapist.create_user_profile(
            user_id=SAMPLE_USER_PROFILE["user_id"],
            profile_data=SAMPLE_USER_PROFILE
        )
        
        # Analyze conversation
        insights = await therapist.analyze_conversation(
            user_id=SAMPLE_USER_PROFILE["user_id"],
            conversation_text=SAMPLE_CONVERSATION,
            context={"platform": "test", "timestamp": datetime.now().isoformat()}
        )
        
        logger.info(f"Generated {len(insights)} therapeutic insights")
        
        if insights:
            insight = insights[0]
            logger.info(f"Primary insight: {insight.insight_type} (confidence: {insight.confidence:.2f})")
            logger.info(f"Description: {insight.description[:100]}...")
        
        # Generate real-time intervention
        intervention = await therapist.generate_realtime_intervention(
            user_id=SAMPLE_USER_PROFILE["user_id"],
            current_message="I'm getting frustrated with this conversation",
            conversation_context=SAMPLE_CONVERSATION
        )
        
        if intervention:
            logger.info(f"Intervention type: {intervention.intervention_type}")
            logger.info(f"Suggestion: {intervention.suggestion[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"AI Therapist test failed: {str(e)}")
        return False

async def test_data_processor():
    """
    Test the data processor functionality
    """
    logger.info("Testing Data Processor...")
    
    try:
        from data_processor import DataProcessor
        
        processor = DataProcessor()
        
        # Test text processing
        result = await processor.process_text_input(
            text=SAMPLE_CONVERSATION,
            user_id="test_user_123",
            metadata={"source": "manual_input", "timestamp": datetime.now().isoformat()}
        )
        
        logger.info(f"Processed text input: {len(result['processed_data'])} characters")
        logger.info(f"Processing status: {result['status']}")
        
        # Test JSON conversation processing
        json_data = {
            "conversation_id": "test_conv_001",
            "participants": ["User", "Partner"],
            "messages": [
                {"sender": "User", "content": "Hey, how was your day?", "timestamp": "2024-01-01T10:00:00Z"},
                {"sender": "Partner", "content": "It was good, thanks for asking!", "timestamp": "2024-01-01T10:01:00Z"}
            ]
        }
        
        json_result = await processor.process_json_conversation(
            json_data=json_data,
            user_id="test_user_123"
        )
        
        logger.info(f"Processed JSON conversation: {len(json_result['messages'])} messages")
        
        return True
        
    except Exception as e:
        logger.error(f"Data Processor test failed: {str(e)}")
        return False

async def test_knowledge_base():
    """
    Test the knowledge base functionality
    """
    logger.info("Testing Knowledge Base...")
    
    try:
        from knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        
        # Add a document
        doc_id = await kb.add_document(
            content=SAMPLE_KNOWLEDGE_DOCUMENT,
            title="Communication Best Practices",
            document_type="guidance",
            metadata={
                "author": "Test System",
                "category": "communication",
                "tags": ["communication", "relationships", "best_practices"]
            }
        )
        
        logger.info(f"Added document with ID: {doc_id}")
        
        # Search the knowledge base
        search_results = await kb.search_documents(
            query="active listening techniques",
            limit=5
        )
        
        logger.info(f"Found {len(search_results)} relevant documents")
        
        if search_results:
            top_result = search_results[0]
            logger.info(f"Top result: {top_result['title']} (score: {top_result['relevance_score']:.2f})")
        
        # Get recommendations
        recommendations = await kb.get_recommendations(
            context="communication problems",
            user_profile=SAMPLE_USER_PROFILE
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return True
        
    except Exception as e:
        logger.error(f"Knowledge Base test failed: {str(e)}")
        return False

async def test_real_time_monitor():
    """
    Test the real-time monitoring functionality
    """
    logger.info("Testing Real-time Monitor...")
    
    try:
        from real_time_monitor import RealTimeMonitor, MonitoringPlatform, LiveMessage
        
        monitor = RealTimeMonitor()
        
        # Start monitoring session
        session_id = await monitor.start_monitoring_session(
            user_id="test_user_123",
            platforms=[MonitoringPlatform.WHATSAPP, MonitoringPlatform.TELEGRAM]
        )
        
        logger.info(f"Started monitoring session: {session_id}")
        
        # Simulate live message
        live_message = LiveMessage(
            content="I'm feeling really frustrated right now",
            platform=MonitoringPlatform.WHATSAPP,
            sender="user",
            timestamp=datetime.now(),
            metadata={"conversation_id": "test_conv_001"}
        )
        
        # Process the message
        recommendations = await monitor.process_live_message(
            session_id=session_id,
            message=live_message
        )
        
        logger.info(f"Generated {len(recommendations)} real-time recommendations")
        
        if recommendations:
            rec = recommendations[0]
            logger.info(f"Top recommendation: {rec.recommendation_type} - {rec.content[:100]}...")
        
        # Stop monitoring
        await monitor.stop_monitoring_session(session_id)
        logger.info("Monitoring session stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"Real-time Monitor test failed: {str(e)}")
        return False

async def test_report_generator():
    """
    Test the report generator functionality
    """
    logger.info("Testing Report Generator...")
    
    try:
        from report_generator import ReportGenerator, ReportType, ReportFormat
        from ai_therapist import AITherapist
        from conversation_analyzer import ConversationAnalyzer
        
        # Initialize components
        therapist = AITherapist()
        analyzer = ConversationAnalyzer()
        generator = ReportGenerator(ai_therapist=therapist, conversation_analyzer=analyzer)
        
        # Create user profile for testing
        await therapist.create_user_profile(
            user_id="test_user_123",
            profile_data=SAMPLE_USER_PROFILE
        )
        
        # Generate a relationship health report
        report_result = await generator.generate_report(
            user_id="test_user_123",
            report_type=ReportType.RELATIONSHIP_HEALTH.value,
            report_format=ReportFormat.JSON.value,
            time_period="last_month"
        )
        
        logger.info(f"Generated report: {report_result['metadata']['report_id']}")
        logger.info(f"Report sections: {len(report_result['sections'])}")
        logger.info(f"Visualizations: {len(report_result['visualizations'])}")
        logger.info(f"Report saved to: {report_result['report_path']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Report Generator test failed: {str(e)}")
        return False

async def test_mcp_server():
    """
    Test the MCP server functionality
    """
    logger.info("Testing MCP Server...")
    
    try:
        from mcp_server import MCPServer, MCPMessage
        
        server = MCPServer()
        
        # Test tool call
        message = MCPMessage(
            jsonrpc="2.0",
            method="tools/call",
            params={
                "name": "analyze_conversation",
                "arguments": {
                    "text": SAMPLE_CONVERSATION,
                    "user_id": "test_user_123",
                    "analysis_type": "comprehensive"
                }
            },
            id=1
        )
        
        response = await server.handle_tool_call(message)
        
        logger.info(f"MCP tool call response: {response.get('result', {}).get('status', 'unknown')}")
        
        # Test prompt request
        prompt_message = MCPMessage(
            jsonrpc="2.0",
            method="prompts/get",
            params={
                "name": "relationship_analysis_prompt",
                "arguments": {
                    "conversation_text": SAMPLE_CONVERSATION,
                    "user_context": "couple seeking communication improvement"
                }
            },
            id=2
        )
        
        prompt_response = await server.handle_prompt_request(prompt_message)
        
        logger.info(f"MCP prompt response generated: {len(prompt_response.get('result', {}).get('messages', []))} messages")
        
        return True
        
    except Exception as e:
        logger.error(f"MCP Server test failed: {str(e)}")
        return False

async def run_system_tests():
    """
    Run all system tests
    """
    logger.info("Starting Relationship Therapist AI System Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Conversation Analyzer", test_conversation_analyzer),
        ("AI Therapist", test_ai_therapist),
        ("Data Processor", test_data_processor),
        ("Knowledge Base", test_knowledge_base),
        ("Real-time Monitor", test_real_time_monitor),
        ("Report Generator", test_report_generator),
        ("MCP Server", test_mcp_server)
    ]
    
    # Import the minimal fallback test
    try:
        from test_minimal_fallback import test_minimal_fallback
        tests.append(("Minimal Fallback System", test_minimal_fallback))
        logger.info("Added Minimal Fallback System test")
    except ImportError as e:
        logger.warning(f"Could not import minimal fallback test: {e}")
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        try:
            success = await test_func()
            results[test_name] = "PASSED" if success else "FAILED"
            logger.info(f"{test_name}: {results[test_name]}")
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)}"
            logger.error(f"{test_name}: {results[test_name]}")
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result == "PASSED")
    total = len(results)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASSED" else "✗"
        logger.info(f"{status_symbol} {test_name}: {result}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready for use.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Please check the logs above.")
    
    return results

def create_sample_files():
    """
    Create sample files for testing
    """
    logger.info("Creating sample test files...")
    
    # Create directories
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create sample conversation file
    with open(test_dir / "sample_conversation.txt", "w") as f:
        f.write(SAMPLE_CONVERSATION)
    
    # Create sample JSON conversation
    json_conversation = {
        "conversation_id": "sample_001",
        "participants": ["User", "Partner"],
        "platform": "whatsapp",
        "date": "2024-01-01",
        "messages": [
            {"sender": "User", "content": "Hey, how was your day?", "timestamp": "2024-01-01T10:00:00Z"},
            {"sender": "Partner", "content": "It was good, thanks! How about yours?", "timestamp": "2024-01-01T10:01:00Z"},
            {"sender": "User", "content": "Pretty busy, but I'm glad to be home now.", "timestamp": "2024-01-01T10:02:00Z"}
        ]
    }
    
    with open(test_dir / "sample_conversation.json", "w") as f:
        json.dump(json_conversation, f, indent=2)
    
    # Create sample knowledge document
    with open(test_dir / "sample_knowledge.txt", "w") as f:
        f.write(SAMPLE_KNOWLEDGE_DOCUMENT)
    
    logger.info(f"Sample files created in {test_dir}")

if __name__ == "__main__":
    # Create sample files
    create_sample_files()
    
    # Run tests
    results = asyncio.run(run_system_tests())
    
    # Exit with appropriate code
    passed = sum(1 for result in results.values() if result == "PASSED")
    total = len(results)
    
    if passed == total:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed