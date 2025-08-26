import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, Mail, ArrowLeft, CheckCircle, MessageSquare, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

export default function ForgotPasswordPage() {
  const { toast } = useToast();
  const navigate = useNavigate();
  
  // Form state
  const [email, setEmail] = useState('');
  const [resetMethod, setResetMethod] = useState('email'); // 'email' or 'otp'
  const [phoneNumber, setPhoneNumber] = useState('');
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Success state
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form based on reset method
    if (resetMethod === 'email') {
      if (!email.trim()) {
        setError('Email is required');
        return;
      }
      
      if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address');
        return;
      }
    } else if (resetMethod === 'otp') {
      if (!phoneNumber.trim()) {
        setError('Phone number is required');
        return;
      }
      
      // Simple phone validation - can be improved
      if (!/^\+?[0-9]{10,15}$/.test(phoneNumber.replace(/\s+/g, ''))) {
        setError('Please enter a valid phone number');
        return;
      }
    }
    
    // Clear previous errors
    setError('');
    setIsLoading(true);
    
    try {
      if (resetMethod === 'email') {
        // Call the API to request password reset via email
        await api.auth.forgotPassword({ email, method: 'email' });
        
        // Show success message
        setIsSubmitted(true);
        
        toast({
          title: 'Reset Email Sent',
          description: 'Check your email for instructions to reset your password',
        });
      } else if (resetMethod === 'otp') {
        // Call the API to request password reset via OTP
        await api.auth.forgotPassword({ phoneNumber, method: 'otp' });
        
        // Show success message
        setIsSubmitted(true);
        
        toast({
          title: 'OTP Sent',
          description: 'Check your phone for the OTP to reset your password',
        });
        
        // Navigate to reset password page with phone number
        navigate(`/auth/reset-password?method=otp&phone=${encodeURIComponent(phoneNumber)}`);
      }
    } catch (err) {
      console.error('Forgot password error:', err);
      
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 404:
            setError(`No account found with this ${resetMethod === 'email' ? 'email address' : 'phone number'}`);
            break;
          case 429:
            setError('Too many requests. Please try again later.');
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
            <h1 className="text-3xl font-bold">Forgot Password</h1>
            <p className="text-muted-foreground mt-2">
              {isSubmitted 
                ? 'Check your email for reset instructions' 
                : 'Enter your email to receive a password reset link'}
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
          
          {isSubmitted ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center space-y-6"
            >
              <div className="bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto">
                <CheckCircle className="h-10 w-10 text-primary" />
              </div>
              
              <div className="space-y-2">
                <h2 className="text-xl font-semibold">Email Sent</h2>
                <p className="text-muted-foreground">
                  We've sent a password reset link to <span className="font-medium text-foreground">{email}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  If you don't see the email in your inbox, please check your spam folder.
                </p>
              </div>
              
              <div className="space-y-4 pt-4">
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    setIsSubmitted(false);
                    setEmail('');
                  }}
                >
                  Try a different email
                </Button>
                
                <div className="text-sm">
                  <span className="text-muted-foreground">Remember your password?</span>{' '}
                  <Link to="/auth/login" className="text-primary hover:underline">
                    Sign in
                  </Link>
                </div>
              </div>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Reset Method Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Reset Method
                </label>
                <div className="flex space-x-2">
                  <Button
                    type="button"
                    variant={resetMethod === 'email' ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => setResetMethod('email')}
                  >
                    <Mail className="mr-2 h-4 w-4" />
                    Email
                  </Button>
                  <Button
                    type="button"
                    variant={resetMethod === 'otp' ? 'default' : 'outline'}
                    className="flex-1"
                    onClick={() => setResetMethod('otp')}
                  >
                    <Smartphone className="mr-2 h-4 w-4" />
                    OTP
                  </Button>
                </div>
              </div>
              
              {resetMethod === 'email' ? (
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      disabled={isLoading}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    We'll send a password reset link to this email address.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <label htmlFor="phoneNumber" className="text-sm font-medium">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Smartphone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="phoneNumber"
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="Enter your phone number"
                      className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      disabled={isLoading}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    We'll send a one-time password (OTP) to this phone number.
                  </p>
                </div>
              )}
              
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
                    Sending...
                  </span>
                ) : (
                  resetMethod === 'email' ? 'Send Reset Link' : 'Send OTP'
                )}
              </Button>
              
              <div className="flex items-center justify-center space-x-4">
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