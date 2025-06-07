import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CoreEngineApp } from '../components/mirrorcore';
import '../assets/styles/core_engine-page.css';

const CoreEnginePage = () => {
  const { currentUser, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="mirrorcore-page-container">
        <div className="mirrorcore-page-header">
          <h1>Core Engine</h1>
        <div className="user-controls">
          <span className="user-info">
            User: {currentUser?.name || currentUser?.id}
          </span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>

      <div className="mirrorcore-app-wrapper">
          {/* Pass the current user ID to the CoreEngineApp component */}
          <CoreEngineApp userId={currentUser?.id} />
      </div>

      <div className="mirrorcore-page-footer">
        <p>Core Engine Dynamic Stage Orchestration System</p>
      </div>
    </div>
  );
};

export default CoreEnginePage;