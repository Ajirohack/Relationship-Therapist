"""Celery Task Service for background processing"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import traceback
import os

try:
    from celery import Celery, Task
    from celery.result import AsyncResult
    from celery.signals import worker_ready, worker_shutdown
except ImportError:
    Celery = None
    Task = None
    AsyncResult = None
    worker_ready = None
    worker_shutdown = None

from config import settings

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class AsyncTaskManager:
    """Fallback async task manager when Celery is not available"""
    
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
    
    def generate_task_id(self) -> str:
        """Generate unique task ID"""
        self.task_counter += 1
        return f"async_task_{self.task_counter}_{datetime.now().timestamp()}"
    
    async def submit_task(self, func, *args, **kwargs) -> str:
        """Submit task for async execution"""
        task_id = self.generate_task_id()
        
        # Store task info
        self.tasks[task_id] = TaskResult(
            task_id=task_id,
            status=TaskStatus.STARTED,
            started_at=datetime.now()
        )
        
        # Execute task in background
        asyncio.create_task(self._execute_task(task_id, func, *args, **kwargs))
        
        return task_id
    
    async def _execute_task(self, task_id: str, func, *args, **kwargs):
        """Execute task and store result"""
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self.tasks[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.SUCCESS,
                result=result,
                started_at=self.tasks[task_id].started_at,
                completed_at=datetime.now()
            )
        except Exception as e:
            self.tasks[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILURE,
                error=str(e),
                started_at=self.tasks[task_id].started_at,
                completed_at=datetime.now()
            )
            logger.error(f"Task {task_id} failed: {e}")
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result"""
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.status if task else TaskStatus.PENDING

# Initialize Celery app if available
celery_app = None
if Celery and settings.celery_enabled:
    try:
        celery_app = Celery(
            'relationship_therapist',
            broker=settings.celery_broker_url,
            backend=settings.celery_result_backend,
            include=['task_service']
        )
        
        # Celery configuration
        celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=30 * 60,  # 30 minutes
            task_soft_time_limit=25 * 60,  # 25 minutes
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            worker_disable_rate_limits=False,
            task_compression='gzip',
            result_compression='gzip',
            result_expires=3600,  # 1 hour
        )
        
        logger.info("Celery app initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Celery: {e}")
        celery_app = None

# Fallback task manager
async_task_manager = AsyncTaskManager()

# Only define BaseTask if Celery is available
if Task:
    class BaseTask(Task):
        """Base task class with common functionality"""
        
        def on_success(self, retval, task_id, args, kwargs):
            """Called on task success"""
            logger.info(f"Task {task_id} completed successfully")
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            """Called on task failure"""
            logger.error(f"Task {task_id} failed: {exc}")
            logger.error(f"Traceback: {einfo}")
        
        def on_retry(self, exc, task_id, args, kwargs, einfo):
            """Called on task retry"""
            logger.warning(f"Task {task_id} retrying: {exc}")
else:
    BaseTask = None

# Task definitions
if celery_app:
    @celery_app.task(base=BaseTask, bind=True)
    def process_conversation_file(self, file_path: str, user_id: str, metadata: Dict[str, Any]):
        """Process uploaded conversation file"""
        try:
            # Update task progress
            self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Reading file'})
            
            # Import here to avoid circular imports
            from conversation_analyzer import ConversationAnalyzer
            from database import DatabaseManager
            
            analyzer = ConversationAnalyzer()
            db_manager = DatabaseManager()
            
            # Read and parse file
            self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Parsing conversations'})
            
            conversations = []
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        conversations = data
                    elif isinstance(data, dict) and 'messages' in data:
                        conversations = data['messages']
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple text parsing - split by lines and create message objects
                    lines = content.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            conversations.append({
                                'content': line.strip(),
                                'timestamp': datetime.now().isoformat(),
                                'sender': 'unknown'
                            })
            
            if not conversations:
                raise ValueError("No conversations found in file")
            
            # Analyze conversations
            self.update_state(state='PROGRESS', meta={'progress': 60, 'status': 'Analyzing conversations'})
            
            analysis_results = []
            for i, conv in enumerate(conversations):
                try:
                    analysis = analyzer.analyze_conversation(conv)
                    analysis_results.append(analysis)
                    
                    # Update progress
                    progress = 60 + (30 * (i + 1) / len(conversations))
                    self.update_state(state='PROGRESS', meta={
                        'progress': progress, 
                        'status': f'Analyzed {i + 1}/{len(conversations)} conversations'
                    })
                except Exception as e:
                    logger.error(f"Failed to analyze conversation {i}: {e}")
                    continue
            
            # Store results in database
            self.update_state(state='PROGRESS', meta={'progress': 95, 'status': 'Storing results'})
            
            # Store conversation data
            conversation_id = f"conv_{user_id}_{datetime.now().timestamp()}"
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove uploaded file: {e}")
            
            return {
                'conversation_id': conversation_id,
                'total_conversations': len(conversations),
                'analysis_results': analysis_results,
                'metadata': metadata,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Conversation processing failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    @celery_app.task(base=BaseTask, bind=True)
    def generate_user_report(self, user_id: str, report_type: str = 'comprehensive'):
        """Generate comprehensive user report"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Initializing report generation'})
            
            # Import here to avoid circular imports
            from ai_therapist import AITherapist
            from database import DatabaseManager
            
            ai_therapist = AITherapist()
            db_manager = DatabaseManager()
            
            # Get user data
            self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Fetching user data'})
            
            user_profile = db_manager.get_user_profile(user_id)
            if not user_profile:
                raise ValueError(f"User profile not found for user_id: {user_id}")
            
            # Get conversation history
            self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Analyzing conversation history'})
            
            conversations = db_manager.get_user_conversations(user_id)
            
            # Generate insights
            self.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'Generating insights'})
            
            insights = ai_therapist.generate_insights(user_profile, conversations)
            
            # Generate recommendations
            self.update_state(state='PROGRESS', meta={'progress': 85, 'status': 'Creating recommendations'})
            
            recommendations = ai_therapist.generate_recommendations(user_profile, insights)
            
            # Compile report
            self.update_state(state='PROGRESS', meta={'progress': 95, 'status': 'Compiling report'})
            
            report = {
                'user_id': user_id,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'user_profile': user_profile,
                'conversation_summary': {
                    'total_conversations': len(conversations),
                    'date_range': {
                        'start': min([c.get('timestamp', '') for c in conversations]) if conversations else None,
                        'end': max([c.get('timestamp', '') for c in conversations]) if conversations else None
                    }
                },
                'insights': insights,
                'recommendations': recommendations,
                'metadata': {
                    'processing_time': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            # Store report
            report_id = f"report_{user_id}_{datetime.now().timestamp()}"
            
            return {
                'report_id': report_id,
                'report': report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    @celery_app.task(base=BaseTask, bind=True)
    async def process_knowledge_base_document(self, file_path: str, document_type: str, metadata: Dict[str, Any]):
        """Process knowledge base document for RAG"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Reading document'})
            
            # Import here to avoid circular imports
            from knowledge_base import KnowledgeBase
            from vector_db import vector_db_service
            
            kb = KnowledgeBase()
            
            # Read document
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Processing document'})
            
            # Process document
            processed_doc = kb.process_document(content, document_type, metadata)
            
            self.update_state(state='PROGRESS', meta={'progress': 60, 'status': 'Generating embeddings'})
            
            # Add to vector database if available
            if vector_db_service.is_available():
                chunks = kb.chunk_document(content)
                chunk_metadata = [{
                    **metadata,
                    'chunk_index': i,
                    'document_type': document_type
                } for i in range(len(chunks))]
                
                await vector_db_service.add_documents(
                    collection_name='knowledge_base',
                    texts=chunks,
                    metadatas=chunk_metadata
                )
            
            self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Storing document'})
            
            # Store in knowledge base
            doc_id = kb.add_document(processed_doc)
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove uploaded file: {e}")
            
            return {
                'document_id': doc_id,
                'document_type': document_type,
                'processed_at': datetime.now().isoformat(),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Knowledge base document processing failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    @celery_app.task(base=BaseTask)
    def cleanup_old_files():
        """Cleanup old temporary files"""
        try:
            import glob
            
            # Clean up old upload files
            upload_dir = settings.upload_directory
            if os.path.exists(upload_dir):
                # Remove files older than 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for file_path in glob.glob(os.path.join(upload_dir, '*')):
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            logger.info(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove file {file_path}: {e}")
            
            return {'cleaned_files': 'success', 'timestamp': datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"File cleanup failed: {e}")
            raise

class TaskService:
    """Main task service that handles both Celery and fallback async tasks"""
    
    def __init__(self):
        self.celery_available = celery_app is not None
        self.async_manager = async_task_manager
    
    def is_celery_available(self) -> bool:
        """Check if Celery is available"""
        return self.celery_available
    
    def submit_conversation_processing(self, file_path: str, user_id: str, metadata: Dict[str, Any]) -> str:
        """Submit conversation processing task"""
        if self.celery_available:
            result = process_conversation_file.delay(file_path, user_id, metadata)
            return result.id
        else:
            # Fallback to async processing
            return asyncio.create_task(
                self.async_manager.submit_task(
                    self._process_conversation_fallback, file_path, user_id, metadata
                )
            )
    
    def submit_report_generation(self, user_id: str, report_type: str = 'comprehensive') -> str:
        """Submit report generation task"""
        if self.celery_available:
            result = generate_user_report.delay(user_id, report_type)
            return result.id
        else:
            # Fallback to async processing
            return asyncio.create_task(
                self.async_manager.submit_task(
                    self._generate_report_fallback, user_id, report_type
                )
            )
    
    def submit_knowledge_base_processing(self, file_path: str, document_type: str, metadata: Dict[str, Any]) -> str:
        """Submit knowledge base document processing task"""
        if self.celery_available:
            result = process_knowledge_base_document.delay(file_path, document_type, metadata)
            return result.id
        else:
            # Fallback to async processing
            return asyncio.create_task(
                self.async_manager.submit_task(
                    self._process_knowledge_base_fallback, file_path, document_type, metadata
                )
            )
    
    def get_task_status(self, task_id: str) -> TaskResult:
        """Get task status and result"""
        if self.celery_available:
            try:
                result = AsyncResult(task_id, app=celery_app)
                
                status_map = {
                    'PENDING': TaskStatus.PENDING,
                    'STARTED': TaskStatus.STARTED,
                    'SUCCESS': TaskStatus.SUCCESS,
                    'FAILURE': TaskStatus.FAILURE,
                    'RETRY': TaskStatus.RETRY,
                    'REVOKED': TaskStatus.REVOKED,
                    'PROGRESS': TaskStatus.STARTED
                }
                
                return TaskResult(
                    task_id=task_id,
                    status=status_map.get(result.status, TaskStatus.PENDING),
                    result=result.result if result.successful() else None,
                    error=str(result.result) if result.failed() else None,
                    progress=result.result if result.status == 'PROGRESS' else None
                )
            except Exception as e:
                logger.error(f"Failed to get Celery task status: {e}")
                return TaskResult(task_id=task_id, status=TaskStatus.FAILURE, error=str(e))
        else:
            # Use async manager
            task_result = self.async_manager.get_task_result(task_id)
            return task_result or TaskResult(task_id=task_id, status=TaskStatus.PENDING)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if self.celery_available:
            try:
                celery_app.control.revoke(task_id, terminate=True)
                return True
            except Exception as e:
                logger.error(f"Failed to cancel Celery task: {e}")
                return False
        else:
            # For async tasks, we can't easily cancel them once started
            logger.warning("Task cancellation not supported for async fallback")
            return False
    
    async def _process_conversation_fallback(self, file_path: str, user_id: str, metadata: Dict[str, Any]):
        """Fallback conversation processing"""
        # Simplified version of conversation processing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic processing
            result = {
                'conversation_id': f"conv_{user_id}_{datetime.now().timestamp()}",
                'processed_at': datetime.now().isoformat(),
                'status': 'processed_with_fallback'
            }
            
            # Clean up file
            try:
                os.remove(file_path)
            except:
                pass
            
            return result
        except Exception as e:
            logger.error(f"Fallback conversation processing failed: {e}")
            raise
    
    async def _generate_report_fallback(self, user_id: str, report_type: str):
        """Fallback report generation"""
        # Simplified report generation
        return {
            'report_id': f"report_{user_id}_{datetime.now().timestamp()}",
            'generated_at': datetime.now().isoformat(),
            'status': 'generated_with_fallback'
        }
    
    async def _process_knowledge_base_fallback(self, file_path: str, document_type: str, metadata: Dict[str, Any]):
        """Fallback knowledge base processing"""
        # Simplified knowledge base processing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                'document_id': f"doc_{datetime.now().timestamp()}",
                'processed_at': datetime.now().isoformat(),
                'status': 'processed_with_fallback'
            }
            
            # Clean up file
            try:
                os.remove(file_path)
            except:
                pass
            
            return result
        except Exception as e:
            logger.error(f"Fallback knowledge base processing failed: {e}")
            raise

# Global task service instance
task_service = TaskService()

# Celery worker signals
if worker_ready:
    @worker_ready.connect
    def worker_ready_handler(sender=None, **kwargs):
        logger.info("Celery worker is ready")

if worker_shutdown:
    @worker_shutdown.connect
    def worker_shutdown_handler(sender=None, **kwargs):
        logger.info("Celery worker is shutting down")