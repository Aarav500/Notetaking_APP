import React, { useState } from 'react';
import { forgot, resetPassword } from '../api/client';

export default function Forgot() {
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onForgot = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      const res = await forgot(email);
      setMsg(res.message + (res.token ? ` Token: ${res.token}` : ''));
      if (res.token) setToken(res.token);
    } catch (err: any) {
      setMsg(err?.response?.data?.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const onReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      const res = await resetPassword(token, newPassword);
      setMsg(res.message);
    } catch (err: any) {
      setMsg(err?.response?.data?.message || 'Reset failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, display: 'grid', gap: 24 }}>
      <div>
        <h2>Forgot Password</h2>
        <form onSubmit={onForgot} style={{ display: 'grid', gap: 8, maxWidth: 420 }}>
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
          <button disabled={loading} type="submit">{loading ? '...' : 'Request reset token'}</button>
        </form>
      </div>
      <div>
        <h2>Reset Password</h2>
        <form onSubmit={onReset} style={{ display: 'grid', gap: 8, maxWidth: 420 }}>
          <input placeholder="Token" value={token} onChange={e => setToken(e.target.value)} />
          <input type="password" placeholder="New password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
          <button disabled={loading} type="submit">{loading ? '...' : 'Reset password'}</button>
        </form>
      </div>
      {msg && <div style={{ color: '#333' }}>{msg}</div>}
    </div>
  );
}
