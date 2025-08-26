import { useState, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import ReCAPTCHA from 'react-google-recaptcha';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import useSettingsStore from '@/store/useSettingsStore';
import api from '@/lib/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const login = useSettingsStore((state) => state.login);
  const recaptchaRef = useRef(null);
  
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [captchaValue, setCaptchaValue] = useState(null);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/';
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    
    if (!password) {
      setError('Password is required');
      return;
    }
    
    if (!captchaValue) {
      setError('Please complete the reCAPTCHA verification');
      return;
    }
    
    // Clear previous errors
    setError('');
    setIsLoading(true);
    
    try {
      // Call the API to login
      const response = await api.auth.login({ 
        email, 
        password, 
        rememberMe,
        recaptchaToken: captchaValue 
      });
      
      // Update the auth state in the store
      login(response.data.user);
      
      // Show success message
      toast({
        title: 'Login Successful',
        description: 'Welcome back!',
      });
      
      // Redirect to the previous page or dashboard
      navigate(from, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 401:
            setError('Invalid email or password');
            break;
          case 403:
            setError('Your account has been locked. Please contact support.');
            break;
          case 400:
            if (err.response.data.message === 'Invalid reCAPTCHA') {
              setError('reCAPTCHA verification failed. Please try again.');
              // Reset reCAPTCHA
              recaptchaRef.current.reset();
              setCaptchaValue(null);
            } else {
              setError('An error occurred during login. Please try again.');
            }
            break;
          default:
            setError('An error occurred during login. Please try again.');
        }
      } else {
        setError('Unable to connect to the server. Please check your internet connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCaptchaChange = (value) => {
    setCaptchaValue(value);
  };
  
  // For demo purposes, provide a quick login option
  const handleDemoLogin = async () => {
    setEmail('demo@example.com');
    setPassword('password123');
    
    // Set a mock captcha value for demo login
    const mockCaptchaValue = 'demo-captcha-token';
    setCaptchaValue(mockCaptchaValue);
    
    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(async () => {
      try {
        // Call the API to login with demo credentials
        const response = await api.auth.login({ 
          email: 'demo@example.com', 
          password: 'password123',
          rememberMe: false,
          recaptchaToken: mockCaptchaValue
        });
        
        // Update the auth state in the store
        login(response.data.user);
        
        // Show success message
        toast({
          title: 'Demo Login Successful',
          description: 'You are now logged in with demo credentials',
        });
        
        // Redirect to the dashboard
        navigate('/', { replace: true });
      } catch (err) {
        console.error('Demo login error:', err);
        setError('Failed to login with demo account. Please try again.');
        
        // Reset captcha
        if (recaptchaRef.current) {
          recaptchaRef.current.reset();
        }
        setCaptchaValue(null);
      } finally {
        setIsLoading(false);
      }
    }, 1000);
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md"
      >
        <div className="bg-card rounded-lg border border-border shadow-sm p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold">Welcome Back</h1>
            <p className="text-muted-foreground mt-2">
              Sign in to your account to continue
            </p>
          </div>
          
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-destructive/10 text-destructive rounded-md p-3 mb-6 flex items-start"
            >
              <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </motion.div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                disabled={isLoading}
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Link
                  to="/auth/forgot-password"
                  className="text-sm text-primary hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
            
            <div className="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-input"
                disabled={isLoading}
              />
              <label htmlFor="remember-me" className="ml-2 text-sm">
                Remember me
              </label>
            </div>
            
            <div className="flex justify-center my-4">
              <ReCAPTCHA
                ref={recaptchaRef}
                sitekey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI" // This is a test key
                onChange={handleCaptchaChange}
                theme="light"
                size="normal"
              />
            </div>
            
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || !captchaValue}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                <span className="flex items-center">
                  <LogIn className="mr-2 h-4 w-4" />
                  Sign In
                </span>
              )}
            </Button>
            
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border"></div>
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-card px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>
            
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={handleDemoLogin}
              disabled={isLoading}
            >
              Demo Account
            </Button>
          </form>
          
          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Don't have an account?</span>{' '}
            <Link to="/auth/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}