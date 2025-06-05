import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthProvider from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { Login, MirrorCorePage, NotFound } from './pages';
import './assets/styles/mirrorcore.css'; // Import the MirrorCore CSS

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/mirrorcore/*"
            element={
              <ProtectedRoute>
                <MirrorCorePage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/mirrorcore" replace />} />
          {/* 404 route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;