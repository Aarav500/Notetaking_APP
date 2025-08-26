import React from 'react';
import { Link, Route, Routes, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Forgot from './pages/Forgot';
import Dashboard from './pages/Dashboard';

function Nav() {
  return (
    <nav style={{ display: 'flex', gap: 12, padding: 12, borderBottom: '1px solid #eee' }}>
      <Link to="/login">Login</Link>
      <Link to="/register">Register</Link>
      <Link to="/forgot">Forgot</Link>
      <Link to="/">Dashboard</Link>
    </nav>
  );
}

export default function App() {
  return (
    <div>
      <Nav />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot" element={<Forgot />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
