import axios from 'axios';

export const API_BASE = (import.meta as any).env?.VITE_API_URL || (window as any).VITE_API_URL || 'http://localhost:3000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export type AuthResponse = {
  user: { id: number; email: string; name?: string };
  token: string;
};

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/login', { email, password });
  return data;
}

export async function register(email: string, password: string, name?: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/register', { email, password, name });
  return data;
}

export async function forgot(email: string): Promise<{ message: string; token?: string }> {
  const { data } = await api.post('/auth/forgot', { email });
  return data;
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  const { data } = await api.post('/auth/reset', { token, newPassword });
  return data;
}

export async function me(token: string): Promise<{ user: { id: number; email: string; name?: string } }> {
  const { data } = await api.get('/auth/me', { headers: { Authorization: `Bearer ${token}` } });
  return data;
}
