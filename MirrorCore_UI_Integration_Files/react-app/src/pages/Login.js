import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../assets/styles/login.css';

const Login = () => {
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get the redirect path or default to /mirrorcore
  const from = location.state?.from?.pathname || '/mirrorcore';

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!userId.trim()) {
      return setError('Please enter a user ID');
    }

    try {
      setError('');
      setLoading(true);

      // In a real app, this would validate with a backend
      // For now, we'll just use the user ID as is
      const success = login({ id: userId, name: `User ${userId}` });

      if (success) {
        navigate(from, { replace: true });
      }
    } catch (error) {
      setError('Failed to log in');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>MirrorCore</h1>
        <h2>Dynamic Stage Orchestration System</h2>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="userId">User ID</label>
            <input
              type="text"
              id="userId"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter your user ID"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="login-info">
          For demo purposes, you can enter any user ID.
        </p>
      </div>
    </div>
  );
};

export default Login;