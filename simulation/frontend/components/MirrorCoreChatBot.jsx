import React, { useState, useEffect, useRef } from 'react';
import '../assets/styles/mirrorcore.css';

const MirrorCoreChatBot = ({ userId, sessionId, onSessionChange }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch session data on component mount or when sessionId changes
  useEffect(() => {
    if (sessionId) {
      fetchSession(sessionId);
      fetchMessages(sessionId);
    }
  }, [sessionId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSession = async (sid) => {
    try {
      const response = await fetch(`/mirrorcore/session/${sid}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentSession(data);
      }
    } catch (error) {
      console.error('Error fetching session:', error);
    }
  };

  const fetchMessages = async (sid) => {
    // In a real implementation, this would fetch messages from the backend
    // For now, we'll simulate with empty messages array
    setMessages([]);
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    // Add user message to chat
    const userMessage = {
      text: inputText,
      sender: 'client',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      // Send message to backend
      const response = await fetch('/mirrorcore/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage,
          user_id: userId,
          session_id: sessionId || null
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add bot response to chat
        const botMessage = {
          text: data.message,
          sender: 'diego',
          timestamp: new Date().toISOString(),
          fmt_id: data.fmt_id,
          fmt_name: data.fmt_name,
          stage: data.stage,
          tone: data.tone
        };

        setMessages(prev => [...prev, botMessage]);
        
        // If this is a new session, update the sessionId
        if (!sessionId) {
          onSessionChange && onSessionChange(data.session_id);
        }

        // Update session data
        fetchSession(sessionId || data.session_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [...prev, {
        text: 'Sorry, there was an error processing your message. Please try again.',
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="mirrorcore-chat-container">
      {/* Chat header */}
      <div className="mirrorcore-chat-header">
        <div className="mirrorcore-chat-title">
          <h2>Diego Camilleri</h2>
          {currentSession && (
            <div className="mirrorcore-stage-badge">
              {currentSession.stage}
            </div>
          )}
        </div>
        {currentSession && currentSession.scores && (
          <div className="mirrorcore-scores">
            <div className="mirrorcore-score">
              <span>Trust:</span>
              <div className="mirrorcore-score-bar">
                <div 
                  className="mirrorcore-score-fill" 
                  style={{ width: `${Math.min(100, Math.max(0, currentSession.scores.trust))}%` }}
                ></div>
              </div>
            </div>
            <div className="mirrorcore-score">
              <span>Openness:</span>
              <div className="mirrorcore-score-bar">
                <div 
                  className="mirrorcore-score-fill" 
                  style={{ width: `${Math.min(100, Math.max(0, currentSession.scores.open))}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Messages area */}
      <div className="mirrorcore-messages-container">
        {messages.length === 0 ? (
          <div className="mirrorcore-empty-chat">
            <p>Start a conversation with Diego</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={index} 
              className={`mirrorcore-message ${msg.sender === 'client' ? 'mirrorcore-user-message' : 'mirrorcore-bot-message'}`}
            >
              <div className="mirrorcore-message-content">
                <p>{msg.text}</p>
                <div className="mirrorcore-message-meta">
                  <span className="mirrorcore-message-time">{formatTimestamp(msg.timestamp)}</span>
                  {msg.fmt_name && (
                    <span className="mirrorcore-message-fmt">{msg.fmt_name}</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="mirrorcore-message mirrorcore-bot-message">
            <div className="mirrorcore-message-content">
              <div className="mirrorcore-typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="mirrorcore-input-container">
        <textarea
          className="mirrorcore-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows={1}
        />
        <button 
          className="mirrorcore-send-button" 
          onClick={handleSendMessage}
          disabled={loading || !inputText.trim()}
        >
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default MirrorCoreChatBot;