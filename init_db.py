#!/usr/bin/env python3
"""
Database Initialization Script
Sets up SQLite database tables for the relationship therapist system
"""

import sqlite3
import os
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database(db_path: str = "./relationship_therapist.db"):
    """
    Initialize the SQLite database with required tables
    """
    try:
        # Create database directory if it doesn't exist
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile_data TEXT,
                preferences TEXT
            )
        """)
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT,
                platform TEXT,
                conversation_data TEXT,
                analysis_results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Create analysis_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                conversation_id TEXT,
                analysis_type TEXT,
                results TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
            )
        """)
        
        # Create recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY,
                user_id TEXT,
                session_id TEXT,
                recommendation_type TEXT,
                content TEXT,
                priority INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
            )
        """)
        
        # Create reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                user_id TEXT,
                report_type TEXT,
                content TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Create knowledge_documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                document_id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                document_type TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create system_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                component TEXT,
                user_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)")
        
        # Commit changes
        conn.commit()
        
        logger.info(f"Database initialized successfully at {db_path}")
        
        # Insert some sample data for testing
        insert_sample_data(cursor)
        conn.commit()
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def insert_sample_data(cursor):
    """
    Insert sample data for testing purposes
    """
    try:
        # Sample user
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, email, profile_data)
            VALUES (?, ?, ?, ?)
        """, (
            "test_user_001",
            "test_user",
            "test@example.com",
            '{"age": 30, "relationship_status": "married", "goals": ["improve_communication"]}'
        ))
        
        # Sample knowledge document
        cursor.execute("""
            INSERT OR IGNORE INTO knowledge_documents (document_id, title, content, document_type, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "doc_001",
            "Communication Guidelines",
            "Effective communication involves active listening, empathy, and clear expression of feelings.",
            "guidance",
            '["communication", "relationships", "guidance"]'
        ))
        
        logger.info("Sample data inserted successfully")
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {str(e)}")

def check_database_health(db_path: str = "./relationship_therapist.db"):
    """
    Check database health and connectivity
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        expected_tables = {
            'users', 'conversations', 'analysis_sessions', 
            'recommendations', 'reports', 'knowledge_documents', 'system_logs'
        }
        
        existing_tables = {table[0] for table in tables}
        
        if expected_tables.issubset(existing_tables):
            logger.info("Database health check passed - all tables present")
            
            # Check record counts
            for table in expected_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"Table {table}: {count} records")
            
            conn.close()
            return True
        else:
            missing_tables = expected_tables - existing_tables
            logger.error(f"Database health check failed - missing tables: {missing_tables}")
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Initialize database
    success = init_database()
    
    if success:
        # Run health check
        check_database_health()
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
        exit(1)