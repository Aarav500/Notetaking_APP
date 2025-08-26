import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import { ThemeProvider } from '@/components/theme-provider';
import { useEffect } from 'react';
import useSettingsStore from '@/store/useSettingsStore';

// Layouts
import MainLayout from '@/components/layouts/MainLayout';

// Pages
import Dashboard from '@/pages/Dashboard';
import Notes from '@/pages/Notes';
import NotePage from '@/pages/NotePage';
import ReadingView from '@/pages/ReadingView';
import ProcessInput from '@/pages/ProcessInput';
import Visualizations from '@/pages/Visualizations';
import Search from '@/pages/Search';
import Settings from '@/pages/Settings';
import NotFound from '@/pages/NotFound';

// Auth Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useSettingsStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/auth/login" replace />;
  }
  
  return children;
};

function App() {
  // Initialize theme from settings store
  const setTheme = useSettingsStore((state) => state.setTheme);
  const theme = useSettingsStore((state) => state.settings.theme);
  
  useEffect(() => {
    // Apply theme from settings store
    setTheme(theme);
  }, [setTheme, theme]);
  
  return (
    <ThemeProvider defaultTheme="system" storageKey="pansophy-theme">
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth">
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
          <Route path="reset-password" element={<ResetPasswordPage />} />
        </Route>
        
        {/* Protected App Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="notes" element={<Notes />} />
          <Route path="notes/:id" element={<NotePage />} />
          <Route path="reading/:id" element={<ReadingView />} />
          <Route path="process" element={<ProcessInput />} />
          <Route path="visualizations" element={<Visualizations />} />
          <Route path="search" element={<Search />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
      <Toaster />
    </ThemeProvider>
  );
}

export default App;