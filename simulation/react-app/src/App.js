import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthProvider from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { Login, CoreEnginePage, NotFound } from './pages';
import './assets/styles/core_engine.css'; // Import the Core Engine CSS

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/core-engine/*"
          element={
            <ProtectedRoute>
              <CoreEnginePage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/core-engine" replace />} />
          {/* 404 route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;