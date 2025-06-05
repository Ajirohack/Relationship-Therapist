#!/usr/bin/env python3
"""
Conversation Analyzer Module
Handles conversation analysis, pattern recognition, and emotional intelligence assessment
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from dataclasses import dataclass
from enum import Enum
# Heavy ML dependencies not available in minimal setup
# import spacy, transformers, sentence_transformers, sklearn, nltk, textblob, numpy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from minimal_implementations import py_mean, py_var, py_std, py_random_uniform, py_cumsum, py_random_rand

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    COMPREHENSIVE = "comprehensive"
    EMOTIONAL = "emotional"
    COMMUNICATION_STYLE = "communication_style"
    COMPATIBILITY = "compatibility"
    RELATIONSHIP_STAGE = "relationship_stage"

@dataclass
class ConversationMetrics:
    response_time: float
    message_length: int
    emotional_tone: str
    engagement_level: float
    intimacy_level: float
    communication_style: str
    topics_discussed: List[str]
    sentiment_score: float
    attachment_indicators: List[str]

@dataclass
class AnalysisResult:
    user_id: str
    analysis_type: str
    overall_score: float
    emotional_analysis: Dict[str, Any]
    communication_patterns: Dict[str, Any]
    relationship_insights: Dict[str, Any]
    red_flags: List[str]
    positive_indicators: List[str]
    recommendations: List[str]
    confidence_score: float
    timestamp: datetime

class ConversationAnalyzer:
    def __init__(self):
        """
        Initialize the conversation analyzer with available models
        """
        logger.info("Initializing ConversationAnalyzer...")
        
        # Use basic NLP processing without heavy dependencies
        self.nlp = None  # spaCy not available
        self.sentiment_analyzer = None  # Transformers not available
        self.emotion_classifier = None  # Transformers not available
        self.relationship_stage_classifier = None
        
        # Initialize VADER sentiment analyzer (available)
        try:
            self.vader_sentiment = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize VADER sentiment: {e}")
            self.vader_sentiment = None
        
        # Set up sentiment analysis method
        logger.info("Sentiment analysis method configured")
        
        logger.info("ConversationAnalyzer initialized successfully (minimal mode)")
    
    def _initialize_models(self):
        """
        Initialize NLP models and analyzers (minimal implementation)
        """
        # Models already initialized in __init__
        pass
    
    async def analyze(self, user_id: str, conversation_history: List[Dict[str, Any]], 
                     analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Main analysis function
        """
        try:
            # Preprocess conversation data
            processed_conversations = self._preprocess_conversations(conversation_history)
            
            # Perform different types of analysis based on request
            if analysis_type == AnalysisType.COMPREHENSIVE.value:
                result = await self._comprehensive_analysis(user_id, processed_conversations)
            elif analysis_type == AnalysisType.EMOTIONAL.value:
                result = await self._emotional_analysis(user_id, processed_conversations)
            elif analysis_type == AnalysisType.COMMUNICATION_STYLE.value:
                result = await self._communication_style_analysis(user_id, processed_conversations)
            elif analysis_type == AnalysisType.COMPATIBILITY.value:
                result = await self._compatibility_analysis(user_id, processed_conversations)
            elif analysis_type == AnalysisType.RELATIONSHIP_STAGE.value:
                result = await self._relationship_stage_analysis(user_id, processed_conversations)
            else:
                result = await self._comprehensive_analysis(user_id, processed_conversations)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis error for user {user_id}: {str(e)}")
            raise
    
    def _preprocess_conversations(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocess and clean conversation data
        """
        processed = []
        
        for conv in conversations:
            # Clean text
            text = conv.get('text', '')
            cleaned_text = self._clean_text(text)
            
            # Extract metadata
            processed_conv = {
                'text': cleaned_text,
                'original_text': text,
                'timestamp': conv.get('timestamp'),
                'sender': conv.get('sender'),
                'platform': conv.get('platform'),
                'message_type': conv.get('message_type', 'text'),
                'metadata': conv.get('metadata', {})
            }
            
            processed.append(processed_conv)
        
        return processed
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep emoticons
        text = re.sub(r'[^\w\s\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', text)
        
        return text.strip()
    
    async def _comprehensive_analysis(self, user_id: str, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive conversation analysis
        """
        # Emotional analysis
        emotional_analysis = await self._analyze_emotions(conversations)
        
        # Communication patterns
        communication_patterns = self._analyze_communication_patterns(conversations)
        
        # Relationship dynamics
        relationship_dynamics = self._analyze_relationship_dynamics(conversations)
        
        # Attachment style analysis
        attachment_analysis = self._analyze_attachment_style(conversations)
        
        # Red flags detection
        red_flags = self._detect_red_flags(conversations)
        
        # Positive indicators
        positive_indicators = self._detect_positive_indicators(conversations)
        
        # Calculate overall relationship health score
        overall_score = self._calculate_relationship_score(
            emotional_analysis, communication_patterns, 
            relationship_dynamics, red_flags, positive_indicators
        )
        
        return {
            'user_id': user_id,
            'analysis_type': 'comprehensive',
            'overall_score': overall_score,
            'emotional_analysis': emotional_analysis,
            'communication_patterns': communication_patterns,
            'relationship_dynamics': relationship_dynamics,
            'attachment_analysis': attachment_analysis,
            'red_flags': red_flags,
            'positive_indicators': positive_indicators,
            'conversation_metrics': self._calculate_conversation_metrics(conversations),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _analyze_emotions(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze emotional content of conversations
        """
        try:
            # Combine all conversation text
            all_text = " ".join([conv.get('text', '') for conv in conversations])
            
            # Use VADER for sentiment analysis
            sentiment_scores = self._analyze_sentiment_vader(all_text)
            
            # Identify primary emotions
            primary_emotions = self._identify_primary_emotions(all_text)
            
            # Detect emotional patterns
            emotional_patterns = self._detect_emotional_patterns(conversations)
            
            return {
                'sentiment': sentiment_scores,
                'primary_emotions': primary_emotions,
                'emotional_patterns': emotional_patterns,
                'emotional_variability': self._calculate_emotional_variability(conversations)
            }
        except Exception as e:
            logger.error(f"Emotion analysis error: {str(e)}")
            # Return minimal analysis using VADER
            return {
                'sentiment': self._analyze_sentiment_vader(all_text) if 'all_text' in locals() else {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1, 'sentiment_label': 'neutral'},
                'primary_emotions': [],
                'emotional_patterns': {},
                'emotional_variability': 0.0
            }
    
    def _analyze_sentiment_vader(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using VADER
        """
        if not text or not self.vader_sentiment:
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1, 'sentiment_label': 'neutral'}
        
        try:
            scores = self.vader_sentiment.polarity_scores(text)
            
            # Add sentiment label
            if scores['compound'] >= 0.05:
                sentiment_label = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
                
            scores['sentiment_label'] = sentiment_label
            
            return scores
        except Exception as e:
            logger.error(f"VADER sentiment analysis error: {str(e)}")
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1, 'sentiment_label': 'neutral'}
    
    def _identify_primary_emotions(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify primary emotions in text using keyword-based approach
        """
        if not text:
            return []
            
        # Dictionary of emotion keywords
        emotion_keywords = {
            'joy': ['happy', 'joy', 'delighted', 'pleased', 'glad', 'excited', 'thrilled', 'enjoy', 'love', 'wonderful'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'heartbroken', 'gloomy', 'disappointed', 'upset'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'frustrated', 'enraged', 'hate', 'resent'],
            'fear': ['afraid', 'scared', 'fearful', 'terrified', 'anxious', 'worried', 'nervous', 'panic', 'dread'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'unexpected', 'wow'],
            'disgust': ['disgusted', 'revolted', 'dislike', 'hate', 'gross', 'repulsed', 'ugh'],
            'trust': ['trust', 'believe', 'faith', 'confident', 'assured', 'reliance', 'dependable'],
            'anticipation': ['anticipate', 'expect', 'look forward', 'hope', 'eager', 'waiting']
        }
        
        text_lower = text.lower()
        emotions_found = []
        
        for emotion, keywords in emotion_keywords.items():
            count = 0
            matches = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    count += text_lower.count(keyword)
                    matches.append(keyword)
            
            if count > 0:
                emotions_found.append({
                    'emotion': emotion,
                    'intensity': min(1.0, count / 10),  # Cap at 1.0
                    'keywords': matches
                })
        
        # Sort by intensity
        emotions_found.sort(key=lambda x: x['intensity'], reverse=True)
        
        return emotions_found[:3]  # Return top 3 emotions
    
    def _detect_emotional_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect emotional patterns across conversations
        """
        if not conversations:
            return {}
            
        # Analyze emotional progression
        sentiment_progression = []
        
        for conv in conversations:
            if 'text' in conv and conv['text']:
                sentiment = self._analyze_sentiment_vader(conv['text'])
                sentiment_progression.append(sentiment['compound'])
        
        # Calculate emotional trend
        emotional_trend = 'stable'
        if len(sentiment_progression) >= 3:
            first_half = sentiment_progression[:len(sentiment_progression)//2]
            second_half = sentiment_progression[len(sentiment_progression)//2:]
            
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            
            if second_avg - first_avg > 0.2:
                emotional_trend = 'improving'
            elif first_avg - second_avg > 0.2:
                emotional_trend = 'deteriorating'
        
        # Detect emotional response patterns
        response_patterns = self._analyze_emotional_responses(conversations)
        
        return {
            'emotional_trend': emotional_trend,
            'sentiment_variance': self._calculate_variance(sentiment_progression) if sentiment_progression else 0,
            'response_patterns': response_patterns,
            'sentiment_progression': sentiment_progression
        }
    
    def _analyze_emotional_responses(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze emotional response patterns between conversation participants
        """
        if len(conversations) < 4:  # Need at least 2 exchanges
            return {'pattern': 'insufficient_data'}
            
        # Group messages by sender
        messages_by_sender = {}
        
        for conv in conversations:
            sender = conv.get('sender', 'unknown')
            if sender not in messages_by_sender:
                messages_by_sender[sender] = []
            messages_by_sender[sender].append(conv)
        
        # Need at least 2 participants
        if len(messages_by_sender) < 2:
            return {'pattern': 'single_participant'}
            
        # Analyze response patterns
        patterns = {}
        
        # Check for mirroring (similar emotional tone in responses)
        mirroring_score = 0
        mirroring_count = 0
        
        # Check for complementary responses (positive to negative)
        complementary_score = 0
        complementary_count = 0
        
        # Get sentiment for each message
        sender_sentiments = {}
        for sender, messages in messages_by_sender.items():
            sender_sentiments[sender] = [self._analyze_sentiment_vader(msg.get('text', ''))['compound'] for msg in messages if msg.get('text', '')]
        
        # Analyze sequential interactions
        senders = list(messages_by_sender.keys())
        if len(senders) >= 2:
            sender1, sender2 = senders[0], senders[1]
            
            # Compare emotions in conversation sequence
            for i in range(min(len(sender_sentiments[sender1]), len(sender_sentiments[sender2]))):
                if i >= len(sender_sentiments[sender1]) or i >= len(sender_sentiments[sender2]):
                    continue
                    
                sentiment1 = sender_sentiments[sender1][i]
                sentiment2 = sender_sentiments[sender2][i]
                
                # Check for mirroring (similar sentiment)
                sentiment_diff = abs(sentiment1 - sentiment2)
                if sentiment_diff < 0.3:  # Similar sentiment
                    mirroring_score += 1
                mirroring_count += 1
                
                # Check for complementary responses (opposite sentiment)
                if (sentiment1 > 0.2 and sentiment2 < -0.2) or (sentiment1 < -0.2 and sentiment2 > 0.2):
                    complementary_score += 1
                complementary_count += 1
        
        # Calculate scores
        mirroring_ratio = mirroring_score / mirroring_count if mirroring_count > 0 else 0
        complementary_ratio = complementary_score / complementary_count if complementary_count > 0 else 0
        
        # Determine primary pattern
        if mirroring_ratio > 0.6:
            primary_pattern = 'emotional_mirroring'
        elif complementary_ratio > 0.4:
            primary_pattern = 'emotional_complementary'
        else:
            primary_pattern = 'mixed_emotional_responses'
        
        return {
            'pattern': primary_pattern,
            'mirroring_ratio': mirroring_ratio,
            'complementary_ratio': complementary_ratio
        }
    
    def _calculate_emotional_variability(self, conversations: List[Dict[str, Any]]) -> float:
        """
        Calculate emotional variability in conversations
        """
        if not conversations:
            return 0.0
            
        # Get sentiment scores for each message
        sentiment_scores = []
        for conv in conversations:
            if 'text' in conv and conv['text']:
                sentiment = self._analyze_sentiment_vader(conv['text'])
                sentiment_scores.append(sentiment['compound'])
        
        # Calculate standard deviation as a measure of variability
        if not sentiment_scores:
            return 0.0
            
        mean = sum(sentiment_scores) / len(sentiment_scores)
        variance = sum((x - mean) ** 2 for x in sentiment_scores) / len(sentiment_scores)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 range (std_dev of 0.5 or higher is considered high variability)
        variability = min(1.0, std_dev * 2)
        
        return variability
    
    def _analyze_communication_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze communication patterns in conversations
        """
        if not conversations:
            return {}
            
        # Message length analysis
        message_lengths = [len(conv.get('text', '')) for conv in conversations]
        avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        
        # Question frequency
        question_count = sum(1 for conv in conversations if '?' in conv.get('text', ''))
        question_ratio = question_count / len(conversations)
        
        # Response patterns
        response_times = []
        for i in range(1, len(conversations)):
            if 'timestamp' in conversations[i-1] and 'timestamp' in conversations[i]:
                try:
                    t1 = datetime.fromisoformat(conversations[i-1]['timestamp'])
                    t2 = datetime.fromisoformat(conversations[i]['timestamp'])
                    response_times.append((t2 - t1).total_seconds())
                except (ValueError, TypeError):
                    pass
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        # Communication style assessment
        style = self._assess_communication_style(conversations)
        
        # Listen-to-talk ratio
        listen_talk_ratio = self._calculate_listen_talk_ratio(conversations)
        
        return {
            'message_analysis': {
                'avg_length': avg_length,
                'length_variance': self._calculate_variance(message_lengths),
                'question_ratio': question_ratio
            },
            'response_analysis': {
                'avg_response_time_seconds': avg_response_time,
                'response_consistency': self._calculate_response_consistency(response_times)
            },
            'communication_style': style,
            'listen_talk_ratio': listen_talk_ratio,
            'conversation_balance': self._analyze_conversation_balance(conversations)
        }
    
    def _assess_communication_style(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess communication style from conversations
        """
        if not conversations:
            return {'primary_style': 'unknown'}
            
        # Count style indicators
        directive_count = 0
        collaborative_count = 0
        passive_count = 0
        aggressive_count = 0
        
        # Style keywords
        style_keywords = {
            'directive': ['should', 'must', 'need to', 'have to', 'do this'],
            'collaborative': ['we could', 'what if we', 'let\'s', 'together', 'our'],
            'passive': ['maybe', 'might', 'possibly', 'if you want', 'whatever'],
            'aggressive': ['always', 'never', 'you always', 'you never', 'ridiculous']
        }
        
        # Count style indicators
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            # Check for style keywords
            for style, keywords in style_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        if style == 'directive':
                            directive_count += 1
                        elif style == 'collaborative':
                            collaborative_count += 1
                        elif style == 'passive':
                            passive_count += 1
                        elif style == 'aggressive':
                            aggressive_count += 1
            
            # Check for questions (collaborative)
            if '?' in text:
                collaborative_count += 0.5
            
            # Check for exclamations (potentially aggressive)
            if '!' in text:
                aggressive_count += 0.2
        
        # Normalize counts by number of messages
        n_messages = len(conversations)
        styles = {
            'directive': directive_count / n_messages,
            'collaborative': collaborative_count / n_messages,
            'passive': passive_count / n_messages,
            'aggressive': aggressive_count / n_messages
        }
        
        # Determine primary style
        primary_style = max(styles, key=styles.get)
        
        # Check if the primary style is strong enough
        if styles[primary_style] < 0.2:
            primary_style = 'balanced'
        
        return {
            'primary_style': primary_style,
            'style_scores': styles
        }
    
    def _calculate_listen_talk_ratio(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate listen-to-talk ratio for participants
        """
        if len(conversations) < 2:
            return {'ratio': 1.0, 'balanced': True}
            
        # Group by sender
        messages_by_sender = {}
        
        for conv in conversations:
            sender = conv.get('sender', 'unknown')
            if sender not in messages_by_sender:
                messages_by_sender[sender] = []
            messages_by_sender[sender].append(conv)
        
        # Need at least 2 participants
        if len(messages_by_sender) < 2:
            return {'ratio': 1.0, 'balanced': True}
            
        # Calculate message counts
        message_counts = {sender: len(messages) for sender, messages in messages_by_sender.items()}
        
        # Calculate ratios for each sender
        ratios = {}
        for sender, count in message_counts.items():
            other_counts = sum(c for s, c in message_counts.items() if s != sender)
            ratios[sender] = other_counts / count if count > 0 else float('inf')
        
        # Calculate overall balance
        min_ratio = min(ratios.values()) if ratios else 1.0
        max_ratio = max(ratios.values()) if ratios else 1.0
        
        overall_ratio = min_ratio / max_ratio if max_ratio > 0 else 1.0
        balanced = overall_ratio > 0.5  # At least somewhat balanced
        
        return {
            'overall_ratio': overall_ratio,
            'sender_ratios': ratios,
            'balanced': balanced
        }
    
    def _analyze_conversation_balance(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze balance in conversation participation
        """
        if len(conversations) < 2:
            return {'balance_score': 1.0, 'assessment': 'single_participant'}
            
        # Group by sender
        messages_by_sender = {}
        
        for conv in conversations:
            sender = conv.get('sender', 'unknown')
            if sender not in messages_by_sender:
                messages_by_sender[sender] = {
                    'message_count': 0,
                    'total_length': 0,
                    'questions': 0
                }
            
            messages_by_sender[sender]['message_count'] += 1
            messages_by_sender[sender]['total_length'] += len(conv.get('text', ''))
            messages_by_sender[sender]['questions'] += conv.get('text', '').count('?')
        
        # Need at least 2 participants
        if len(messages_by_sender) < 2:
            return {'balance_score': 1.0, 'assessment': 'single_participant'}
        
        # Calculate metrics
        counts = [data['message_count'] for data in messages_by_sender.values()]
        lengths = [data['total_length'] for data in messages_by_sender.values()]
        questions = [data['questions'] for data in messages_by_sender.values()]
        
        # Calculate balance score (1.0 = perfectly balanced, 0.0 = completely imbalanced)
        min_count = min(counts)
        max_count = max(counts)
        count_balance = min_count / max_count if max_count > 0 else 1.0
        
        min_length = min(lengths)
        max_length = max(lengths)
        length_balance = min_length / max_length if max_length > 0 else 1.0
        
        # Combined balance score
        balance_score = (count_balance + length_balance) / 2
        
        # Assess balance
        if balance_score > 0.8:
            assessment = 'very_balanced'
        elif balance_score > 0.6:
            assessment = 'balanced'
        elif balance_score > 0.4:
            assessment = 'somewhat_imbalanced'
        else:
            assessment = 'highly_imbalanced'
        
        return {
            'balance_score': balance_score,
            'count_balance': count_balance,
            'length_balance': length_balance,
            'assessment': assessment,
            'participant_data': {sender: data for sender, data in messages_by_sender.items()}
        }
    
    def _analyze_relationship_dynamics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze relationship dynamics from conversations
        """
        if not conversations:
            return {}
            
        # Power dynamics analysis
        power_dynamics = self._analyze_power_dynamics(conversations)
        
        # Conflict pattern analysis
        conflict_patterns = self._analyze_conflict_patterns(conversations)
        
        # Support pattern analysis
        support_patterns = self._analyze_support_patterns(conversations)
        
        # Intimacy analysis
        intimacy_level = self._analyze_intimacy_level(conversations)
        
        return {
            'power_dynamics': power_dynamics,
            'conflict_patterns': conflict_patterns,
            'support_patterns': support_patterns,
            'intimacy_level': intimacy_level,
            'relationship_stage': self._assess_relationship_stage(conversations)
        }
    
    def _analyze_power_dynamics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze power dynamics in conversations
        """
        if len(conversations) < 3:
            return {'pattern': 'insufficient_data'}
            
        # Group by sender
        messages_by_sender = {}
        
        for conv in conversations:
            sender = conv.get('sender', 'unknown')
            if sender not in messages_by_sender:
                messages_by_sender[sender] = []
            messages_by_sender[sender].append(conv)
        
        # Need at least 2 participants
        if len(messages_by_sender) < 2:
            return {'pattern': 'single_participant'}
            
        # Calculate directive language usage
        directive_keywords = ['must', 'should', 'have to', 'need to', 'do this', 'do that']
        directive_counts = {}
        
        for sender, messages in messages_by_sender.items():
            directive_counts[sender] = 0
            for msg in messages:
                text = msg.get('text', '').lower()
                for keyword in directive_keywords:
                    if keyword in text:
                        directive_counts[sender] += 1
        
        # Calculate decision-making language
        decision_keywords = ['decide', 'decision', 'choose', 'choice', 'option', 'plan']
        decision_counts = {}
        
        for sender, messages in messages_by_sender.items():
            decision_counts[sender] = 0
            for msg in messages:
                text = msg.get('text', '').lower()
                for keyword in decision_keywords:
                    if keyword in text:
                        decision_counts[sender] += 1
        
        # Determine power balance
        power_scores = {}
        for sender in messages_by_sender.keys():
            # Normalize by message count
            message_count = len(messages_by_sender[sender])
            directive_ratio = directive_counts[sender] / message_count if message_count > 0 else 0
            decision_ratio = decision_counts[sender] / message_count if message_count > 0 else 0
            
            power_scores[sender] = (directive_ratio + decision_ratio) / 2
        
        # Check if power is balanced
        if len(power_scores) >= 2:
            scores = list(power_scores.values())
            max_score = max(scores)
            min_score = min(scores)
            
            power_ratio = min_score / max_score if max_score > 0 else 1.0
            
            if power_ratio > 0.7:
                pattern = 'balanced'
            elif power_ratio > 0.4:
                pattern = 'somewhat_imbalanced'
            else:
                pattern = 'significantly_imbalanced'
                
            dominant_partner = max(power_scores.items(), key=lambda x: x[1])[0] if power_scores else None
        else:
            pattern = 'insufficient_data'
            power_ratio = 1.0
            dominant_partner = None
        
        return {
            'pattern': pattern,
            'power_ratio': power_ratio,
            'power_scores': power_scores,
            'dominant_partner': dominant_partner if pattern != 'balanced' else None
        }
    
    def _analyze_conflict_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conflict patterns in conversations
        """
        if not conversations:
            return {}
            
        # Conflict keywords
        conflict_keywords = ['argument', 'fight', 'disagree', 'upset', 'angry', 'mad', 'frustrated', 'annoyed']
        
        # Criticism keywords
        criticism_keywords = ['always', 'never', 'why do you', 'you should', 'you don\'t', 'your fault']
        
        # Defensiveness keywords
        defensiveness_keywords = ['not my fault', 'wasn\'t me', 'you\'re the one', 'i didn\'t', 'that\'s not true']
        
        # Conflict resolution keywords
        resolution_keywords = ['sorry', 'apologize', 'understand', 'compromise', 'agree', 'resolve', 'solution']
        
        # Count occurrences
        conflict_count = 0
        criticism_count = 0
        defensiveness_count = 0
        resolution_count = 0
        
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            # Check for conflict indicators
            for keyword in conflict_keywords:
                if keyword in text:
                    conflict_count += 1
                    break
            
            # Check for criticism
            for keyword in criticism_keywords:
                if keyword in text:
                    criticism_count += 1
                    break
            
            # Check for defensiveness
            for keyword in defensiveness_keywords:
                if keyword in text:
                    defensiveness_count += 1
                    break
            
            # Check for resolution attempts
            for keyword in resolution_keywords:
                if keyword in text:
                    resolution_count += 1
                    break
        
        # Normalize by message count
        n_messages = len(conversations)
        conflict_ratio = conflict_count / n_messages
        criticism_ratio = criticism_count / n_messages
        defensiveness_ratio = defensiveness_count / n_messages
        resolution_ratio = resolution_count / n_messages
        
        # Determine conflict style
        if conflict_ratio < 0.1:
            pattern = 'minimal_conflict'
        elif resolution_ratio > criticism_ratio and resolution_ratio > defensiveness_ratio:
            pattern = 'constructive_conflict'
        elif criticism_ratio > 0.2 and defensiveness_ratio > 0.2:
            pattern = 'criticism_defensiveness_cycle'
        elif criticism_ratio > 0.2:
            pattern = 'criticism_heavy'
        elif defensiveness_ratio > 0.2:
            pattern = 'defensiveness_heavy'
        else:
            pattern = 'mixed_conflict'
        
        # Calculate resolution effectiveness
        if conflict_count > 0:
            resolution_effectiveness = resolution_count / conflict_count
        else:
            resolution_effectiveness = 1.0  # No conflicts to resolve
        
        return {
            'pattern': pattern,
            'conflict_ratio': conflict_ratio,
            'criticism_ratio': criticism_ratio,
            'defensiveness_ratio': defensiveness_ratio,
            'resolution_ratio': resolution_ratio,
            'resolution_effectiveness': resolution_effectiveness
        }
    
    def _analyze_support_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze support patterns in conversations
        """
        if not conversations:
            return {}
            
        # Support keywords
        support_keywords = ['here for you', 'support', 'help', 'understand', 'there for you', 'got your back']
        
        # Validation keywords
        validation_keywords = ['make sense', 'understand', 'see your point', 'valid', 'appreciate']
        
        # Empathy keywords
        empathy_keywords = ['feel', 'emotion', 'must be', 'sounds like', 'that\'s tough', 'that\'s hard']
        
        # Count occurrences
        support_count = 0
        validation_count = 0
        empathy_count = 0
        
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            # Check for support indicators
            for keyword in support_keywords:
                if keyword in text:
                    support_count += 1
                    break
            
            # Check for validation
            for keyword in validation_keywords:
                if keyword in text:
                    validation_count += 1
                    break
            
            # Check for empathy
            for keyword in empathy_keywords:
                if keyword in text:
                    empathy_count += 1
                    break
        
        # Normalize by message count
        n_messages = len(conversations)
        support_ratio = support_count / n_messages
        validation_ratio = validation_count / n_messages
        empathy_ratio = empathy_count / n_messages
        
        # Calculate overall support score
        support_score = (support_ratio + validation_ratio + empathy_ratio) / 3
        
        # Determine support level
        if support_score < 0.1:
            level = 'low'
        elif support_score < 0.3:
            level = 'moderate'
        else:
            level = 'high'
        
        return {
            'support_score': support_score,
            'level': level,
            'support_ratio': support_ratio,
            'validation_ratio': validation_ratio,
            'empathy_ratio': empathy_ratio
        }
    
    def _analyze_intimacy_level(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze intimacy level in conversations
        """
        if not conversations:
            return {'level': 'unknown', 'score': 0.0}
            
        # Intimacy keywords
        intimacy_keywords = {
            'high': ['love you', 'miss you', 'trust you', 'always', 'forever', 'future', 'promise'],
            'moderate': ['care', 'special', 'important', 'like you', 'appreciate', 'feelings'],
            'low': ['thanks', 'ok', 'fine', 'sure', 'whatever', 'later']
        }
        
        # Personal disclosure keywords
        disclosure_keywords = ['feel', 'think', 'worry', 'afraid', 'happy', 'sad', 'dream', 'hope']
        
        # Count occurrences
        intimacy_counts = {'high': 0, 'moderate': 0, 'low': 0}
        disclosure_count = 0
        
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            # Check for intimacy indicators
            for level, keywords in intimacy_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        intimacy_counts[level] += 1
                        break
            
            # Check for personal disclosure
            for keyword in disclosure_keywords:
                if keyword in text:
                    disclosure_count += 1
                    break
        
        # Calculate intimacy score (weighted)
        total_intimacy = intimacy_counts['high'] * 1.0 + intimacy_counts['moderate'] * 0.6 + intimacy_counts['low'] * 0.2
        max_possible = len(conversations)  # Maximum one intimacy indicator per message
        
        intimacy_score = total_intimacy / max_possible if max_possible > 0 else 0
        
        # Add disclosure component
        disclosure_ratio = disclosure_count / len(conversations)
        combined_score = (intimacy_score * 0.7) + (disclosure_ratio * 0.3)  # Weighted combination
        
        # Determine intimacy level
        if combined_score < 0.2:
            level = 'low'
        elif combined_score < 0.5:
            level = 'moderate'
        else:
            level = 'high'
        
        return {
            'level': level,
            'score': combined_score,
            'intimacy_components': intimacy_counts,
            'disclosure_ratio': disclosure_ratio
        }
    
    def _assess_relationship_stage(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess relationship stage from conversation content
        """
        if not conversations:
            return {'stage': 'unknown', 'confidence': 0.0}
            
        # Stage indicator keywords
        stage_keywords = {
            'initial_connection': ['first', 'meet', 'new', 'start', 'beginning', 'introduce', 'hello', 'hi'],
            'exploration': ['get to know', 'learn about', 'tell me', 'about you', 'interested in', 'curious'],
            'establishment': ['relationship', 'together', 'us', 'couple', 'we are', 'dating'],
            'commitment': ['love', 'commitment', 'serious', 'future', 'long term', 'always'],
            'deep_connection': ['trust', 'understand', 'support', 'there for you', 'deep', 'connection']
        }
        
        # Count stage indicators
        stage_counts = {stage: 0 for stage in stage_keywords.keys()}
        
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            for stage, keywords in stage_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        stage_counts[stage] += 1
        
        # Determine primary stage (max count)
        primary_stage = max(stage_counts.items(), key=lambda x: x[1])
        
        # If no clear indicators, use fallback assessment
        if primary_stage[1] == 0:
            # Fallback: use message style and content
            intimacy = self._analyze_intimacy_level(conversations)
            if intimacy['level'] == 'high':
                stage = 'deep_connection'
                confidence = 0.5
            elif intimacy['level'] == 'moderate':
                stage = 'establishment'
                confidence = 0.4
            else:
                stage = 'exploration'
                confidence = 0.3
        else:
            stage = primary_stage[0]
            # Calculate confidence based on how dominant this stage is
            total_indicators = sum(stage_counts.values())
            confidence = primary_stage[1] / total_indicators if total_indicators > 0 else 0.0
        
        return {
            'stage': stage,
            'confidence': confidence,
            'stage_indicators': stage_counts
        }
    
    def _analyze_attachment_style(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze attachment style indicators in conversations
        """
        if not conversations:
            return {}
            
        # Attachment style indicators
        attachment_indicators = {
            'secure': ['trust', 'comfortable', 'open', 'honest', 'support', 'independent', 'together'],
            'anxious': ['worry', 'fear', 'need', 'alone', 'abandonment', 'clingy', 'love me'],
            'avoidant': ['space', 'distance', 'uncomfortable', 'suffocating', 'independence', 'freedom'],
            'disorganized': ['confusing', 'mixed', 'chaotic', 'unpredictable', 'uncertain']
        }
        
        # Count attachment indicators
        attachment_counts = {style: 0 for style in attachment_indicators.keys()}
        
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            for style, keywords in attachment_indicators.items():
                for keyword in keywords:
                    if keyword in text:
                        attachment_counts[style] += 1
        
        # Normalize counts
        total_indicators = sum(attachment_counts.values())
        if total_indicators > 0:
            attachment_ratios = {style: count / total_indicators for style, count in attachment_counts.items()}
        else:
            attachment_ratios = {style: 0.0 for style in attachment_counts.keys()}
        
        # Determine primary attachment style
        primary_style = max(attachment_ratios.items(), key=lambda x: x[1])
        
        # If no clear indicators or very low confidence, mark as undetermined
        if primary_style[1] < 0.3:
            primary_style = ('undetermined', primary_style[1])
        
        return {
            'primary_style': primary_style[0],
            'confidence': primary_style[1],
            'style_ratios': attachment_ratios
        }
    
    def _detect_red_flags(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Detect relationship red flags in conversations
        """
        if not conversations:
            return []
            
        red_flags = []
        
        # Red flag patterns
        red_flag_patterns = {
            'controlling_behavior': ['control', 'permission', 'allow', 'let you', 'can\'t go', 'have to ask'],
            'jealousy': ['jealous', 'suspicious', 'checking', 'other people', 'talking to', 'who is'],
            'disrespect': ['stupid', 'idiot', 'shut up', 'pathetic', 'useless', 'worthless'],
            'manipulation': ['your fault', 'make me', 'because of you', 'if you loved me', 'guilt'],
            'gaslighting': ['never happened', 'imagining', 'remember wrong', 'crazy', 'overreacting'],
            'isolation': ['don\'t need them', 'just us', 'your friends are', 'your family is'],
            'emotional_neglect': ['don\'t care', 'whatever', 'not my problem', 'deal with it'],
            'inconsistency': ['promise', 'forgot', 'supposed to', 'you said']
        }
        
        # Check for red flags
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            for flag_type, patterns in red_flag_patterns.items():
                for pattern in patterns:
                    if pattern in text:
                        flag = f"{flag_type.replace('_', ' ').title()}: '{pattern}' detected"
                        if flag not in red_flags:
                            red_flags.append(flag)
        
        return red_flags
    
    def _detect_positive_indicators(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Detect positive relationship indicators in conversations
        """
        if not conversations:
            return []
            
        positive_indicators = []
        
        # Positive indicator patterns
        positive_patterns = {
            'appreciation': ['thank you', 'appreciate', 'grateful', 'lucky to have you', 'value'],
            'support': ['support', 'here for you', 'help', 'got your back', 'count on me'],
            'affection': ['love', 'care', 'miss', 'adore', 'fond', 'cherish'],
            'respect': ['respect', 'opinion', 'perspective', 'right to', 'your choice', 'up to you'],
            'trust': ['trust', 'believe', 'faith', 'honest', 'truth'],
            'growth': ['future', 'grow', 'better', 'improve', 'learn', 'progress'],
            'healthy_boundaries': ['space', 'time alone', 'independence', 'respect that'],
            'emotional_intimacy': ['feel', 'share', 'open', 'vulnerable', 'emotions', 'connect']
        }
        
        # Check for positive indicators
        for conv in conversations:
            text = conv.get('text', '').lower()
            
            for indicator_type, patterns in positive_patterns.items():
                for pattern in patterns:
                    if pattern in text:
                        indicator = f"{indicator_type.replace('_', ' ').title()}: '{pattern}' detected"
                        if indicator not in positive_indicators:
                            positive_indicators.append(indicator)
        
        return positive_indicators
    
    def _calculate_relationship_score(self, 
                                     emotional_analysis: Dict[str, Any],
                                     communication_patterns: Dict[str, Any],
                                     relationship_dynamics: Dict[str, Any],
                                     red_flags: List[str],
                                     positive_indicators: List[str]) -> float:
        """
        Calculate overall relationship health score
        """
        score = 0.5  # Start at neutral point
        
        # Adjust based on sentiment
        sentiment = emotional_analysis.get('sentiment', {})
        if isinstance(sentiment, dict) and 'compound' in sentiment:
            score += sentiment['compound'] * 0.1  # Sentiment impact: -0.1 to +0.1
        
        # Adjust based on communication
        communication_style = communication_patterns.get('communication_style', {})
        if isinstance(communication_style, dict):
            style = communication_style.get('primary_style', '')
            if style in ['collaborative', 'balanced']:
                score += 0.1
            elif style in ['directive', 'aggressive']:
                score -= 0.1
        
        # Adjust based on relationship dynamics
        power_dynamics = relationship_dynamics.get('power_dynamics', {})
        if isinstance(power_dynamics, dict):
            pattern = power_dynamics.get('pattern', '')
            if pattern == 'balanced':
                score += 0.1
            elif pattern == 'significantly_imbalanced':
                score -= 0.1
        
        # Adjust based on support patterns
        support_patterns = relationship_dynamics.get('support_patterns', {})
        if isinstance(support_patterns, dict):
            support_score = support_patterns.get('support_score', 0)
            score += support_score * 0.1  # Support impact: 0 to +0.1
        
        # Adjust based on conflict patterns
        conflict_patterns = relationship_dynamics.get('conflict_patterns', {})
        if isinstance(conflict_patterns, dict):
            pattern = conflict_patterns.get('pattern', '')
            if pattern == 'constructive_conflict':
                score += 0.05
            elif pattern in ['criticism_defensiveness_cycle', 'criticism_heavy']:
                score -= 0.1
        
        # Adjust based on red flags and positive indicators
        score -= len(red_flags) * 0.05  # Each red flag reduces score
        score += len(positive_indicators) * 0.03  # Each positive indicator increases score
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _calculate_conversation_metrics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall conversation metrics
        """
        if not conversations:
            return {}
            
        # Message timing
        timestamps = []
        for conv in conversations:
            if 'timestamp' in conv:
                try:
                    timestamps.append(datetime.fromisoformat(conv['timestamp']))
                except (ValueError, TypeError):
                    pass
        
        # Calculate time ranges
        time_range = None
        avg_gap = None
        
        if len(timestamps) >= 2:
            timestamps.sort()
            time_range = (timestamps[-1] - timestamps[0]).total_seconds()
            
            gaps = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
            avg_gap = sum(gaps) / len(gaps)
        
        # Message length stats
        message_lengths = [len(conv.get('text', '')) for conv in conversations]
        avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        
        # Content diversity
        unique_words = set()
        total_words = 0
        
        for conv in conversations:
            words = conv.get('text', '').lower().split()
            unique_words.update(words)
            total_words += len(words)
        
        vocabulary_diversity = len(unique_words) / total_words if total_words > 0 else 0
        
        return {
            'message_count': len(conversations),
            'time_range_seconds': time_range,
            'avg_gap_seconds': avg_gap,
            'avg_message_length': avg_length,
            'vocabulary_diversity': vocabulary_diversity,
            'total_words': total_words
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """
        Calculate variance of a list of values
        """
        if not values:
            return 0.0
            
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance
    
    def _calculate_mean(self, values: List[float]) -> float:
        """
        Calculate mean of a list of values
        """
        if not values:
            return 0.0
            
        return sum(values) / len(values)
        
    def _calculate_standard_deviation(self, values: List[float]) -> float:
        """
        Calculate standard deviation without numpy dependency
        """
        if not values:
            return 0.0
            
        variance = self._calculate_variance(values)
        return variance ** 0.5
    
    async def analyze_context(self, user_id: str, current_text: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze current conversation context for real-time recommendations
        """
        try:
            # Analyze current message
            current_analysis = {
                'sentiment': self._analyze_single_message_sentiment(current_text),
                'emotion': self._analyze_single_message_emotion(current_text),
                'intent': self._analyze_message_intent(current_text),
                'urgency': self._assess_message_urgency(current_text),
                'topics': self._extract_topics(current_text)
            }
            
            # Consider conversation context if provided
            if context:
                current_analysis['context_relevance'] = self._assess_context_relevance(current_text, context)
                current_analysis['conversation_flow'] = self._analyze_conversation_flow(current_text, context)
            
            return current_analysis
            
        except Exception as e:
            logger.error(f"Context analysis error: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods
    def _aggregate_emotions(self, emotions: List[Dict]) -> Dict[str, float]:
        """Aggregate emotion classifications"""
        if not emotions:
            return {}
        
        emotion_counts = {}
        for emotion in emotions:
            label = emotion.get('label', 'unknown')
            score = emotion.get('score', 0)
            emotion_counts[label] = emotion_counts.get(label, 0) + score
        
        total = sum(emotion_counts.values())
        return {k: v/total for k, v in emotion_counts.items()} if total > 0 else {}
    
    def _aggregate_sentiments(self, sentiments: List[Dict]) -> Dict[str, float]:
        """Aggregate sentiment classifications"""
        if not sentiments:
            return {}
        
        sentiment_counts = {}
        for sentiment in sentiments:
            label = sentiment.get('label', 'unknown')
            score = sentiment.get('score', 0)
            sentiment_counts[label] = sentiment_counts.get(label, 0) + score
        
        total = sum(sentiment_counts.values())
        return {k: v/total for k, v in sentiment_counts.items()} if total > 0 else {}
    
    def _calculate_emotional_stability(self, emotions: List[Dict]) -> float:
        """Calculate emotional stability score"""
        if not emotions:
            return 0.5
        
        # Calculate variance in emotional scores
        scores = [e.get('score', 0) for e in emotions]
        if len(scores) < 2:
            return 0.5
        
        variance = py_var(scores)
        # Lower variance = higher stability
        stability = max(0, 1 - variance)
        return stability
    
    def _calculate_emotional_intensity(self, emotions: List[Dict]) -> float:
        """Calculate average emotional intensity"""
        if not emotions:
            return 0.5
        
        scores = [e.get('score', 0) for e in emotions]
        return py_mean(scores)
    
    def _get_dominant_emotions(self, emotion_distribution: Dict[str, float]) -> List[str]:
        """Get top 3 dominant emotions"""
        if not emotion_distribution:
            return []
        
        sorted_emotions = sorted(emotion_distribution.items(), key=lambda x: x[1], reverse=True)
        return [emotion[0] for emotion in sorted_emotions[:3]]
    
    def _determine_communication_style(self, patterns: Dict) -> str:
        """Determine overall communication style"""
        question_ratio = patterns.get('question_ratio', 0)
        exclamation_ratio = patterns.get('exclamation_ratio', 0)
        emoji_ratio = patterns.get('emoji_ratio', 0)
        
        if question_ratio > 0.3:
            return 'inquisitive'
        elif exclamation_ratio > 0.2:
            return 'enthusiastic'
        elif emoji_ratio > 0.5:
            return 'expressive'
        else:
            return 'neutral'
    
    def _detect_conflict_indicators(self, conversations: List[Dict]) -> List[str]:
        """Detect signs of conflict"""
        conflict_keywords = ['argue', 'fight', 'disagree', 'angry', 'upset', 'frustrated']
        indicators = []
        
        for conv in conversations:
            text = conv['text'].lower()
            for keyword in conflict_keywords:
                if keyword in text:
                    indicators.append(keyword)
        
        return list(set(indicators))
    
    def _detect_support_indicators(self, conversations: List[Dict]) -> List[str]:
        """Detect signs of emotional support"""
        support_keywords = ['support', 'help', 'understand', 'listen', 'care', 'comfort']
        indicators = []
        
        for conv in conversations:
            text = conv['text'].lower()
            for keyword in support_keywords:
                if keyword in text:
                    indicators.append(keyword)
        
        return list(set(indicators))
    
    def _determine_relationship_stage(self, conversations: List[Dict]) -> str:
        """Determine current relationship stage"""
        # Simplified relationship stage detection
        intimacy_keywords = ['love', 'relationship', 'future', 'together']
        casual_keywords = ['fun', 'hang out', 'chat', 'talk']
        
        intimacy_count = 0
        casual_count = 0
        
        for conv in conversations:
            text = conv['text'].lower()
            intimacy_count += sum(1 for word in text.split() if word in intimacy_keywords)
            casual_count += sum(1 for word in text.split() if word in casual_keywords)
        
        if intimacy_count > casual_count:
            return 'serious'
        elif casual_count > intimacy_count:
            return 'casual'
        else:
            return 'developing'
    
    def _calculate_duration(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Calculate conversation duration"""
        if len(conversations) < 2:
            return {'total_duration': 0, 'unit': 'minutes'}
        
        timestamps = [conv.get('timestamp') for conv in conversations if conv.get('timestamp')]
        if len(timestamps) < 2:
            return {'total_duration': 0, 'unit': 'minutes'}
        
        # Convert to datetime objects if they're strings
        datetime_objects = []
        for ts in timestamps:
            if isinstance(ts, str):
                try:
                    datetime_objects.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                except:
                    continue
            elif isinstance(ts, datetime):
                datetime_objects.append(ts)
        
        if len(datetime_objects) < 2:
            return {'total_duration': 0, 'unit': 'minutes'}
        
        duration = max(datetime_objects) - min(datetime_objects)
        return {
            'total_duration': duration.total_seconds() / 60,  # in minutes
            'unit': 'minutes'
        }
    
    def _calculate_message_frequency(self, conversations: List[Dict]) -> float:
        """Calculate messages per hour"""
        duration_info = self._calculate_duration(conversations)
        duration_minutes = duration_info.get('total_duration', 0)
        
        if duration_minutes == 0:
            return 0
        
        messages_per_hour = (len(conversations) / duration_minutes) * 60
        return messages_per_hour
    
    def _analyze_response_patterns(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Analyze response patterns between participants"""
        user_responses = []
        partner_responses = []
        
        for i in range(1, len(conversations)):
            current = conversations[i]
            previous = conversations[i-1]
            
            if current.get('sender') != previous.get('sender'):
                # This is a response
                if current.get('sender') == 'user':
                    user_responses.append(len(current['text'].split()))
                else:
                    partner_responses.append(len(current['text'].split()))
        
        return {
            'user_avg_response_length': py_mean(user_responses) if user_responses else 0,
            'partner_avg_response_length': py_mean(partner_responses) if partner_responses else 0,
            'response_balance': len(user_responses) / len(partner_responses) if partner_responses else 0
        }
    
    async def analyze_batch(self, user_id: str, batch_data: Dict[str, Any]):
        """
        Analyze a batch of conversation data in background
        """
        try:
            logger.info(f"Starting batch analysis for user {user_id}")
            
            conversations = batch_data.get('conversations', [])
            if not conversations:
                logger.warning(f"No conversations found in batch for user {user_id}")
                return
            
            # Perform comprehensive analysis
            analysis_result = await self.analyze(
                user_id=user_id,
                conversation_history=conversations,
                analysis_type="comprehensive"
            )
            
            # Store results (implement storage logic)
            # await self._store_analysis_results(user_id, analysis_result)
            
            logger.info(f"Batch analysis completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Batch analysis error for user {user_id}: {str(e)}")