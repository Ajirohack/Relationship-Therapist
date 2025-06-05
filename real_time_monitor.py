#!/usr/bin/env python3
"""
Real-Time Monitor Module
Handles live social media monitoring and real-time recommendations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor

# Social media APIs not available in minimal setup
# import tweepy  # Twitter API
# import praw  # Reddit API
# import facebook  # Facebook API
# import instaloader  # Instagram API
# import discord  # Discord API
# import slack_sdk  # Slack API
# import telegram  # Telegram API

logger = logging.getLogger(__name__)

class MonitoringPlatform(Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    CUSTOM = "custom"

class RecommendationType(Enum):
    IMMEDIATE = "immediate"
    SUGGESTED = "suggested"
    WARNING = "warning"
    OPPORTUNITY = "opportunity"

@dataclass
class LiveMessage:
    platform: str
    message_id: str
    content: str
    sender: str
    recipient: str
    timestamp: datetime
    metadata: Dict[str, Any]
    conversation_id: Optional[str] = None

@dataclass
class RealTimeRecommendation:
    recommendation_id: str
    user_id: str
    recommendation_type: str
    priority: int  # 1-10, 10 being highest
    title: str
    message: str
    suggested_response: Optional[str]
    reasoning: str
    confidence: float
    expires_at: datetime
    context: Dict[str, Any]
    timestamp: datetime

@dataclass
class MonitoringSession:
    session_id: str
    user_id: str
    platforms: List[str]
    target_users: List[str]
    keywords: List[str]
    active: bool
    started_at: datetime
    last_activity: datetime
    message_count: int = 0
    recommendations_sent: int = 0

class RealTimeMonitor:
    def __init__(self, conversation_analyzer, ai_therapist):
        self.conversation_analyzer = conversation_analyzer
        self.ai_therapist = ai_therapist
        
        # Active monitoring sessions
        self.active_sessions: Dict[str, MonitoringSession] = {}
        
        # Message queues for real-time processing
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.recommendation_queue = asyncio.Queue(maxsize=500)
        
        # WebSocket connections for real-time updates
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Recent messages buffer (for context)
        self.recent_messages: Dict[str, deque] = {}  # user_id -> deque of messages
        
        # Recommendation cache
        self.recommendation_cache: Dict[str, List[RealTimeRecommendation]] = {}
        
        # Platform connectors
        self.platform_connectors = {}
        
        # Background tasks
        self.background_tasks = set()
        
        # Thread pool for CPU-intensive tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize platform connectors
        self._initialize_platform_connectors()
    
    def _initialize_platform_connectors(self):
        """
        Initialize connections to various social media platforms
        """
        try:
            # Twitter connector (example)
            # self.platform_connectors[MonitoringPlatform.TWITTER.value] = TwitterConnector()
            
            # Facebook connector (example)
            # self.platform_connectors[MonitoringPlatform.FACEBOOK.value] = FacebookConnector()
            
            # For demo purposes, we'll use mock connectors
            self.platform_connectors[MonitoringPlatform.CUSTOM.value] = MockConnector()
            
            logger.info("Platform connectors initialized")
            
        except Exception as e:
            logger.error(f"Error initializing platform connectors: {str(e)}")
    
    async def start_monitoring_session(self, user_id: str, config: Dict[str, Any]) -> str:
        """
        Start a new real-time monitoring session
        """
        try:
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
            
            session = MonitoringSession(
                session_id=session_id,
                user_id=user_id,
                platforms=config.get('platforms', []),
                target_users=config.get('target_users', []),
                keywords=config.get('keywords', []),
                active=True,
                started_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.active_sessions[session_id] = session
            
            # Initialize message buffer for this user
            if user_id not in self.recent_messages:
                self.recent_messages[user_id] = deque(maxlen=50)  # Keep last 50 messages
            
            # Start monitoring tasks for each platform
            for platform in session.platforms:
                if platform in self.platform_connectors:
                    task = asyncio.create_task(
                        self._monitor_platform(session_id, platform, config)
                    )
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
            
            # Start recommendation processing task
            task = asyncio.create_task(self._process_recommendations(session_id))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
            logger.info(f"Started monitoring session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting monitoring session: {str(e)}")
            raise
    
    async def stop_monitoring_session(self, session_id: str) -> bool:
        """
        Stop a monitoring session
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].active = False
                del self.active_sessions[session_id]
                
                # Cancel related background tasks
                for task in list(self.background_tasks):
                    if hasattr(task, 'session_id') and task.session_id == session_id:
                        task.cancel()
                        self.background_tasks.discard(task)
                
                logger.info(f"Stopped monitoring session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping monitoring session: {str(e)}")
            return False
    
    async def _monitor_platform(self, session_id: str, platform: str, config: Dict[str, Any]):
        """
        Monitor a specific platform for new messages
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            connector = self.platform_connectors.get(platform)
            if not connector:
                logger.warning(f"No connector available for platform {platform}")
                return
            
            logger.info(f"Starting monitoring for platform {platform} in session {session_id}")
            
            while session.active:
                try:
                    # Get new messages from platform
                    messages = await connector.get_new_messages(
                        target_users=session.target_users,
                        keywords=session.keywords,
                        config=config
                    )
                    
                    for message_data in messages:
                        # Create LiveMessage object
                        live_message = LiveMessage(
                            platform=platform,
                            message_id=message_data.get('id'),
                            content=message_data.get('content', ''),
                            sender=message_data.get('sender'),
                            recipient=message_data.get('recipient'),
                            timestamp=datetime.fromisoformat(message_data.get('timestamp', datetime.now().isoformat())),
                            metadata=message_data.get('metadata', {}),
                            conversation_id=message_data.get('conversation_id')
                        )
                        
                        # Add to message queue for processing
                        await self.message_queue.put((session_id, live_message))
                        
                        # Update session activity
                        session.last_activity = datetime.now()
                        session.message_count += 1
                    
                    # Wait before next poll
                    await asyncio.sleep(config.get('poll_interval', 5))
                    
                except Exception as e:
                    logger.error(f"Error monitoring platform {platform}: {str(e)}")
                    await asyncio.sleep(10)  # Wait longer on error
                    
        except asyncio.CancelledError:
            logger.info(f"Platform monitoring cancelled for {platform} in session {session_id}")
        except Exception as e:
            logger.error(f"Fatal error in platform monitoring: {str(e)}")
    
    async def process_live_message(self, user_id: str, message: LiveMessage) -> List[RealTimeRecommendation]:
        """
        Process a live message and generate real-time recommendations
        """
        try:
            # Add message to recent messages buffer
            if user_id not in self.recent_messages:
                self.recent_messages[user_id] = deque(maxlen=50)
            
            self.recent_messages[user_id].append(message)
            
            # Get conversation context
            context = await self._build_conversation_context(user_id, message)
            
            # Analyze current message in context
            analysis_result = await self.conversation_analyzer.analyze_context(
                user_id=user_id,
                current_text=message.content,
                context=context
            )
            
            # Generate recommendations based on analysis
            recommendations = await self._generate_real_time_recommendations(
                user_id=user_id,
                message=message,
                analysis=analysis_result,
                context=context
            )
            
            # Cache recommendations
            if user_id not in self.recommendation_cache:
                self.recommendation_cache[user_id] = []
            
            self.recommendation_cache[user_id].extend(recommendations)
            
            # Clean up old recommendations
            self._cleanup_expired_recommendations(user_id)
            
            # Send recommendations via WebSocket if connected
            await self._send_recommendations_to_client(user_id, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error processing live message: {str(e)}")
            return []
    
    async def _build_conversation_context(self, user_id: str, current_message: LiveMessage) -> Dict[str, Any]:
        """
        Build conversation context from recent messages
        """
        recent_msgs = list(self.recent_messages.get(user_id, []))
        
        # Convert recent messages to conversation format
        conversation_history = []
        for msg in recent_msgs[-10:]:  # Last 10 messages
            conversation_history.append({
                'text': msg.content,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat(),
                'platform': msg.platform
            })
        
        # Analyze conversation patterns
        if len(conversation_history) > 1:
            patterns = await self.conversation_analyzer._analyze_communication_patterns(conversation_history)
        else:
            patterns = {}
        
        context = {
            'recent_messages': conversation_history,
            'conversation_length': len(conversation_history),
            'current_platform': current_message.platform,
            'conversation_id': current_message.conversation_id,
            'patterns': patterns,
            'last_sender': recent_msgs[-2].sender if len(recent_msgs) > 1 else None,
            'topics': [],  # Will be filled by analyzer
            'last_intent': None  # Will be filled by analyzer
        }
        
        return context
    
    async def _generate_real_time_recommendations(self, user_id: str, message: LiveMessage, 
                                                analysis: Dict[str, Any], 
                                                context: Dict[str, Any]) -> List[RealTimeRecommendation]:
        """
        Generate real-time recommendations based on message analysis
        """
        recommendations = []
        
        try:
            # Get AI therapist recommendations
            ai_recommendations = await self.ai_therapist.get_real_time_recommendations(
                user_id=user_id,
                current_message=message.content,
                analysis_result=analysis,
                conversation_context=context
            )
            
            # Convert AI recommendations to RealTimeRecommendation objects
            for i, rec in enumerate(ai_recommendations):
                recommendation = RealTimeRecommendation(
                    recommendation_id=f"rec_{user_id}_{int(datetime.now().timestamp())}_{i}",
                    user_id=user_id,
                    recommendation_type=rec.get('type', RecommendationType.SUGGESTED.value),
                    priority=rec.get('priority', 5),
                    title=rec.get('title', 'Recommendation'),
                    message=rec.get('message', ''),
                    suggested_response=rec.get('suggested_response'),
                    reasoning=rec.get('reasoning', ''),
                    confidence=rec.get('confidence', 0.7),
                    expires_at=datetime.now() + timedelta(minutes=rec.get('expires_in_minutes', 30)),
                    context={
                        'message_id': message.message_id,
                        'platform': message.platform,
                        'analysis': analysis,
                        'conversation_context': context
                    },
                    timestamp=datetime.now()
                )
                
                recommendations.append(recommendation)
            
            # Add rule-based recommendations
            rule_based_recs = await self._generate_rule_based_recommendations(
                user_id, message, analysis, context
            )
            recommendations.extend(rule_based_recs)
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating real-time recommendations: {str(e)}")
            return []
    
    async def _generate_rule_based_recommendations(self, user_id: str, message: LiveMessage,
                                                 analysis: Dict[str, Any], 
                                                 context: Dict[str, Any]) -> List[RealTimeRecommendation]:
        """
        Generate rule-based recommendations
        """
        recommendations = []
        
        try:
            # Rule 1: Detect questions and suggest thoughtful responses
            if '?' in message.content:
                recommendations.append(RealTimeRecommendation(
                    recommendation_id=f"rule_question_{user_id}_{int(datetime.now().timestamp())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.SUGGESTED.value,
                    priority=7,
                    title="Question Detected",
                    message="Your partner asked a question. Consider giving a thoughtful, detailed response.",
                    suggested_response=None,
                    reasoning="Questions indicate engagement and interest in conversation",
                    confidence=0.8,
                    expires_at=datetime.now() + timedelta(minutes=15),
                    context={'rule': 'question_detection'},
                    timestamp=datetime.now()
                ))
            
            # Rule 2: Detect emotional content
            sentiment = analysis.get('sentiment', {})
            if sentiment.get('label') == 'negative' and sentiment.get('score', 0) > 0.7:
                recommendations.append(RealTimeRecommendation(
                    recommendation_id=f"rule_negative_{user_id}_{int(datetime.now().timestamp())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.WARNING.value,
                    priority=9,
                    title="Negative Emotion Detected",
                    message="Your partner seems upset. Consider offering support or asking if they're okay.",
                    suggested_response="I can sense something might be bothering you. Do you want to talk about it?",
                    reasoning="Negative emotions require empathetic response",
                    confidence=0.9,
                    expires_at=datetime.now() + timedelta(minutes=10),
                    context={'rule': 'negative_emotion'},
                    timestamp=datetime.now()
                ))
            
            # Rule 3: Detect long response delays
            recent_msgs = list(self.recent_messages.get(user_id, []))
            if len(recent_msgs) >= 2:
                last_msg = recent_msgs[-2]
                time_diff = message.timestamp - last_msg.timestamp
                
                if time_diff.total_seconds() > 3600:  # 1 hour delay
                    recommendations.append(RealTimeRecommendation(
                        recommendation_id=f"rule_delay_{user_id}_{int(datetime.now().timestamp())}",
                        user_id=user_id,
                        recommendation_type=RecommendationType.OPPORTUNITY.value,
                        priority=6,
                        title="Long Response Delay",
                        message="There was a long gap in conversation. Consider acknowledging the delay.",
                        suggested_response="Sorry for the late response! I was busy but wanted to get back to you.",
                        reasoning="Long delays can create uncertainty in relationships",
                        confidence=0.7,
                        expires_at=datetime.now() + timedelta(minutes=20),
                        context={'rule': 'response_delay', 'delay_hours': time_diff.total_seconds() / 3600},
                        timestamp=datetime.now()
                    ))
            
            # Rule 4: Detect affectionate messages
            affection_keywords = ['love', 'miss', 'care', 'adore', 'cherish']
            if any(keyword in message.content.lower() for keyword in affection_keywords):
                recommendations.append(RealTimeRecommendation(
                    recommendation_id=f"rule_affection_{user_id}_{int(datetime.now().timestamp())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.OPPORTUNITY.value,
                    priority=8,
                    title="Affectionate Message",
                    message="Your partner expressed affection. This is a great opportunity to reciprocate.",
                    suggested_response=None,
                    reasoning="Reciprocating affection strengthens emotional bonds",
                    confidence=0.8,
                    expires_at=datetime.now() + timedelta(minutes=25),
                    context={'rule': 'affection_detection'},
                    timestamp=datetime.now()
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating rule-based recommendations: {str(e)}")
            return []
    
    async def _process_recommendations(self, session_id: str):
        """
        Background task to process message queue and generate recommendations
        """
        try:
            while session_id in self.active_sessions and self.active_sessions[session_id].active:
                try:
                    # Get message from queue with timeout
                    session_id_from_queue, message = await asyncio.wait_for(
                        self.message_queue.get(), timeout=5.0
                    )
                    
                    if session_id_from_queue == session_id:
                        session = self.active_sessions[session_id]
                        
                        # Process the message
                        recommendations = await self.process_live_message(
                            session.user_id, message
                        )
                        
                        session.recommendations_sent += len(recommendations)
                        
                        # Mark task as done
                        self.message_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No messages in queue, continue
                    continue
                except Exception as e:
                    logger.error(f"Error processing message in queue: {str(e)}")
                    continue
                    
        except asyncio.CancelledError:
            logger.info(f"Recommendation processing cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Fatal error in recommendation processing: {str(e)}")
    
    def _cleanup_expired_recommendations(self, user_id: str):
        """
        Remove expired recommendations from cache
        """
        if user_id in self.recommendation_cache:
            now = datetime.now()
            self.recommendation_cache[user_id] = [
                rec for rec in self.recommendation_cache[user_id]
                if rec.expires_at > now
            ]
    
    async def _send_recommendations_to_client(self, user_id: str, recommendations: List[RealTimeRecommendation]):
        """
        Send recommendations to client via WebSocket
        """
        if user_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[user_id]
                
                message = {
                    'type': 'recommendations',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'recommendations': [asdict(rec) for rec in recommendations]
                }
                
                await websocket.send(json.dumps(message, default=str))
                
            except Exception as e:
                logger.error(f"Error sending recommendations via WebSocket: {str(e)}")
                # Remove broken connection
                if user_id in self.websocket_connections:
                    del self.websocket_connections[user_id]
    
    async def register_websocket(self, user_id: str, websocket: websockets.WebSocketServerProtocol):
        """
        Register a WebSocket connection for real-time updates
        """
        self.websocket_connections[user_id] = websocket
        logger.info(f"WebSocket registered for user {user_id}")
        
        try:
            # Send initial connection confirmation
            await websocket.send(json.dumps({
                'type': 'connection_established',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Keep connection alive
            async for message in websocket:
                # Handle incoming messages from client
                await self._handle_websocket_message(user_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for user {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        finally:
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
    
    async def _handle_websocket_message(self, user_id: str, message: str):
        """
        Handle incoming WebSocket messages from client
        """
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Respond to ping
                await self.websocket_connections[user_id].send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            
            elif message_type == 'get_recommendations':
                # Send cached recommendations
                cached_recs = self.recommendation_cache.get(user_id, [])
                await self._send_recommendations_to_client(user_id, cached_recs)
            
            elif message_type == 'manual_message':
                # Process manually submitted message
                manual_message = LiveMessage(
                    platform='manual',
                    message_id=f"manual_{int(datetime.now().timestamp())}",
                    content=data.get('content', ''),
                    sender=data.get('sender', 'unknown'),
                    recipient=user_id,
                    timestamp=datetime.now(),
                    metadata={'source': 'manual_input'}
                )
                
                await self.process_live_message(user_id, manual_message)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a monitoring session
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'platforms': session.platforms,
            'active': session.active,
            'started_at': session.started_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'message_count': session.message_count,
            'recommendations_sent': session.recommendations_sent,
            'uptime_minutes': (datetime.now() - session.started_at).total_seconds() / 60
        }
    
    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent recommendations for a user
        """
        self._cleanup_expired_recommendations(user_id)
        
        recommendations = self.recommendation_cache.get(user_id, [])
        
        # Sort by timestamp (newest first) and limit
        sorted_recs = sorted(recommendations, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [asdict(rec) for rec in sorted_recs]
    
    async def submit_manual_message(self, user_id: str, message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Manually submit a message for analysis and recommendations
        """
        try:
            manual_message = LiveMessage(
                platform=message_data.get('platform', 'manual'),
                message_id=f"manual_{int(datetime.now().timestamp())}",
                content=message_data.get('content', ''),
                sender=message_data.get('sender', 'unknown'),
                recipient=user_id,
                timestamp=datetime.now(),
                metadata=message_data.get('metadata', {'source': 'manual_input'}),
                conversation_id=message_data.get('conversation_id')
            )
            
            recommendations = await self.process_live_message(user_id, manual_message)
            return [asdict(rec) for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Error submitting manual message: {str(e)}")
            return []
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of all active monitoring sessions
        """
        return [
            {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'platforms': session.platforms,
                'started_at': session.started_at.isoformat(),
                'message_count': session.message_count,
                'recommendations_sent': session.recommendations_sent
            }
            for session in self.active_sessions.values()
            if session.active
        ]
    
    async def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """
        Clean up inactive sessions
        """
        cutoff_time = datetime.now() - timedelta(hours=max_inactive_hours)
        
        inactive_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for session_id in inactive_sessions:
            await self.stop_monitoring_session(session_id)
            logger.info(f"Cleaned up inactive session {session_id}")
        
        return len(inactive_sessions)


class MockConnector:
    """
    Mock connector for demonstration purposes
    """
    
    def __init__(self):
        self.message_counter = 0
    
    async def get_new_messages(self, target_users: List[str], keywords: List[str], 
                             config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Mock method to simulate getting new messages
        """
        # Simulate occasional new messages
        import random
        
        if random.random() < 0.3:  # 30% chance of new message
            self.message_counter += 1
            
            sample_messages = [
                "Hey, how was your day?",
                "I miss you!",
                "What are you up to?",
                "Can't wait to see you again",
                "Thanks for being so understanding",
                "I'm feeling a bit stressed today",
                "Do you want to grab dinner tonight?",
                "I love spending time with you"
            ]
            
            return [{
                'id': f"mock_msg_{self.message_counter}",
                'content': random.choice(sample_messages),
                'sender': random.choice(target_users) if target_users else 'partner',
                'recipient': 'user',
                'timestamp': datetime.now().isoformat(),
                'metadata': {'source': 'mock_connector'},
                'conversation_id': 'mock_conversation'
            }]
        
        return []