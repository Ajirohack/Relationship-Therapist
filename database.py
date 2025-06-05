"""Enhanced Database Service with PostgreSQL and SQLite support"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import uuid

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

from config import settings, DatabaseType

logger = logging.getLogger(__name__)

class ConversationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

@dataclass
class User:
    id: str
    email: str
    username: str
    role: UserRole
    subscription_type: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class UserProfile:
    user_id: str
    age: Optional[int] = None
    relationship_status: Optional[str] = None
    relationship_duration: Optional[str] = None
    communication_style: Optional[str] = None
    goals: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Conversation:
    id: str
    user_id: str
    title: str
    platform: str
    participants: List[str]
    message_count: int
    status: ConversationStatus
    file_path: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Message:
    id: str
    conversation_id: str
    sender: str
    content: str
    timestamp: datetime
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Report:
    id: str
    user_id: str
    report_type: str
    title: str
    content: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class DatabaseInterface:
    """Abstract database interface"""
    
    async def connect(self) -> bool:
        raise NotImplementedError
    
    async def disconnect(self):
        raise NotImplementedError
    
    async def create_tables(self) -> bool:
        raise NotImplementedError
    
    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError

class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation"""
    
    def __init__(self):
        # Extract path from database_url (remove sqlite:/// prefix)
        self.db_path = settings.database_url.replace("sqlite:///", "")
        self.connection = None
    
    async def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from SQLite database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    async def create_tables(self) -> bool:
        """Create SQLite tables"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    subscription_type TEXT DEFAULT 'free',
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    age INTEGER,
                    relationship_status TEXT,
                    relationship_duration TEXT,
                    communication_style TEXT,
                    goals TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    platform TEXT,
                    participants TEXT,
                    message_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    file_path TEXT,
                    analysis_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'generated',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Knowledge base documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    document_type TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Sessions table for authentication
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Refresh tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    revoked BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id)")
            
            self.connection.commit()
            logger.info("SQLite tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create SQLite tables: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform SQLite health check"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            return {
                "status": "healthy" if result else "unhealthy",
                "database_type": "sqlite",
                "database_path": self.db_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_type": "sqlite",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount

class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation"""
    
    def __init__(self):
        self.connection_pool = None
        self.connection_params = {
            'host': settings.postgres_host,
            'port': settings.postgres_port,
            'database': settings.postgres_db,
            'user': settings.postgres_user,
            'password': settings.postgres_password
        }
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            if asyncpg:
                self.connection_pool = await asyncpg.create_pool(
                    **self.connection_params,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("Connected to PostgreSQL database")
                return True
            else:
                logger.error("asyncpg not available for PostgreSQL connection")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from PostgreSQL database"""
        if self.connection_pool:
            await self.connection_pool.close()
            self.connection_pool = None
    
    async def create_tables(self) -> bool:
        """Create PostgreSQL tables"""
        try:
            async with self.connection_pool.acquire() as connection:
                # Users table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user',
                        subscription_type VARCHAR(50) DEFAULT 'free',
                        is_active BOOLEAN DEFAULT TRUE,
                        last_login TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # User profiles table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                        age INTEGER,
                        relationship_status VARCHAR(100),
                        relationship_duration VARCHAR(100),
                        communication_style VARCHAR(100),
                        goals JSONB,
                        preferences JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Conversations table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        platform VARCHAR(100),
                        participants JSONB,
                        message_count INTEGER DEFAULT 0,
                        status VARCHAR(50) DEFAULT 'pending',
                        file_path TEXT,
                        analysis_results JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Messages table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                        sender VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        message_type VARCHAR(50) DEFAULT 'text',
                        metadata JSONB
                    )
                """)
                
                # Reports table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        report_type VARCHAR(100) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        content JSONB NOT NULL,
                        status VARCHAR(50) DEFAULT 'generated',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Knowledge base documents table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_documents (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        document_type VARCHAR(100),
                        tags JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Sessions table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        session_token VARCHAR(255) UNIQUE NOT NULL,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Refresh tokens table
                await connection.execute("""
                    CREATE TABLE IF NOT EXISTS refresh_tokens (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        token_hash VARCHAR(255) UNIQUE NOT NULL,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        revoked BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create indexes
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports (user_id)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)")
                await connection.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id)")
                
                logger.info("PostgreSQL tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL tables: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform PostgreSQL health check"""
        try:
            async with self.connection_pool.acquire() as connection:
                result = await connection.fetchval("SELECT 1")
                
                return {
                    "status": "healthy" if result == 1 else "unhealthy",
                    "database_type": "postgresql",
                    "pool_size": self.connection_pool.get_size(),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_type": "postgresql",
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        async with self.connection_pool.acquire() as connection:
            rows = await connection.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        async with self.connection_pool.acquire() as connection:
            result = await connection.execute(query, *params)
            return int(result.split()[-1]) if result else 0

class DatabaseManager:
    """Main database manager that handles both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_type = settings.database_type
        self.database = self._initialize_database()
    
    def _initialize_database(self) -> DatabaseInterface:
        """Initialize database based on configuration"""
        if self.db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLDatabase()
        else:
            return SQLiteDatabase()
    
    async def initialize(self) -> bool:
        """Initialize database connection and create tables"""
        try:
            connected = await self.database.connect()
            if not connected:
                return False
            
            tables_created = await self.database.create_tables()
            if not tables_created:
                return False
            
            logger.info(f"Database manager initialized with {self.db_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup database resources"""
        await self.database.disconnect()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        return await self.database.health_check()
    
    # User management methods
    async def create_user(self, email: str, username: str, password_hash: str, 
                         role: UserRole = UserRole.USER, subscription_type: str = "free") -> Optional[str]:
        """Create a new user"""
        try:
            user_id = str(uuid.uuid4())
            
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    INSERT INTO users (id, email, username, password_hash, role, subscription_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                self.database.execute_update(query, (user_id, email, username, password_hash, role.value, subscription_type))
            else:
                query = """
                    INSERT INTO users (id, email, username, password_hash, role, subscription_type)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """
                await self.database.execute_update(query, (user_id, email, username, password_hash, role.value, subscription_type))
            
            logger.info(f"Created user: {username} ({email})")
            return user_id
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = "SELECT * FROM users WHERE email = ?"
                results = self.database.execute_query(query, (email,))
            else:
                query = "SELECT * FROM users WHERE email = $1"
                results = await self.database.execute_query(query, (email,))
            
            if results:
                row = results[0]
                return User(
                    id=row['id'],
                    email=row['email'],
                    username=row['username'],
                    role=UserRole(row['role']),
                    subscription_type=row['subscription_type'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row.get('last_login'),
                    is_active=row['is_active'],
                    metadata=json.loads(row['metadata']) if row.get('metadata') else None
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = "SELECT * FROM users WHERE id = ?"
                results = self.database.execute_query(query, (user_id,))
            else:
                query = "SELECT * FROM users WHERE id = $1"
                results = await self.database.execute_query(query, (user_id,))
            
            if results:
                row = results[0]
                return User(
                    id=row['id'],
                    email=row['email'],
                    username=row['username'],
                    role=UserRole(row['role']),
                    subscription_type=row['subscription_type'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row.get('last_login'),
                    is_active=row['is_active'],
                    metadata=json.loads(row['metadata']) if row.get('metadata') else None
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    async def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
                affected = self.database.execute_update(query, (user_id,))
            else:
                query = "UPDATE users SET last_login = NOW() WHERE id = $1"
                affected = await self.database.execute_update(query, (user_id,))
            
            return affected > 0
        except Exception as e:
            logger.error(f"Failed to update user last login: {e}")
            return False
    
    # User profile methods
    async def create_or_update_user_profile(self, profile: UserProfile) -> bool:
        """Create or update user profile"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, age, relationship_status, relationship_duration, communication_style, goals, preferences, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """
                params = (
                    profile.user_id,
                    profile.age,
                    profile.relationship_status,
                    profile.relationship_duration,
                    profile.communication_style,
                    json.dumps(profile.goals) if profile.goals else None,
                    json.dumps(profile.preferences) if profile.preferences else None
                )
                self.database.execute_update(query, params)
            else:
                query = """
                    INSERT INTO user_profiles 
                    (user_id, age, relationship_status, relationship_duration, communication_style, goals, preferences)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (user_id) DO UPDATE SET
                        age = EXCLUDED.age,
                        relationship_status = EXCLUDED.relationship_status,
                        relationship_duration = EXCLUDED.relationship_duration,
                        communication_style = EXCLUDED.communication_style,
                        goals = EXCLUDED.goals,
                        preferences = EXCLUDED.preferences,
                        updated_at = NOW()
                """
                params = (
                    profile.user_id,
                    profile.age,
                    profile.relationship_status,
                    profile.relationship_duration,
                    profile.communication_style,
                    profile.goals,
                    profile.preferences
                )
                await self.database.execute_update(query, params)
            
            return True
        except Exception as e:
            logger.error(f"Failed to create/update user profile: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = "SELECT * FROM user_profiles WHERE user_id = ?"
                results = self.database.execute_query(query, (user_id,))
            else:
                query = "SELECT * FROM user_profiles WHERE user_id = $1"
                results = await self.database.execute_query(query, (user_id,))
            
            if results:
                row = results[0]
                return UserProfile(
                    user_id=row['user_id'],
                    age=row.get('age'),
                    relationship_status=row.get('relationship_status'),
                    relationship_duration=row.get('relationship_duration'),
                    communication_style=row.get('communication_style'),
                    goals=json.loads(row['goals']) if row.get('goals') else None,
                    preferences=json.loads(row['preferences']) if row.get('preferences') else None,
                    created_at=row.get('created_at'),
                    updated_at=row.get('updated_at')
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    # Conversation methods
    async def create_conversation(self, conversation: Conversation) -> Optional[str]:
        """Create a new conversation"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    INSERT INTO conversations 
                    (id, user_id, title, platform, participants, message_count, status, file_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    conversation.id,
                    conversation.user_id,
                    conversation.title,
                    conversation.platform,
                    json.dumps(conversation.participants),
                    conversation.message_count,
                    conversation.status.value,
                    conversation.file_path,
                    json.dumps(conversation.metadata) if conversation.metadata else None
                )
                self.database.execute_update(query, params)
            else:
                query = """
                    INSERT INTO conversations 
                    (id, user_id, title, platform, participants, message_count, status, file_path, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """
                params = (
                    conversation.id,
                    conversation.user_id,
                    conversation.title,
                    conversation.platform,
                    conversation.participants,
                    conversation.message_count,
                    conversation.status.value,
                    conversation.file_path,
                    conversation.metadata
                )
                await self.database.execute_update(query, params)
            
            return conversation.id
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None
    
    async def get_user_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """Get user's conversations"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    SELECT * FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                results = self.database.execute_query(query, (user_id, limit, offset))
            else:
                query = """
                    SELECT * FROM conversations 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2 OFFSET $3
                """
                results = await self.database.execute_query(query, (user_id, limit, offset))
            
            conversations = []
            for row in results:
                conversations.append(Conversation(
                    id=row['id'],
                    user_id=row['user_id'],
                    title=row['title'],
                    platform=row.get('platform'),
                    participants=json.loads(row['participants']) if row.get('participants') else [],
                    message_count=row['message_count'],
                    status=ConversationStatus(row['status']),
                    file_path=row.get('file_path'),
                    analysis_results=json.loads(row['analysis_results']) if row.get('analysis_results') else None,
                    created_at=row.get('created_at'),
                    updated_at=row.get('updated_at'),
                    metadata=json.loads(row['metadata']) if row.get('metadata') else None
                ))
            
            return conversations
        except Exception as e:
            logger.error(f"Failed to get user conversations: {e}")
            return []
    
    async def update_conversation_analysis(self, conversation_id: str, analysis_results: Dict[str, Any]) -> bool:
        """Update conversation analysis results"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    UPDATE conversations 
                    SET analysis_results = ?, status = 'completed', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """
                affected = self.database.execute_update(query, (json.dumps(analysis_results), conversation_id))
            else:
                query = """
                    UPDATE conversations 
                    SET analysis_results = $1, status = 'completed', updated_at = NOW() 
                    WHERE id = $2
                """
                affected = await self.database.execute_update(query, (analysis_results, conversation_id))
            
            return affected > 0
        except Exception as e:
            logger.error(f"Failed to update conversation analysis: {e}")
            return False
    
    # Report methods
    async def create_report(self, report: Report) -> Optional[str]:
        """Create a new report"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    INSERT INTO reports (id, user_id, report_type, title, content, status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    report.id,
                    report.user_id,
                    report.report_type,
                    report.title,
                    json.dumps(report.content),
                    report.status,
                    json.dumps(report.metadata) if report.metadata else None
                )
                self.database.execute_update(query, params)
            else:
                query = """
                    INSERT INTO reports (id, user_id, report_type, title, content, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """
                params = (
                    report.id,
                    report.user_id,
                    report.report_type,
                    report.title,
                    report.content,
                    report.status,
                    report.metadata
                )
                await self.database.execute_update(query, params)
            
            return report.id
        except Exception as e:
            logger.error(f"Failed to create report: {e}")
            return None
    
    async def get_user_reports(self, user_id: str, limit: int = 20) -> List[Report]:
        """Get user's reports"""
        try:
            if isinstance(self.database, SQLiteDatabase):
                query = """
                    SELECT * FROM reports 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                results = self.database.execute_query(query, (user_id, limit))
            else:
                query = """
                    SELECT * FROM reports 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """
                results = await self.database.execute_query(query, (user_id, limit))
            
            reports = []
            for row in results:
                reports.append(Report(
                    id=row['id'],
                    user_id=row['user_id'],
                    report_type=row['report_type'],
                    title=row['title'],
                    content=json.loads(row['content']) if isinstance(row['content'], str) else row['content'],
                    status=row['status'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=json.loads(row['metadata']) if row.get('metadata') and isinstance(row['metadata'], str) else row.get('metadata')
                ))
            
            return reports
        except Exception as e:
            logger.error(f"Failed to get user reports: {e}")
            return []

# Global database manager instance
database_manager = DatabaseManager()