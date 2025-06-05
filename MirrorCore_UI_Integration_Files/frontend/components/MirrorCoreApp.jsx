import React, { useState } from 'react';
import MirrorCoreChatBot from './MirrorCoreChatBot';
import SessionDashboard from './SessionDashboard';
import '../assets/styles/mirrorcore.css';

const MirrorCoreApp = () => {
  const [currentUserId, setCurrentUserId] = useState('user123'); // In a real app, this would come from authentication
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
        <h1>MirrorCore</h1>
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
          <MirrorCoreChatBot 
            userId={currentUserId}
            sessionId={currentSessionId}
            onSessionChange={setCurrentSessionId}
          />
        )}
      </main>

      <footer className="mirrorcore-app-footer">
        <p>MirrorCore Dynamic Stage Orchestration System</p>
      </footer>
    </div>
  );
};

export default MirrorCoreApp;