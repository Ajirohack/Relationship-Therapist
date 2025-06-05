#!/usr/bin/env python3
"""
Simple Flask Server for Relationship Therapist Testing UI
"""

from flask import Flask, request, jsonify, send_from_directory
from minimal_implementations import MinimalConversationAnalyzer, MinimalAITherapist
import logging
import re
import os
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize minimal implementations
analyzer = MinimalConversationAnalyzer()
therapist = MinimalAITherapist()

@app.route('/')
def index():
    return send_from_directory('.', 'test_ui_fixed.html')

@app.route('/api/v1/analyze/conversation', methods=['POST'])
def analyze_conversation():
    """
    Analyze conversation using minimal implementations
    """
    try:
        data = request.json
        conversation_text = data.get('conversation', '')
        
        # Parse the conversation into messages
        messages = parse_conversation(conversation_text)
        
        # Analyze sentiment
        sentiment = analyzer.analyze_basic_sentiment(conversation_text)
        
        # Analyze communication style
        comm_style = analyzer.analyze_communication_style(messages)
        
        # Detect topics
        topics_result = analyzer.detect_topics(messages)
        topics = list(set([t.lower() for t in topics_result]))
        
        # Check for red flags
        red_flags = analyzer.detect_red_flags(messages)
        
        # Generate recommendations
        recommendations_data = {
            "sentiment": sentiment,
            "text": conversation_text,
            "topics": topics_result,
            "conflict_patterns": analyzer.detect_conflict_patterns(messages)
        }
        recommendations = therapist.generate_recommendations(recommendations_data)
        
        # Format the response
        response = {
            "sentiment": {
                "sentiment": sentiment.get("sentiment_label", "neutral"),
                "score": sentiment.get("compound", 0.5),
                "details": {
                    "positive_score": sentiment.get("positive", 0),
                    "negative_score": sentiment.get("negative", 0),
                    "neutral_score": sentiment.get("neutral", 0)
                }
            },
            "communication_style": {
                "style": comm_style.get("style", "balanced"),
                "question_ratio": comm_style.get("question_ratio", 0),
                "exclamation_ratio": comm_style.get("exclamation_ratio", 0)
            },
            "topics": topics,
            "recommendations": recommendations if isinstance(recommendations, list) else ["Continue building your positive communication patterns."],
            "red_flags": red_flags
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error analyzing conversation: {str(e)}")
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

def parse_conversation(text):
    """
    Parse a text conversation into a list of messages
    """
    lines = text.split('\n')
    messages = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to extract sender and message
        match = re.match(r'^([^:]+):\s*(.+)$', line)
        if match:
            sender, content = match.groups()
            messages.append({
                "text": content.strip(),
                "sender": sender.strip()
            })
        else:
            # If no clear sender, assign to previous sender or "Unknown"
            sender = messages[-1]["sender"] if messages else "Unknown"
            messages.append({
                "text": line,
                "sender": sender
            })
    
    return messages

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start the Relationship Therapist Test UI Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    args = parser.parse_args()
    
    logger.info(f"Starting Relationship Therapist Test UI server on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port, debug=True)
