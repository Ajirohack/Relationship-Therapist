from datetime import datetime, timedelta
from collections import deque, Counter
import re, math
from typing import Dict, Any, List, Optional

try:
    from textblob import TextBlob
except ImportError:
    print("TextBlob not installed. Please install with: pip install textblob")
    print("Using fallback sentiment analysis.")
    
    class FallbackTextBlob:
        class Sentiment:
            def __init__(self, polarity=0.0, subjectivity=0.0):
                self.polarity = polarity
                self.subjectivity = subjectivity
                
        def __init__(self, text):
            self.text = text
            self.sentiment = self.Sentiment()
            
    TextBlob = FallbackTextBlob

# Key word sets for scoring
INTIMACY = {"feel", "heart", "love", "trust", "care", "miss", "hug"}
ATTACH = {"future", "together", "our", "we", "us", "forever"}


def _sentiment(txt: str) -> float:
    """Calculate sentiment score normalized to 0-1 range"""
    return (TextBlob(txt).sentiment.polarity + 1) / 2  # 0-1


def _question_ratio(txt: str) -> float:
    """Calculate the ratio of questions to total sentences"""
    sents = re.split(r'[.!?]+', txt)
    qs = sum(1 for s in sents if "?" in s)
    return qs / max(1, len(sents))


def _token_count(txt: str) -> int:
    """Count the number of tokens in text"""
    return len(re.findall(r'\w+', txt))


def _contains(words: set, txt: str) -> bool:
    """Check if any words from the set are in the text"""
    tokens = set(t.lower() for t in re.findall(r'\w+', txt))
    return len(words & tokens) > 0


def score_single(msg: Dict[str, Any], reply_latency_hrs: float) -> Dict[str, float]:
    """
    Score a single message for trust and openness
    
    Args:
        msg: Dictionary with message data including text and optional reciprocation score
        reply_latency_hrs: Hours between Diego message and CL reply
        
    Returns:
        Dictionary with trust and openness scores (0-100)
    """
    text = msg["text"].strip()
    length_score = min(1.0, _token_count(text) / 120)  # full credit ≥120 tokens
    sentiment = _sentiment(text)
    q_ratio = _question_ratio(text)
    pronouns = len(re.findall(r'\b(I|you)\b', text, re.I)) / max(1, _token_count(text))
    intimacy = 1.0 if _contains(INTIMACY, text) else 0.0
    attach = 1.0 if _contains(ATTACH, text) else 0.0
    politeness = 1.0 if re.search(r'\b(thanks?|appreciate|grateful)\b', text, re.I) or "❤️" in text else 0.0
    latency_norm = 1.0 - min(1.0, reply_latency_hrs / 48)  # ≤2 days → good

    # weight vectors
    trust = (
        0.10 * sentiment + 0.10 * length_score + 0.10 * latency_norm +
        0.05 * q_ratio + 0.05 * pronouns + 0.15 * intimacy +
        0.20 * msg.get("reciprocation", 0) + 0.15 * attach +
        0.10 * politeness
    )
    open_ = (
        0.15 * sentiment + 0.10 * length_score + 0.05 * latency_norm +
        0.10 * q_ratio + 0.10 * pronouns + 0.20 * intimacy +
        0.10 * msg.get("reciprocation", 0) + 0.10 * attach +
        0.10 * politeness
    )

    return {"trust": round(trust * 100, 2), "open": round(open_ * 100, 2)}


class RollingScorer:
    """Maintains a moving window of last N CL messages"""
    
    def __init__(self, window=10):
        self.window = window
        self.buffer = deque(maxlen=window)

    def add(self, score: Dict[str, float]):
        """Add a new score to the buffer"""
        self.buffer.append(score)

    @property
    def aggregate(self) -> Dict[str, float]:
        """Calculate aggregate scores from the buffer"""
        if not self.buffer:
            return {"trust": 0.0, "open": 0.0}
        trust = sum(s["trust"] for s in self.buffer) / len(self.buffer)
        open_ = sum(s["open"] for s in self.buffer) / len(self.buffer)
        return {"trust": round(trust, 1), "open": round(open_, 1)}


def score_interaction(cl_msg: str,
                      diego_prev: str,
                      latency_hours: float,
                      history: RollingScorer) -> Dict[str, float]:
    """
    High-level helper called by MirrorCore to score an interaction
    
    Args:
        cl_msg: The client's message text
        diego_prev: Diego's previous message text
        latency_hours: Hours between Diego's message and client's reply
        history: RollingScorer instance to maintain history
        
    Returns:
        Dictionary with aggregate trust and openness scores
    """
    # Check if client's message contains words from Diego's message (reciprocation)
    reciprocation = 1.0 if any(
        w.lower() in cl_msg.lower() for w in diego_prev.split()[:15]) else 0.0

    single = score_single(
        {"role": "cl", "text": cl_msg, "reciprocation": reciprocation},
        latency_hours
    )
    history.add(single)
    return history.aggregate