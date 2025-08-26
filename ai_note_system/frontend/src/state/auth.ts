import axios from 'axios';
import { create } from 'zustand';

export type User = { id: number; email: string; name?: string | null };

const API_BASE = (import.meta as any)?.env?.VITE_API_URL || 'http://localhost:3000/api';

export const api = axios.create({ baseURL: API_BASE });

export interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  me: () => Promise<void>;
}

export const useAuth = create<AuthState>((set, get) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  user: null,
  setAuth: (token, user) => {
    if (typeof window !== 'undefined') localStorage.setItem('token', token);
    set({ token, user });
  },
  logout: () => {
    if (typeof window !== 'undefined') localStorage.removeItem('token');
    set({ token: null, user: null });
  },
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    const { token, user } = res.data;
    get().setAuth(token, user);
  },
  register: async (email: string, password: string, name?: string) => {
    const res = await api.post('/auth/register', { email, password, name });
    const { token, user } = res.data;
    get().setAuth(token, user);
  },
  me: async () => {
    const token = get().token;
    if (!token) return;
    const res = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    set({ user: res.data.user });
  },
}));

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = useAuth.getState().token;
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});
