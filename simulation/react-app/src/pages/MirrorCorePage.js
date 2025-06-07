import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { MirrorCoreApp } from '../components/mirrorcore';
import '../assets/styles/mirrorcore-page.css';

const MirrorCorePage = () => {
  const { currentUser, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="mirrorcore-page-container">
      <div className="mirrorcore-page-header">
        <h1>MirrorCore</h1>
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
        {/* Pass the current user ID to the MirrorCoreApp component */}
        <MirrorCoreApp userId={currentUser?.id} />
      </div>

      <div className="mirrorcore-page-footer">
        <p>MirrorCore Dynamic Stage Orchestration System</p>
      </div>
    </div>
  );
};

export default MirrorCorePage;