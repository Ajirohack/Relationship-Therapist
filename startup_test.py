#!/usr/bin/env python3
"""
Startup Test Script
Tests all system components and verifies readiness for E2E testing
"""

import os
import sys
import logging
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """
    Check if all required environment variables and files are present
    """
    logger.info("Checking environment setup...")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        logger.error(".env file not found")
        return False
    
    # Check database
    db_file = Path('relationship_therapist.db')
    if not db_file.exists():
        logger.error("Database file not found")
        return False
    
    # Check required directories
    required_dirs = [
        'knowledge_base/documents',
        'reports/generated',
        'models',
        'data/uploads'
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            logger.error(f"Required directory not found: {dir_path}")
            return False
    
    logger.info("Environment setup check passed")
    return True

def test_imports():
    """
    Test if all required modules can be imported
    """
    logger.info("Testing module imports...")
    
    try:
        # Test core modules
        import main
        import conversation_analyzer
        import data_processor
        import ai_therapist
        import knowledge_base
        import report_generator
        import real_time_monitor
        import mcp_server
        import minimal_implementations
        
        logger.info("All core modules imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        return False

def test_database_connectivity():
    """
    Test database connectivity and basic operations
    """
    logger.info("Testing database connectivity...")
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('relationship_therapist.db')
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_documents")
        doc_count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"Database connectivity test passed - Users: {user_count}, Documents: {doc_count}")
        return True
        
    except Exception as e:
        logger.error(f"Database connectivity test failed: {e}")
        return False

def test_minimal_implementations():
    """
    Test the minimal implementations
    """
    logger.info("Testing minimal implementations...")
    
    try:
        from minimal_implementations import (
            MinimalConversationAnalyzer,
            MinimalAITherapist,
            MinimalKnowledgeBase,
            create_minimal_analysis_result
        )
        
        # Test conversation analyzer
        analyzer = MinimalConversationAnalyzer()
        sentiment = analyzer.analyze_basic_sentiment("I love you so much!")
        assert sentiment['sentiment_label'] == 'positive'
        
        # Test AI therapist
        therapist = MinimalAITherapist()
        mock_analysis = {
            'emotional_analysis': {'sentiment_label': 'positive'},
            'red_flags': [],
            'positive_indicators': ['love detected']
        }
        recommendations = therapist.generate_recommendations(mock_analysis)
        assert len(recommendations) > 0
        
        # Test knowledge base
        kb = MinimalKnowledgeBase()
        tips = kb.get_guidance('communication_tips')
        assert len(tips) > 0
        
        # Test complete analysis
        sample_conversations = [
            {'text': 'I love spending time with you', 'sender': 'user1'},
            {'text': 'You make me happy!', 'sender': 'user2'}
        ]
        result = create_minimal_analysis_result('test_user', sample_conversations)
        assert 'overall_score' in result
        assert 'recommendations' in result
        
        logger.info("Minimal implementations test passed")
        return True
        
    except Exception as e:
        logger.error(f"Minimal implementations test failed: {e}")
        return False

async def test_core_components():
    """
    Test core system components
    """
    logger.info("Testing core components...")
    
    try:
        # Test conversation analyzer
        from conversation_analyzer import ConversationAnalyzer
        analyzer = ConversationAnalyzer()
        
        # Test data processor
        from data_processor import DataProcessor
        processor = DataProcessor()
        
        # Test AI therapist
        from ai_therapist import AITherapist
        therapist = AITherapist()
        
        # Test knowledge base
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        
        logger.info("Core components initialization test passed")
        return True
        
    except Exception as e:
        logger.error(f"Core components test failed: {e}")
        return False

def test_api_endpoints():
    """
    Test if the FastAPI application can be imported and configured
    """
    logger.info("Testing API endpoints configuration...")
    
    try:
        from main import app
        
        # Check if app is properly configured
        assert app is not None
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = [
            '/api/v1/upload/conversation',
            '/api/v1/analyze/conversation',
            '/api/v1/realtime/recommendation',
            '/api/v1/user/profile'
        ]
        
        for route in expected_routes:
            if route not in routes:
                logger.warning(f"Expected route not found: {route}")
        
        logger.info("API endpoints configuration test passed")
        return True
        
    except Exception as e:
        logger.error(f"API endpoints test failed: {e}")
        return False

def create_test_data():
    """
    Create some test data for E2E testing
    """
    logger.info("Creating test data...")
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('relationship_therapist.db')
        cursor = conn.cursor()
        
        # Insert test conversation
        test_conversation = {
            'conversation_id': 'test_conv_001',
            'user_id': 'test_user_001',
            'platform': 'test',
            'conversation_data': json.dumps([
                {'text': 'I love spending time with you', 'sender': 'user1', 'timestamp': '2024-01-01'},
                {'text': 'You make me so happy!', 'sender': 'user2', 'timestamp': '2024-01-01'},
                {'text': 'I appreciate how you listen to me', 'sender': 'user1', 'timestamp': '2024-01-01'}
            ]),
            'created_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO conversations 
            (conversation_id, user_id, platform, conversation_data, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            test_conversation['conversation_id'],
            test_conversation['user_id'],
            test_conversation['platform'],
            test_conversation['conversation_data'],
            test_conversation['created_at']
        ))
        
        # Insert additional knowledge document
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_documents 
            (document_id, title, content, document_type, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'test_doc_001',
            'Test Relationship Advice',
            'This is test content for relationship guidance.',
            'guidance',
            json.dumps(['test', 'guidance']),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("Test data created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test data creation failed: {e}")
        return False

def run_comprehensive_test():
    """
    Run comprehensive system test
    """
    logger.info("Starting comprehensive system test...")
    
    test_results = {
        'environment_check': check_environment(),
        'imports_test': test_imports(),
        'database_connectivity': test_database_connectivity(),
        'minimal_implementations': test_minimal_implementations(),
        'api_endpoints': test_api_endpoints(),
        'test_data_creation': create_test_data()
    }
    
    # Run async tests
    try:
        loop = asyncio.get_event_loop()
        test_results['core_components'] = loop.run_until_complete(test_core_components())
    except Exception as e:
        logger.error(f"Async tests failed: {e}")
        test_results['core_components'] = False
    
    # Summary
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    logger.info(f"\n{'='*50}")
    logger.info("SYSTEM TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 System is ready for E2E testing!")
        return True
    else:
        logger.warning("⚠️  Some tests failed. Please address issues before E2E testing.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)