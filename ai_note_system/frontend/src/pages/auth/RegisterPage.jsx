import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Eye, EyeOff, UserPlus, AlertCircle, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import useSettingsStore from '@/store/useSettingsStore';
import api from '@/lib/api';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const register = useSettingsStore((state) => state.register);
  
  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  
  // Password strength
  const [passwordStrength, setPasswordStrength] = useState(0);
  
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
  
  // Validate form
  const validateForm = () => {
    const errors = {};
    
    if (!name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (passwordStrength < 3) {
      errors.password = 'Password is too weak';
    }
    
    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    if (!agreeToTerms) {
      errors.agreeToTerms = 'You must agree to the terms and conditions';
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    // Clear previous errors
    setError('');
    setIsLoading(true);
    
    try {
      // Call the API to register
      const response = await api.auth.register({ 
        name, 
        email, 
        password 
      });
      
      // Update the auth state in the store
      register(response.data.user);
      
      // Show success message
      toast({
        title: 'Registration Successful',
        description: 'Your account has been created successfully!',
      });
      
      // Redirect to the dashboard
      navigate('/', { replace: true });
    } catch (err) {
      console.error('Registration error:', err);
      
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 409:
            setError('Email already in use. Please use a different email or try logging in.');
            break;
          case 400:
            if (err.response.data.errors) {
              // Set field-specific errors
              const apiErrors = {};
              err.response.data.errors.forEach(error => {
                apiErrors[error.field] = error.message;
              });
              setFieldErrors(apiErrors);
            } else {
              setError('Invalid registration data. Please check your information.');
            }
            break;
          default:
            setError('An error occurred during registration. Please try again.');
        }
      } else {
        setError('Unable to connect to the server. Please check your internet connection.');
      }
    } finally {
      setIsLoading(false);
    }
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
            <h1 className="text-3xl font-bold">Create Account</h1>
            <p className="text-muted-foreground mt-2">
              Sign up to get started with Pansophy
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
              <label htmlFor="name" className="text-sm font-medium">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                className={`w-full rounded-md border ${fieldErrors.name ? 'border-destructive' : 'border-input'} bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
                disabled={isLoading}
              />
              {fieldErrors.name && (
                <p className="text-destructive text-xs mt-1">{fieldErrors.name}</p>
              )}
            </div>
            
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
                className={`w-full rounded-md border ${fieldErrors.email ? 'border-destructive' : 'border-input'} bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
                disabled={isLoading}
              />
              {fieldErrors.email && (
                <p className="text-destructive text-xs mt-1">{fieldErrors.email}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    checkPasswordStrength(e.target.value);
                  }}
                  placeholder="Create a password"
                  className={`w-full rounded-md border ${fieldErrors.password ? 'border-destructive' : 'border-input'} bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
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
              
              {fieldErrors.password && (
                <p className="text-destructive text-xs mt-1">{fieldErrors.password}</p>
              )}
              
              <div className="text-xs text-muted-foreground mt-1">
                Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters.
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  className={`w-full rounded-md border ${fieldErrors.confirmPassword ? 'border-destructive' : 'border-input'} bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
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
              {fieldErrors.confirmPassword && (
                <p className="text-destructive text-xs mt-1">{fieldErrors.confirmPassword}</p>
              )}
            </div>
            
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="terms"
                  type="checkbox"
                  checked={agreeToTerms}
                  onChange={(e) => setAgreeToTerms(e.target.checked)}
                  className={`h-4 w-4 rounded border-input ${fieldErrors.agreeToTerms ? 'border-destructive' : ''}`}
                  disabled={isLoading}
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="terms" className="text-sm">
                  I agree to the{' '}
                  <Link to="/terms" className="text-primary hover:underline">
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link to="/privacy" className="text-primary hover:underline">
                    Privacy Policy
                  </Link>
                </label>
                {fieldErrors.agreeToTerms && (
                  <p className="text-destructive text-xs mt-1">{fieldErrors.agreeToTerms}</p>
                )}
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
                  Creating Account...
                </span>
              ) : (
                <span className="flex items-center">
                  <UserPlus className="mr-2 h-4 w-4" />
                  Create Account
                </span>
              )}
            </Button>
          </form>
          
          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Already have an account?</span>{' '}
            <Link to="/auth/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}