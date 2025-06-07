import React, { useState } from 'react';
import CoreEngineChatBot from './CoreEngineChatBot';
import SessionDashboard from './SessionDashboard';

const CoreEngineApp = ({ userId }) => {
  const [currentUserId, setCurrentUserId] = useState(userId || 'user123'); // Use provided userId or default
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [view, setView] = useState('dashboard'); // 'dashboard' or 'chat'

  const handleSelectSession = (sessionId) => {
    setCurrentSessionId(sessionId);
    setView('chat');
  };

  const handleBackToDashboard = () => {
    setView('dashboard');
  };

  return (
    <div className="mirrorcore-app-container">
        <header className="mirrorcore-app-header">
          <h1>Core Engine</h1>
        {view === 'chat' && (
          <button 
            className="mirrorcore-back-button"
            onClick={handleBackToDashboard}
          >
            ← Back to Dashboard
          </button>
        )}
      </header>

      <main className="mirrorcore-app-content">
        {view === 'dashboard' ? (
          <SessionDashboard 
            userId={currentUserId} 
            onSelectSession={handleSelectSession} 
          />
        ) : (
          <CoreEngineChatBot 
            userId={currentUserId}
            sessionId={currentSessionId}
            onSessionChange={setCurrentSessionId}
          />
        )}
      </main>

      <footer className="mirrorcore-app-footer">
        <p>Core Engine Dynamic Stage Orchestration System</p>
      </footer>
    </div>
  );
};

export default CoreEngineApp;