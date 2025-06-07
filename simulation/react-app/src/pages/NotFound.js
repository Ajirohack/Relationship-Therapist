import React from 'react';
import { Link } from 'react-router-dom';
import '../assets/styles/not-found.css';

const NotFound = () => {
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for doesn't exist or has been moved.</p>
        <Link to="/" className="not-found-button">Go to Home</Link>
      </div>
    </div>
  );
};

export default NotFound;