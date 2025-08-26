import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Eye, EyeOff, AlertCircle, CheckCircle, Lock, ArrowLeft, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  
  // Get parameters from URL query parameters
  const queryParams = new URLSearchParams(location.search);
  const token = queryParams.get('token');
  const method = queryParams.get('method') || 'email';
  const phone = queryParams.get('phone');
  
  // Form state
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otp, setOtp] = useState('');
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [tokenError, setTokenError] = useState('');
  
  // Success state
  const [isSuccess, setIsSuccess] = useState(false);
  
  // Password strength
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  // Validate token or method on mount
  useEffect(() => {
    if (method === 'email' && !token) {
      setTokenError('Invalid or missing reset token. Please request a new password reset link.');
      return;
    }
    
    if (method === 'otp' && !phone) {
      setTokenError('Invalid or missing phone number. Please request a new OTP.');
      return;
    }
    
    // In a real app, you might want to validate the token with the server
    // For now, we'll just check if it exists
  }, [token, method, phone]);
  
  // Check password strength
  const checkPasswordStrength = (password) => {
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength += 1;
    
    // Contains lowercase
    if (/[a-z]/.test(password)) strength += 1;
    
    // Contains uppercase
    if (/[A-Z]/.test(password)) strength += 1;
    
    // Contains number
    if (/[0-9]/.test(password)) strength += 1;
    
    // Contains special character
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    setPasswordStrength(strength);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!password) {
      setError('Password is required');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    if (passwordStrength < 3) {
      setError('Password is too weak');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    // Validate OTP if using OTP method
    if (method === 'otp' && !otp.trim()) {
      setError('OTP is required');
      return;
    }
    
    // Clear previous errors
    setError('');
    setIsLoading(true);
    
    try {
      // Call the API to reset password based on method
      if (method === 'email') {
        await api.auth.resetPassword({ token, password, method: 'email' });
      } else if (method === 'otp') {
        await api.auth.resetPassword({ 
          phoneNumber: phone, 
          otp, 
          password,
          method: 'otp' 
        });
      }
      
      // Show success message
      setIsSuccess(true);
      
      toast({
        title: 'Password Reset Successful',
        description: 'Your password has been reset successfully',
      });
      
      // Redirect to login after a delay
      setTimeout(() => {
        navigate('/auth/login', { 
          replace: true,
          state: { message: 'Your password has been reset. Please log in with your new password.' }
        });
      }, 3000);
    } catch (err) {
      console.error('Password reset error:', err);
      
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 400:
            if (method === 'otp' && err.response.data?.message?.includes('OTP')) {
              setError('Invalid OTP. Please check and try again or request a new OTP.');
            } else {
              setError('Invalid password. Please try again with a stronger password.');
            }
            break;
          case 401:
            if (method === 'email') {
              setError('Invalid or expired token. Please request a new password reset link.');
            } else {
              setError('Invalid or expired OTP. Please request a new OTP.');
            }
            break;
          default:
            setError('An error occurred. Please try again later.');
        }
      } else {
        setError('Unable to connect to the server. Please check your internet connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  // If token is invalid, show error message
  if (tokenError) {
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
              <h1 className="text-3xl font-bold">Reset Password</h1>
              <p className="text-muted-foreground mt-2">
                There was a problem with your reset link
              </p>
            </div>
            
            <div className="bg-destructive/10 text-destructive rounded-md p-4 mb-6 flex items-start">
              <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
              <span>{tokenError}</span>
            </div>
            
            <div className="flex justify-center">
              <Button asChild>
                <Link to="/auth/forgot-password">
                  Request New Reset Link
                </Link>
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }
  
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
            <h1 className="text-3xl font-bold">Reset Password</h1>
            <p className="text-muted-foreground mt-2">
              {isSuccess 
                ? 'Your password has been reset successfully' 
                : 'Create a new password for your account'}
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
          
          {isSuccess ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center space-y-6"
            >
              <div className="bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto">
                <CheckCircle className="h-10 w-10 text-primary" />
              </div>
              
              <div className="space-y-2">
                <h2 className="text-xl font-semibold">Password Reset Complete</h2>
                <p className="text-muted-foreground">
                  Your password has been reset successfully. You will be redirected to the login page shortly.
                </p>
              </div>
              
              <Button asChild className="w-full">
                <Link to="/auth/login">
                  Go to Login
                </Link>
              </Button>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {method === 'otp' && (
                <div className="space-y-2">
                  <label htmlFor="otp" className="text-sm font-medium">
                    One-Time Password (OTP)
                  </label>
                  <div className="relative">
                    <Smartphone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="otp"
                      type="text"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      placeholder="Enter OTP sent to your phone"
                      className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      disabled={isLoading}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Enter the verification code sent to {phone}
                  </p>
                </div>
              )}
              
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      checkPasswordStrength(e.target.value);
                    }}
                    placeholder="Enter new password"
                    className="w-full rounded-md border border-input bg-background pl-10 pr-10 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
                
                {/* Password strength indicator */}
                {password && (
                  <div className="mt-2">
                    <div className="flex gap-1 mb-1">
                      {[1, 2, 3, 4, 5].map((level) => (
                        <div
                          key={level}
                          className={`h-1 flex-1 rounded-full ${
                            passwordStrength >= level
                              ? passwordStrength < 3
                                ? 'bg-destructive'
                                : passwordStrength < 4
                                  ? 'bg-amber-500'
                                  : 'bg-green-500'
                              : 'bg-muted'
                          }`}
                        ></div>
                      ))}
                    </div>
                    <p className={`text-xs ${
                      passwordStrength < 3
                        ? 'text-destructive'
                        : passwordStrength < 4
                          ? 'text-amber-500'
                          : 'text-green-500'
                    }`}>
                      {passwordStrength < 3
                        ? 'Weak password'
                        : passwordStrength < 4
                          ? 'Moderate password'
                          : 'Strong password'}
                    </p>
                  </div>
                )}
                
                <div className="text-xs text-muted-foreground mt-1">
                  Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters.
                </div>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                    className="w-full rounded-md border border-input bg-background pl-10 pr-10 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Resetting Password...
                  </span>
                ) : (
                  'Reset Password'
                )}
              </Button>
              
              <div className="flex items-center justify-center">
                <Link
                  to="/auth/login"
                  className="flex items-center text-sm text-primary hover:underline"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Login
                </Link>
              </div>
            </form>
          )}
        </div>
      </motion.div>
    </div>
  );
}