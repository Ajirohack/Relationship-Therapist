import React, { useState, useEffect } from 'react';

const SessionDashboard = ({ userId, onSelectSession }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (userId) {
      fetchUserSessions(userId);
    }
  }, [userId]);

  const fetchUserSessions = async (uid) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/core-engine/user/${uid}/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      } else {
        setError('Failed to fetch sessions');
      }
    } catch (error) {
      console.error('Error fetching user sessions:', error);
      setError('An error occurred while fetching sessions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNewSession = async () => {
    // In a real implementation, this would create a new session
    // For now, we'll just select null to indicate a new session should be created
    onSelectSession(null);
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown date';
    
    const date = new Date(timestamp);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStageColor = (stage) => {
    switch (stage) {
      case 'APP':
        return 'mirrorcore-stage-app';
      case 'FPP':
        return 'mirrorcore-stage-fpp';
      case 'RPP':
        return 'mirrorcore-stage-rpp';
      default:
        return '';
    }
  };

  if (loading) {
    return (
      <div className="mirrorcore-dashboard-container mirrorcore-loading">
        <div className="mirrorcore-loading-spinner"></div>
        <p>Loading sessions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mirrorcore-dashboard-container mirrorcore-error">
        <p>{error}</p>
        <button 
          className="mirrorcore-button" 
          onClick={() => fetchUserSessions(userId)}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="mirrorcore-dashboard-container">
      <div className="mirrorcore-dashboard-header">
        <h2>Your Conversations with Diego</h2>
        <button 
          className="mirrorcore-button mirrorcore-primary-button" 
          onClick={handleCreateNewSession}
        >
          Start New Conversation
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="mirrorcore-empty-sessions">
          <p>You don't have any conversations with Diego yet.</p>
          <p>Start your first conversation to begin building your relationship.</p>
        </div>
      ) : (
        <div className="mirrorcore-sessions-list">
          {sessions.map((session) => (
            <div 
              key={session.session_id} 
              className="mirrorcore-session-card"
              onClick={() => onSelectSession(session.session_id)}
            >
              <div className="mirrorcore-session-header">
                <span className={`mirrorcore-stage-indicator ${getStageColor(session.stage)}`}>
                  {session.stage}
                </span>
                <span className="mirrorcore-session-date">
                  {formatDate(session.last_updated)}
                </span>
              </div>
              
              <div className="mirrorcore-session-scores">
                <div className="mirrorcore-session-score">
                  <span>Trust:</span>
                  <div className="mirrorcore-score-bar">
                    <div 
                      className="mirrorcore-score-fill" 
                      style={{ width: `${Math.min(100, Math.max(0, session.scores.trust))}%` }}
                    ></div>
                  </div>
                </div>
                <div className="mirrorcore-session-score">
                  <span>Openness:</span>
                  <div className="mirrorcore-score-bar">
                    <div 
                      className="mirrorcore-score-fill" 
                      style={{ width: `${Math.min(100, Math.max(0, session.scores.open))}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              {session.flags && Object.keys(session.flags).length > 0 && (
                <div className="mirrorcore-session-flags">
                  {Object.entries(session.flags)
                    .filter(([_, value]) => value === true)
                    .map(([key]) => (
                      <span key={key} className="mirrorcore-flag">{key.replace(/_/g, ' ')}</span>
                    ))
                  }
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionDashboard;