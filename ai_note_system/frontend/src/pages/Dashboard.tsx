import React, { useEffect, useState } from 'react';
import { me } from '../api/client';
import { Link } from 'react-router-dom';

type User = { id: number; email: string; name?: string };

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    me(token)
      .then((res) => setUser(res.user))
      .catch((err) => setError(err?.response?.data?.message || 'Failed to fetch profile'));
  }, []);

  if (!localStorage.getItem('token')) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Welcome to AI Notes</h2>
        <p>Please <Link to="/login">Login</Link> or <Link to="/register">Register</Link> to continue.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Dashboard</h2>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {user ? (
        <div>
          <p>Hello, {user.name || user.email}!</p>
          <p>This is a minimal placeholder dashboard.</p>
        </div>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
