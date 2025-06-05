#!/usr/bin/env python3
"""
Minimal Implementations for Core Components
Provides basic functionality without heavy ML/AI dependencies
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Sequence
from datetime import datetime
import random
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pathlib import Path
import math

logger = logging.getLogger(__name__)

# Pure Python implementations of NumPy functions
def py_mean(data: Sequence[Union[int, float]]) -> float:
    """Pure Python implementation of numpy.mean"""
    if not data:
        return 0.0
    return sum(data) / len(data)

def py_var(data: Sequence[Union[int, float]]) -> float:
    """Pure Python implementation of numpy.var"""
    if len(data) < 2:
        return 0.0
    
    mean = py_mean(data)
    return sum((x - mean) ** 2 for x in data) / len(data)

def py_std(data: Sequence[Union[int, float]]) -> float:
    """Pure Python implementation of numpy.std"""
    return math.sqrt(py_var(data))

def py_random_uniform(low: float, high: float, size: Union[int, Tuple[int, ...]] = None) -> Union[float, List[float]]:
    """Pure Python implementation of numpy.random.uniform"""
    if size is None:
        return low + (high - low) * random.random()
    
    if isinstance(size, int):
        return [low + (high - low) * random.random() for _ in range(size)]
    
    # Handle multi-dimensional arrays
    if len(size) == 1:
        return [low + (high - low) * random.random() for _ in range(size[0])]
    
    # For 2D arrays
    if len(size) == 2:
        return [[low + (high - low) * random.random() for _ in range(size[1])] for _ in range(size[0])]
    
    # Default fallback
    return low + (high - low) * random.random()

def py_cumsum(data: Sequence[Union[int, float]]) -> List[float]:
    """Pure Python implementation of numpy.cumsum"""
    result = []
    total = 0
    for value in data:
        total += value
        result.append(total)
    return result

def py_random_rand(size: int) -> List[float]:
    """Pure Python implementation of numpy.random.rand"""
    return [random.random() for _ in range(size)]

class MinimalConversationAnalyzer:
    """
    Minimal conversation analyzer using basic NLP and rule-based approaches
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.communication_patterns = {
            'positive_words': ['love', 'happy', 'great', 'wonderful', 'amazing', 'perfect', 'beautiful'],
            'negative_words': ['hate', 'angry', 'terrible', 'awful', 'horrible', 'worst', 'disgusting'],
            'relationship_words': ['relationship', 'together', 'couple', 'partner', 'boyfriend', 'girlfriend', 'husband', 'wife'],
            'conflict_words': ['fight', 'argue', 'disagree', 'conflict', 'problem', 'issue', 'wrong']
        }
        # Add more sophisticated conflict detection patterns
        self.conflict_patterns = {
            'criticism': ['always', 'never', 'you always', 'you never', 'why do you', 'wrong with you'],
            'defensiveness': ['not my fault', 'wasn\'t me', 'i didn\'t', 'don\'t blame me', 'it\'s not me'],
            'contempt': ['whatever', 'ridiculous', 'pathetic', 'stupid', 'worthless', 'eye roll'],
            'stonewalling': ['forget it', 'never mind', 'don\'t want to talk', 'shut down', 'silence']
        }
        # Add emotional intensity markers
        self.emotional_intensity_markers = {
            'high': ['extremely', 'absolutely', 'furious', 'ecstatic', 'devastated', 'cannot stand', 'hate'],
            'medium': ['very', 'quite', 'upset', 'happy', 'sad', 'annoyed', 'pleased'],
            'low': ['somewhat', 'a bit', 'slightly', 'a little', 'kind of', 'sort of']
        }
        # Add more sophisticated conflict detection patterns
        self.conflict_patterns = {
            'criticism': ['always', 'never', 'you always', 'you never', 'why do you', 'wrong with you'],
            'defensiveness': ['not my fault', 'wasn\'t me', 'i didn\'t', 'don\'t blame me', 'it\'s not me'],
            'contempt': ['whatever', 'ridiculous', 'pathetic', 'stupid', 'worthless', 'eye roll'],
            'stonewalling': ['forget it', 'never mind', 'don\'t want to talk', 'shut down', 'silence']
        }
        # Add emotional intensity markers
        self.emotional_intensity_markers = {
            'high': ['extremely', 'absolutely', 'furious', 'ecstatic', 'devastated', 'cannot stand', 'hate'],
            'medium': ['very', 'quite', 'upset', 'happy', 'sad', 'annoyed', 'pleased'],
            'low': ['somewhat', 'a bit', 'slightly', 'a little', 'kind of', 'sort of']
        }
    
    def analyze_basic_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Basic sentiment analysis using VADER
        """
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'sentiment_label': self._get_sentiment_label(scores['compound'])
        }
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_communication_style(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Basic communication style analysis
        """
        total_messages = len(conversations)
        if total_messages == 0:
            return {'style': 'unknown', 'confidence': 0.0}
        
        # Count patterns
        question_count = sum(1 for conv in conversations if '?' in conv.get('text', ''))
        exclamation_count = sum(1 for conv in conversations if '!' in conv.get('text', ''))
        avg_length = sum(len(conv.get('text', '')) for conv in conversations) / total_messages
        
        # Determine style
        question_ratio = question_count / total_messages
        exclamation_ratio = exclamation_count / total_messages
        
        if question_ratio > 0.3:
            style = 'inquisitive'
        elif exclamation_ratio > 0.2:
            style = 'expressive'
        elif avg_length > 100:
            style = 'detailed'
        elif avg_length < 20:
            style = 'concise'
        else:
            style = 'balanced'
        
        return {
            'style': style,
            'question_ratio': question_ratio,
            'exclamation_ratio': exclamation_ratio,
            'avg_message_length': avg_length,
            'confidence': 0.7
        }
    
    def detect_red_flags(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Basic red flag detection using keyword matching
        """
        red_flags = []
        red_flag_patterns = {
            'controlling_behavior': ['control', 'forbid', 'not allowed', 'permission'],
            'jealousy': ['jealous', 'suspicious', 'checking phone', 'who were you with'],
            'aggression': ['yell', 'scream', 'hit', 'hurt', 'violence'],
            'isolation': ['friends are bad', 'family problems', 'only me', 'nobody else'],
            'manipulation': ['guilt trip', 'your fault', 'always wrong', 'crazy']
        }
        
        all_text = ' '.join([conv.get('text', '').lower() for conv in conversations])
        
        for flag_type, patterns in red_flag_patterns.items():
            for pattern in patterns:
                if pattern in all_text:
                    red_flags.append(f"Potential {flag_type.replace('_', ' ')}: '{pattern}' detected")
        
        return red_flags
    
    def detect_positive_indicators(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Basic positive indicator detection
        """
        positive_indicators = []
        positive_patterns = {
            'appreciation': ['thank you', 'grateful', 'appreciate', 'lucky to have'],
            'support': ['support', 'help', 'there for you', 'understand'],
            'affection': ['love you', 'miss you', 'care about', 'special'],
            'communication': ['talk about', 'discuss', 'share', 'listen'],
            'future_planning': ['future', 'plans', 'together', 'someday']
        }
        
        all_text = ' '.join([conv.get('text', '').lower() for conv in conversations])
        
        for indicator_type, patterns in positive_patterns.items():
            for pattern in patterns:
                if pattern in all_text:
                    positive_indicators.append(f"Positive {indicator_type.replace('_', ' ')}: '{pattern}' detected")
        
        return positive_indicators
    
    def detect_conflict_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect common conflict patterns based on Gottman's Four Horsemen
        """
        conflict_results = {
            'patterns_detected': [],
            'criticism_count': 0,
            'defensiveness_count': 0, 
            'contempt_count': 0,
            'stonewalling_count': 0,
            'severity': 'low',
            'examples': []
        }
        
        all_text = ' '.join([conv.get('text', '').lower() for conv in conversations])
        
        # Detect conflict patterns
        for pattern_type, keywords in self.conflict_patterns.items():
            pattern_count = 0
            pattern_examples = []
            
            for keyword in keywords:
                if keyword in all_text:
                    pattern_count += all_text.count(keyword)
                    
                    # Find an example in context
                    for conv in conversations:
                        text = conv.get('text', '').lower()
                        if keyword in text:
                            pattern_examples.append({
                                'pattern': pattern_type,
                                'keyword': keyword,
                                'example': text[:text.find(keyword) + len(keyword) + 30]  # Get some context
                            })
                            break
            
            if pattern_count > 0:
                if pattern_type == 'criticism':
                    conflict_results['criticism_count'] = pattern_count
                elif pattern_type == 'defensiveness':
                    conflict_results['defensiveness_count'] = pattern_count
                elif pattern_type == 'contempt':
                    conflict_results['contempt_count'] = pattern_count
                elif pattern_type == 'stonewalling':
                    conflict_results['stonewalling_count'] = pattern_count
                
                conflict_results['patterns_detected'].append({
                    'type': pattern_type,
                    'count': pattern_count
                })
                
                # Add up to 2 examples per pattern
                if pattern_examples:
                    conflict_results['examples'].extend(pattern_examples[:2])
        
        # Calculate overall severity
        total_patterns = (conflict_results['criticism_count'] + 
                          conflict_results['defensiveness_count'] + 
                          conflict_results['contempt_count'] + 
                          conflict_results['stonewalling_count'])
        
        if total_patterns > 10:
            conflict_results['severity'] = 'high'
        elif total_patterns > 5:
            conflict_results['severity'] = 'medium'
        else:
            conflict_results['severity'] = 'low'
        
        return conflict_results
        
    def analyze_emotional_intensity(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the intensity of emotions expressed in conversations
        """
        # Default result
        result = {
            'overall_intensity': 'medium',
            'intensity_score': 0.5,
            'primary_emotions': [],
            'emotional_volatility': 'low',
            'intensity_markers': []
        }
        
        all_text = ' '.join([conv.get('text', '').lower() for conv in conversations])
        
        # Basic emotion categories
        emotions = {
            'joy': ['happy', 'joy', 'excited', 'glad', 'pleased', 'delight', 'content'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'blue', 'upset', 'disappointed'],
            'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'terrified'],
            'disgust': ['disgusted', 'repulsed', 'revolted', 'dislike', 'hate'],
            'surprise': ['surprised', 'shocked', 'astonished', 'amazed', 'startled'],
            'love': ['love', 'adore', 'care', 'cherish', 'affection'],
            'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed']
        }
        
        # Count emotion words
        emotion_counts = {}
        for emotion, keywords in emotions.items():
            count = sum(all_text.count(word) for word in keywords)
            emotion_counts[emotion] = count
        
        # Find primary emotions (top 2)
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        primary_emotions = [emotion for emotion, count in sorted_emotions[:2] if count > 0]
        result['primary_emotions'] = primary_emotions
        
        # Calculate intensity based on intensity markers
        high_intensity_count = 0
        medium_intensity_count = 0
        low_intensity_count = 0
        
        for intensity, markers in self.emotional_intensity_markers.items():
            for marker in markers:
                if marker in all_text:
                    count = all_text.count(marker)
                    result['intensity_markers'].append({
                        'marker': marker,
                        'intensity': intensity,
                        'count': count
                    })
                    
                    if intensity == 'high':
                        high_intensity_count += count
                    elif intensity == 'medium':
                        medium_intensity_count += count
                    else:
                        low_intensity_count += count
        
        # Calculate intensity score (0-1 scale)
        total_markers = max(1, high_intensity_count + medium_intensity_count + low_intensity_count)
        intensity_score = (high_intensity_count * 1.0 + medium_intensity_count * 0.5 + low_intensity_count * 0.25) / total_markers
        result['intensity_score'] = intensity_score
        
        # Determine overall intensity
        if intensity_score > 0.7:
            result['overall_intensity'] = 'high'
        elif intensity_score > 0.4:
            result['overall_intensity'] = 'medium'
        else:
            result['overall_intensity'] = 'low'
        
        # Calculate emotional volatility
        if len(conversations) < 3:
            result['emotional_volatility'] = 'undetermined (insufficient data)'
        else:
            # Check for emotional shifts
            sentiment_shifts = 0
            prev_sentiment = None
            
            for conv in conversations:
                text = conv.get('text', '')
                sentiment = self.analyze_basic_sentiment(text)['sentiment_label']
                
                if prev_sentiment and sentiment != prev_sentiment:
                    sentiment_shifts += 1
                
                prev_sentiment = sentiment
            
            volatility_ratio = sentiment_shifts / (len(conversations) - 1) if len(conversations) > 1 else 0
            
            if volatility_ratio > 0.5:
                result['emotional_volatility'] = 'high'
            elif volatility_ratio > 0.25:
                result['emotional_volatility'] = 'medium'
            else:
                result['emotional_volatility'] = 'low'
        
        return result
        
    def detect_topics(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Detect main topics in the conversation
        """
        topics = []
        topic_keywords = {
            'communication': ['talk', 'communicate', 'discuss', 'conversation', 'chat', 'say'],
            'emotions': ['feel', 'emotion', 'happy', 'sad', 'angry', 'upset', 'joy'],
            'relationship': ['relationship', 'together', 'couple', 'partner', 'love', 'commitment'],
            'finances': ['money', 'budget', 'finance', 'spend', 'afford', 'cost', 'expense'],
            'family': ['family', 'parents', 'children', 'kids', 'mom', 'dad', 'relatives'],
            'leisure': ['fun', 'hobby', 'vacation', 'trip', 'enjoy', 'relax', 'activities'],
            'work': ['job', 'work', 'career', 'office', 'business', 'professional'],
            'home': ['home', 'house', 'apartment', 'chores', 'cleaning', 'living space'],
            'health': ['health', 'doctor', 'sick', 'wellness', 'exercise', 'diet', 'sleep'],
            'future': ['future', 'plan', 'goal', 'dream', 'aspiration', 'hope', 'someday']
        }
        
        all_text = ' '.join([conv.get('text', '').lower() for conv in conversations])
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    topics.append(topic)
                    break
        
        return topics

class MinimalAITherapist:
    """
    Minimal AI therapist providing basic recommendations
    """
    
    def __init__(self):
        self.recommendation_templates = {
            'communication': [
                "Try using 'I' statements to express your feelings without blame.",
                "Practice active listening by summarizing what your partner says.",
                "Set aside dedicated time for meaningful conversations."
            ],
            'conflict_resolution': [
                "Take a break when emotions run high and return to discuss calmly.",
                "Focus on the specific issue rather than bringing up past problems.",
                "Look for compromise solutions that address both partners' needs."
            ],
            'emotional_support': [
                "Validate your partner's feelings even if you don't agree with their perspective.",
                "Express appreciation for the positive things your partner does.",
                "Create regular opportunities for emotional intimacy and connection."
            ],
            'relationship_building': [
                "Plan regular date nights or special activities together.",
                "Share your goals and dreams with each other.",
                "Practice gratitude by acknowledging what you value in your relationship."
            ]
        }
        
        # Add topic-specific recommendations
        self.topic_recommendations = {
            'communication': [
                "Schedule a weekly check-in to discuss relationship matters openly.",
                "Practice reflective listening by paraphrasing what your partner says.",
                "Use 'I' statements instead of 'you' statements during difficult conversations."
            ],
            'emotions': [
                "Create a safe space for sharing feelings without judgment.",
                "Acknowledge your partner's emotions even when you don't understand them.",
                "Express appreciation for emotional vulnerability."
            ],
            'finances': [
                "Create a shared budget that respects both partners' priorities.",
                "Have regular, non-judgmental conversations about financial goals.",
                "Be transparent about spending and financial decisions."
            ],
            'family': [
                "Establish clear boundaries with extended family together.",
                "Support each other during family challenges.",
                "Discuss expectations about family involvement in your relationship."
            ],
            'leisure': [
                "Find activities you both enjoy and make time for them regularly.",
                "Respect each other's need for individual hobbies and interests.",
                "Try new experiences together to create shared memories."
            ]
        }
        
        # Add conflict pattern recommendations
        self.conflict_pattern_recommendations = {
            'criticism': [
                "Replace criticism with gentle, specific requests for change.",
                "Focus on the behavior, not the person's character.",
                "Express needs in positive terms rather than complaints."
            ],
            'defensiveness': [
                "Take responsibility for at least part of the issue.",
                "Listen fully to your partner's concern before responding.",
                "Ask clarifying questions instead of immediately defending yourself."
            ],
            'contempt': [
                "Build a culture of appreciation and respect.",
                "Express frustrations respectfully without mockery or disrespect.",
                "Remember your partner's positive qualities during conflicts."
            ],
            'stonewalling': [
                "Recognize when you're feeling overwhelmed and request a break.",
                "Learn self-soothing techniques to manage emotional flooding.",
                "Return to the conversation when you're calm and ready to engage."
            ]
        }
        
        # Add emotional intensity recommendations
        self.emotional_intensity_recommendations = {
            'high': [
                "Practice emotional regulation techniques like deep breathing when emotions run high.",
                "Take a time-out when emotions become overwhelming, with a clear plan to return to the discussion.",
                "Journal intense feelings before discussing them to gain clarity."
            ],
            'medium': [
                "Balance emotional expression with rational problem-solving.",
                "Check that your emotional responses match the situation.",
                "Validate each other's emotions before moving to solutions."
            ],
            'low': [
                "Create opportunities to deepen emotional connection.",
                "Practice expressing feelings more directly and openly.",
                "Share vulnerabilities to build emotional intimacy."
            ]
        }
    
    def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate basic recommendations based on analysis
        """
        recommendations = []
        
        # Check sentiment
        emotional_analysis = analysis_results.get('emotional_analysis', {})
        sentiment = analysis_results.get('sentiment', {})
        if isinstance(emotional_analysis, dict) and emotional_analysis.get('sentiment_label') == 'negative':
            recommendations.extend(random.sample(self.recommendation_templates['conflict_resolution'], 2))
        elif isinstance(sentiment, dict) and sentiment.get('sentiment_label') == 'negative':
            recommendations.extend(random.sample(self.recommendation_templates['conflict_resolution'], 2))
        
        # Check red flags
        red_flags = analysis_results.get('red_flags', [])
        if red_flags:
            recommendations.append("Consider seeking professional counseling to address concerning patterns.")
            recommendations.extend(random.sample(self.recommendation_templates['communication'], 1))
        
        # Check positive indicators
        positive_indicators = analysis_results.get('positive_indicators', [])
        if positive_indicators:
            recommendations.extend(random.sample(self.recommendation_templates['relationship_building'], 1))
        
        # Check conflict patterns
        conflict_patterns = analysis_results.get('conflict_patterns', {})
        if conflict_patterns and 'patterns_detected' in conflict_patterns:
            for pattern in conflict_patterns.get('patterns_detected', []):
                pattern_type = pattern.get('type')
                if pattern_type in self.conflict_pattern_recommendations:
                    recommendations.append(random.choice(self.conflict_pattern_recommendations[pattern_type]))
        
        # Check emotional intensity
        emotional_intensity = analysis_results.get('emotional_intensity', {})
        if emotional_intensity and 'overall_intensity' in emotional_intensity:
            intensity = emotional_intensity.get('overall_intensity')
            if intensity in self.emotional_intensity_recommendations:
                recommendations.append(random.choice(self.emotional_intensity_recommendations[intensity]))
        
        # Check for topics and add topic-specific recommendations
        text = analysis_results.get('text', '')
        topics = analysis_results.get('topics', [])
        
        if not topics and text:
            analyzer = MinimalConversationAnalyzer()
            topics = analyzer.detect_topics([{"text": text}])
            
        topic_recommendations = self.generate_topic_recommendations(topics)
        recommendations.extend(topic_recommendations)
        
        # Default recommendations
        if not recommendations:
            recommendations.extend(random.sample(self.recommendation_templates['communication'], 2))
            recommendations.extend(random.sample(self.recommendation_templates['emotional_support'], 1))
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate basic relationship insights
        """
        insights = {
            'relationship_health_score': self._calculate_health_score(analysis_results),
            'key_strengths': self._identify_strengths(analysis_results),
            'areas_for_improvement': self._identify_improvements(analysis_results),
            'communication_assessment': self._assess_communication(analysis_results)
        }
        
        return insights
    
    def generate_conflict_recommendations(self, conflict_patterns: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on conflict patterns
        """
        recommendations = []
        
        # Check severity
        severity = conflict_patterns.get('severity', 'low')
        
        # Generate general conflict resolution recommendation based on severity
        if severity == 'high':
            recommendations.append("Consider taking a temporary break from difficult discussions and focus on rebuilding positive interactions.")
        
        # Check patterns detected
        patterns_detected = conflict_patterns.get('patterns_detected', [])
        
        # Find the most frequent pattern
        most_frequent_pattern = None
        highest_count = 0
        
        for pattern in patterns_detected:
            pattern_type = pattern.get('type')
            count = pattern.get('count', 0)
            
            if count > highest_count:
                highest_count = count
                most_frequent_pattern = pattern_type
        
        # Add specific recommendations for the most frequent pattern
        if most_frequent_pattern and most_frequent_pattern in self.conflict_pattern_recommendations:
            # Add all recommendations for this pattern
            pattern_recs = self.conflict_pattern_recommendations[most_frequent_pattern]
            recommendations.extend(pattern_recs)
        
        # Add general conflict resolution recommendation
        recommendations.append("Use a structured approach to conflict: describe the situation objectively, express feelings, specify needs, and offer positive solutions.")
        
        return recommendations[:3]  # Limit to 3 recommendations
        
    def generate_emotional_intensity_recommendations(self, emotional_intensity: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on emotional intensity analysis
        """
        recommendations = []
        
        # Check overall intensity
        intensity = emotional_intensity.get('overall_intensity', 'medium')
        
        # Add intensity-specific recommendations
        if intensity in self.emotional_intensity_recommendations:
            recommendations.extend(random.sample(self.emotional_intensity_recommendations[intensity], 2))
        
        # Check emotional volatility
        volatility = emotional_intensity.get('emotional_volatility', 'low')
        if volatility == 'high':
            recommendations.append("Work on emotional regulation and self-soothing techniques to manage rapid emotional shifts.")
        
        # Check primary emotions
        primary_emotions = emotional_intensity.get('primary_emotions', [])
        
        emotion_specific_recommendations = {
            'anger': "Practice anger management techniques such as timeouts and deep breathing when emotions escalate.",
            'sadness': "Create space for expressing sadness and grief without rushing to fix feelings.",
            'fear': "Acknowledge fears and anxieties openly, and develop reassurance routines as a couple.",
            'joy': "Build on positive experiences by scheduling activities that bring shared joy.",
            'love': "Express affection in your partner's preferred love language regularly.",
            'disgust': "Address sources of resentment early before they create lasting negative patterns.",
            'surprise': "Embrace unpredictability by creating occasional surprises for each other."
        }
        
        for emotion in primary_emotions:
            if emotion in emotion_specific_recommendations:
                recommendations.append(emotion_specific_recommendations[emotion])
                break  # Just add one emotion-specific recommendation
        
        return recommendations[:3]  # Limit to 3 recommendations
        
    def generate_topic_recommendations(self, topics: List[str]) -> List[str]:
        """
        Generate recommendations based on detected topics
        """
        recommendations = []
        
        for topic in topics:
            if topic in self.topic_recommendations:
                # Add one recommendation per detected topic
                if self.topic_recommendations[topic]:
                    recommendations.append(random.choice(self.topic_recommendations[topic]))
        
        return recommendations[:2]  # Limit to 2 topic-specific recommendations
    
    def _calculate_health_score(self, analysis_results: Dict[str, Any]) -> float:
        """
        Calculate a relationship health score based on analysis results
        """
        health_score = 0.5  # Start at neutral
        
        # Adjust based on sentiment
        sentiment = analysis_results.get('sentiment', {})
        if isinstance(sentiment, dict) and 'compound' in sentiment:
            # Adjust health score based on sentiment (-0.2 to +0.2)
            health_score += sentiment['compound'] * 0.2
        
        # Adjust based on red flags
        red_flags = analysis_results.get('red_flags', [])
        # Each red flag reduces health score
        health_score -= len(red_flags) * 0.05
        
        # Adjust based on positive indicators
        positive_indicators = analysis_results.get('positive_indicators', [])
        # Each positive indicator increases health score
        health_score += len(positive_indicators) * 0.05
        
        # Ensure score is between 0 and 1
        health_score = max(0.0, min(1.0, health_score))
        
        return health_score
    
    def _identify_strengths(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Identify relationship strengths based on analysis
        """
        strengths = []
        
        # Check positive indicators
        positive_indicators = analysis_results.get('positive_indicators', [])
        
        # Group similar indicators
        strength_categories = {
            'communication': ['communication', 'listen', 'talk', 'discuss'],
            'emotional_support': ['support', 'understanding', 'empathy', 'validation'],
            'affection': ['love', 'affection', 'care', 'appreciation'],
            'trust': ['trust', 'honesty', 'transparency'],
            'teamwork': ['teamwork', 'cooperation', 'partnership', 'together']
        }
        
        # Track which categories we've found
        found_categories = set()
        
        # Analyze positive indicators to identify strength categories
        for indicator in positive_indicators:
            indicator_lower = indicator.lower()
            for category, keywords in strength_categories.items():
                if any(keyword in indicator_lower for keyword in keywords) and category not in found_categories:
                    if category == 'communication':
                        strengths.append("Effective communication")
                    elif category == 'emotional_support':
                        strengths.append("Emotional support and understanding")
                    elif category == 'affection':
                        strengths.append("Expressions of affection and appreciation")
                    elif category == 'trust':
                        strengths.append("Trust and honesty")
                    elif category == 'teamwork':
                        strengths.append("Teamwork and collaboration")
                    
                    found_categories.add(category)
        
        # Check sentiment for positive emotional connection
        sentiment = analysis_results.get('sentiment', {})
        if isinstance(sentiment, dict) and sentiment.get('compound', 0) > 0.2:
            strengths.append("Positive emotional connection")
        
        # Add default strength if none found
        if not strengths:
            strengths.append("Willingness to seek improvement")
        
        return strengths
    
    def _identify_improvements(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Identify areas for improvement based on analysis
        """
        improvements = []
        
        # Check red flags
        red_flags = analysis_results.get('red_flags', [])
        
        # Group similar red flags
        improvement_categories = {
            'communication': ['miscommunication', 'misunderstanding', 'not listening'],
            'conflict': ['argument', 'fight', 'conflict', 'disagreement'],
            'boundaries': ['controlling', 'boundary', 'privacy', 'space'],
            'trust': ['suspicious', 'jealous', 'trust issues'],
            'emotional_expression': ['emotional', 'feelings', 'express', 'shut down']
        }
        
        # Track which categories we've found
        found_categories = set()
        
        # Analyze red flags to identify improvement categories
        for flag in red_flags:
            flag_lower = flag.lower()
            for category, keywords in improvement_categories.items():
                if any(keyword in flag_lower for keyword in keywords) and category not in found_categories:
                    if category == 'communication':
                        improvements.append("Communication clarity and effectiveness")
                    elif category == 'conflict':
                        improvements.append("Conflict resolution skills")
                    elif category == 'boundaries':
                        improvements.append("Healthy boundary setting and respect")
                    elif category == 'trust':
                        improvements.append("Trust building and transparency")
                    elif category == 'emotional_expression':
                        improvements.append("Emotional expression and vulnerability")
                    
                    found_categories.add(category)
        
        # Check sentiment for negative emotional patterns
        sentiment = analysis_results.get('sentiment', {})
        if isinstance(sentiment, dict) and sentiment.get('compound', 0) < -0.2:
            improvements.append("Positive interaction patterns")
        
        # Add default improvement if none found
        if not improvements:
            improvements.append("Deepening emotional connection")
        
        return improvements
    
    def _assess_communication(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess communication patterns
        """
        # Default assessment
        assessment = {
            'effectiveness': 'moderate',
            'balance': 'somewhat balanced',
            'emotional_tone': 'neutral',
            'listening_quality': 'adequate',
            'improvement_areas': []
        }
        
        # Check text for communication patterns
        text = analysis_results.get('text', '')
        if text:
            # Check for questions (listening)
            question_ratio = text.count('?') / (len(text) / 100) if len(text) > 0 else 0
            if question_ratio > 0.5:
                assessment['listening_quality'] = 'good'
            elif question_ratio < 0.1:
                assessment['listening_quality'] = 'needs improvement'
                assessment['improvement_areas'].append('Active listening and asking questions')
            
            # Check interruption patterns
            interruption_indicators = ['interrupt', 'cut off', 'let me finish', 'don\'t interrupt']
            if any(indicator in text.lower() for indicator in interruption_indicators):
                assessment['balance'] = 'imbalanced'
                assessment['improvement_areas'].append('Taking turns and avoiding interruptions')
            
            # Check for clarification attempts
            clarification_indicators = ['what do you mean', 'did you mean', 'clarify', 'understand']
            if any(indicator in text.lower() for indicator in clarification_indicators):
                assessment['effectiveness'] = 'improving'
            
            # Check sentiment for emotional tone
            sentiment = analysis_results.get('sentiment', {})
            if isinstance(sentiment, dict):
                compound = sentiment.get('compound', 0)
                if compound > 0.3:
                    assessment['emotional_tone'] = 'positive'
                elif compound < -0.3:
                    assessment['emotional_tone'] = 'negative'
                    assessment['improvement_areas'].append('Maintaining a positive emotional tone')
        
        return assessment


class MinimalKnowledgeBase:
    """
    Minimal knowledge base implementation
    """
    
    def __init__(self, storage_path: str = "./knowledge_base"):
        self.storage_path = Path(storage_path)
        self.documents = []
        self.load_documents()
    
    def load_documents(self):
        """
        Load documents from the knowledge base directory
        """
        try:
            if not self.storage_path.exists():
                self.storage_path.mkdir(parents=True, exist_ok=True)
                self._create_initial_documents()
                return
            
            for file_path in self.storage_path.glob("**/*.json"):
                try:
                    with open(file_path, 'r') as f:
                        document = json.load(f)
                        self.documents.append(document)
                except Exception as e:
                    logger.warning(f"Failed to load document {file_path}: {e}")
            
            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
    
    def _create_initial_documents(self):
        """
        Create initial documents for the knowledge base
        """
        initial_documents = [
            {
                "id": "communication_patterns",
                "title": "Common Communication Patterns",
                "content": json.dumps({
                    "patterns": [
                        {"name": "Criticism", "description": "Attacking character rather than behavior"},
                        {"name": "Defensiveness", "description": "Self-protection in the form of righteous indignation"},
                        {"name": "Contempt", "description": "Attacking with intention to insult or abuse"},
                        {"name": "Stonewalling", "description": "Withdrawing from conversation as a way to avoid conflict"},
                        {"name": "Validation", "description": "Acknowledging partner's perspective and feelings"},
                        {"name": "Active Listening", "description": "Fully concentrating on what is being said"},
                        {"name": "I Statements", "description": "Speaking from personal experience without blame"}
                    ]
                }),
                "type": "reference",
                "tags": ["communication", "patterns", "gottman"]
            },
            {
                "id": "relationship_red_flags",
                "title": "Relationship Red Flags",
                "content": json.dumps({
                    "red_flags": [
                        {"category": "control", "indicators": ["isolation", "monitoring", "decision making", "financial control"]},
                        {"category": "respect", "indicators": ["belittling", "public humiliation", "dismissiveness"]},
                        {"category": "trust", "indicators": ["jealousy", "accusations", "privacy invasion"]},
                        {"category": "conflict", "indicators": ["escalation", "violence", "threats", "intimidation"]},
                        {"category": "balance", "indicators": ["inequality", "one-sided effort", "sacrifice imbalance"]}
                    ]
                }),
                "type": "reference",
                "tags": ["red flags", "warning signs", "safety"]
            },
            {
                "id": "therapeutic_approaches",
                "title": "Therapeutic Approaches",
                "content": json.dumps({
                    "approaches": [
                        {
                            "name": "Gottman Method",
                            "focus": "Building friendship, managing conflict, creating shared meaning",
                            "techniques": ["love maps", "fondness and admiration", "turning towards", "positive perspective"]
                        },
                        {
                            "name": "Emotionally Focused Therapy",
                            "focus": "Attachment bonds, emotional responses",
                            "techniques": ["tracking patterns", "accessing emotions", "restructuring interactions"]
                        },
                        {
                            "name": "Cognitive Behavioral Therapy",
                            "focus": "Thoughts, beliefs, behaviors",
                            "techniques": ["identifying patterns", "challenging beliefs", "behavior change"]
                        }
                    ]
                }),
                "type": "reference",
                "tags": ["therapy", "approaches", "techniques"]
            },
            {
                "id": "communication_exercises",
                "title": "Communication Exercises",
                "content": json.dumps({
                    "exercises": [
                        {
                            "name": "Speaker-Listener Technique",
                            "description": "One person speaks while the other listens, then switch roles",
                            "steps": [
                                "Speaker holds an object to indicate their turn",
                                "Listener focuses only on understanding, not responding",
                                "Listener summarizes what they heard before responding",
                                "Switch roles regularly"
                            ]
                        },
                        {
                            "name": "Daily Check-ins",
                            "description": "Brief daily conversations to maintain connection",
                            "steps": [
                                "Set aside 15-20 minutes each day",
                                "Share highlights, lowlights, and needs",
                                "Practice active listening without problem-solving",
                                "Express appreciation for each other"
                            ]
                        }
                    ]
                }),
                "type": "guidance",
                "tags": ["exercises", "communication", "practice"]
            }
        ]
        
        # Save initial documents
        for document in initial_documents:
            file_path = self.storage_path / f"{document['id']}.json"
            try:
                with open(file_path, 'w') as f:
                    json.dump(document, f, indent=2)
                self.documents.append(document)
            except Exception as e:
                logger.warning(f"Failed to create initial document {document['id']}: {e}")
        
        logger.info(f"Created {len(initial_documents)} initial documents in knowledge base")
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Basic search function using keyword matching
        """
        if not query or not self.documents:
            return []
        
        # Simple keyword search
        query_terms = query.lower().split()
        results = []
        
        for document in self.documents:
            # Search in title, content, and tags
            title = document.get('title', '').lower()
            content = document.get('content', '').lower()
            tags = [tag.lower() for tag in document.get('tags', [])]
            
            # Calculate a simple relevance score
            score = 0
            for term in query_terms:
                # Title matches are more important
                if term in title:
                    score += 3
                # Content matches
                if term in content:
                    score += 1
                # Tag matches are also important
                if term in tags or any(term in tag for tag in tags):
                    score += 2
            
            if score > 0:
                results.append({
                    'document': document,
                    'score': score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N results
        return [result['document'] for result in results[:limit]]
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by ID
        """
        for document in self.documents:
            if document.get('id') == document_id:
                return document
        return None


def create_minimal_analysis_result(user_id: str, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a minimal analysis result from conversations
    """
    # Initialize analyzers
    analyzer = MinimalConversationAnalyzer()
    
    # Extract all text
    all_text = " ".join([conv.get('text', '') for conv in conversations])
    
    # Perform basic sentiment analysis
    sentiment = analyzer.analyze_basic_sentiment(all_text)
    
    # Detect patterns
    red_flags = analyzer.detect_red_flags(conversations)
    positive_indicators = analyzer.detect_positive_indicators(conversations)
    communication_style = analyzer.analyze_communication_style(conversations)
    
    # Calculate overall score
    overall_score = 0.5  # Start at neutral
    
    # Adjust based on sentiment
    overall_score += sentiment['compound'] * 0.2
    
    # Adjust based on red flags and positive indicators
    overall_score -= len(red_flags) * 0.05
    overall_score += len(positive_indicators) * 0.05
    
    # Ensure score is between 0 and 1
    overall_score = max(0.0, min(1.0, overall_score))
    
    # Create analysis result
    result = {
        'user_id': user_id,
        'analysis_type': 'comprehensive',
        'overall_score': overall_score,
        'emotional_analysis': {
            'sentiment': sentiment['sentiment_label'],
            'sentiment_scores': {
                'positive': sentiment['positive'],
                'negative': sentiment['negative'],
                'neutral': sentiment['neutral'],
                'compound': sentiment['compound']
            }
        },
        'communication_patterns': {
            'style': communication_style['style'],
            'metrics': {
                'question_ratio': communication_style['question_ratio'],
                'exclamation_ratio': communication_style['exclamation_ratio'],
                'avg_message_length': communication_style['avg_message_length']
            }
        },
        'relationship_insights': {
            'health_level': _get_health_level(overall_score),
            'primary_interaction_mode': _get_interaction_mode(sentiment, red_flags, positive_indicators)
        },
        'red_flags': red_flags,
        'positive_indicators': positive_indicators,
        'recommendations': _generate_basic_recommendations(sentiment, red_flags, positive_indicators),
        'confidence_score': 0.7,
        'timestamp': datetime.now()
    }
    
    return result

def _get_health_level(score: float) -> str:
    """Get relationship health level from score"""
    if score >= 0.8:
        return "very healthy"
    elif score >= 0.6:
        return "healthy"
    elif score >= 0.4:
        return "moderately healthy"
    elif score >= 0.2:
        return "needs attention"
    else:
        return "concerning"

def _get_interaction_mode(sentiment: Dict[str, Any], red_flags: List[str], positive_indicators: List[str]) -> str:
    """Determine primary interaction mode"""
    # Calculate positivity ratio
    if isinstance(sentiment, dict) and sentiment.get('compound', 0) > 0.5 and len(positive_indicators) > len(red_flags):
        return "supportive"
    elif isinstance(sentiment, dict) and sentiment.get('compound', 0) < -0.3 and len(red_flags) > 0:
        return "conflictual"
    elif len(red_flags) > 0 and any("controlling" in flag.lower() for flag in red_flags):
        return "controlling"
    elif isinstance(sentiment, dict) and sentiment.get('compound', 0) > 0 and sentiment.get('compound', 0) < 0.5:
        return "cooperative"
    else:
        return "neutral"

def _generate_basic_recommendations(sentiment: Dict[str, Any], red_flags: List[str], positive_indicators: List[str]) -> List[str]:
    """Generate basic recommendations based on analysis"""
    recommendations = []
    
    # Communication recommendations
    recommendations.append("Practice active listening by paraphrasing what your partner says before responding")
    
    # Add sentiment-based recommendations
    if sentiment['sentiment_label'] == 'negative':
        recommendations.append("Try to use more positive language and express appreciation regularly")
    
    # Add red flag recommendations
    if len(red_flags) > 0:
        if any("controlling" in flag.lower() for flag in red_flags):
            recommendations.append("Work on respecting boundaries and individual autonomy")
        if any("jealous" in flag.lower() for flag in red_flags):
            recommendations.append("Build trust through transparency and consistent behavior")
    
    # Add positive reinforcement
    if len(positive_indicators) > 0:
        recommendations.append("Continue building on strengths like " + 
                             (positive_indicators[0].split(":")[0].lower() if ":" in positive_indicators[0] else positive_indicators[0].lower()))
    
    # General recommendation
    recommendations.append("Schedule regular check-ins to discuss relationship needs and concerns")
    
    return recommendations

if __name__ == "__main__":
    # Test code for minimal implementations
    logging.basicConfig(level=logging.INFO)
    
    # Sample conversation
    sample_conversation = [
        {"speaker": "Person A", "text": "I really appreciate how you've been helping with the chores lately."},
        {"speaker": "Person B", "text": "Thanks! I'm trying to be better about that."},
        {"speaker": "Person A", "text": "It makes me feel like we're a team."},
        {"speaker": "Person B", "text": "I feel the same way. Though I was wondering if we could talk about our budget soon?"},
        {"speaker": "Person A", "text": "Sure, I've been meaning to bring that up too."}
    ]
    
    # Test analyzers
    analyzer = MinimalConversationAnalyzer()
    sentiment = analyzer.analyze_basic_sentiment(" ".join([c["text"] for c in sample_conversation]))
    print(f"Sentiment: {sentiment}")
    
    red_flags = analyzer.detect_red_flags(sample_conversation)
    print(f"Red flags: {red_flags}")
    
    positive_indicators = analyzer.detect_positive_indicators(sample_conversation)
    print(f"Positive indicators: {positive_indicators}")
    
    # Test topics detection
    topics = analyzer.detect_topics(sample_conversation)
    print(f"Detected topics: {topics}")
    
    # Test therapist
    therapist = MinimalAITherapist()
    recommendations = therapist.generate_recommendations({
        "sentiment": sentiment,
        "red_flags": red_flags,
        "positive_indicators": positive_indicators,
        "text": " ".join([c["text"] for c in sample_conversation])
    })
    print(f"Recommendations: {recommendations}")
    
    # Test knowledge base
    kb = MinimalKnowledgeBase()
    results = kb.search("communication patterns")
    print(f"Knowledge base search results: {len(results)} documents found")
    
    # Test full analysis
    result = create_minimal_analysis_result("test_user", sample_conversation)
    print(f"Analysis result: {result['overall_score']:.2f} - {result['relationship_insights']['health_level']}")