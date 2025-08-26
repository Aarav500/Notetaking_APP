import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register as registerApi } from '../api/client';

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await registerApi(email, password, name);
      localStorage.setItem('token', res.token);
      navigate('/');
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Register failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Register</h2>
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 8, maxWidth: 360 }}>
        <input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button disabled={loading} type="submit">{loading ? '...' : 'Create account'}</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </form>
    </div>
  );
}
