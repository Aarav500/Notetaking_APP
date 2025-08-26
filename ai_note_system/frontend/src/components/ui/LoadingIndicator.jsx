import { motion } from 'framer-motion';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * LoadingIndicator component for displaying loading states and progress
 * 
 * @param {Object} props
 * @param {boolean} props.loading - Whether the component is in loading state
 * @param {boolean} props.error - Whether there's an error
 * @param {boolean} props.success - Whether operation completed successfully
 * @param {string} props.loadingText - Text to display during loading
 * @param {string} props.errorText - Text to display on error
 * @param {string} props.successText - Text to display on success
 * @param {number} props.progress - Progress percentage (0-100)
 * @param {'spinner' | 'bar' | 'dots'} props.type - Type of loading indicator
 * @param {'sm' | 'md' | 'lg'} props.size - Size of the loading indicator
 * @param {string} props.className - Additional CSS classes
 */
const LoadingIndicator = ({
  loading = false,
  error = false,
  success = false,
  loadingText = 'Loading...',
  errorText = 'An error occurred',
  successText = 'Completed successfully',
  progress = null,
  type = 'spinner',
  size = 'md',
  className = '',
}) => {
  // Size mappings
  const sizeClasses = {
    sm: {
      container: 'text-sm',
      icon: 'h-4 w-4',
      bar: 'h-1',
    },
    md: {
      container: 'text-base',
      icon: 'h-5 w-5',
      bar: 'h-2',
    },
    lg: {
      container: 'text-lg',
      icon: 'h-6 w-6',
      bar: 'h-3',
    },
  };

  // Determine what to render based on state
  const renderContent = () => {
    if (error) {
      return (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
          className="flex items-center text-destructive"
        >
          <AlertCircle className={cn(sizeClasses[size].icon, "mr-2")} />
          <span>{errorText}</span>
        </motion.div>
      );
    }

    if (success) {
      return (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
          className="flex items-center text-green-500"
        >
          <CheckCircle className={cn(sizeClasses[size].icon, "mr-2")} />
          <span>{successText}</span>
        </motion.div>
      );
    }

    if (loading) {
      if (type === 'spinner') {
        return (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }}
            className="flex items-center"
          >
            <Loader2 className={cn(sizeClasses[size].icon, "mr-2 animate-spin")} />
            <span>{loadingText}</span>
            {progress !== null && (
              <span className="ml-2 text-muted-foreground">{Math.round(progress)}%</span>
            )}
          </motion.div>
        );
      }

      if (type === 'bar') {
        return (
          <div className="space-y-2">
            {loadingText && <div className="text-sm">{loadingText}</div>}
            <div className="w-full bg-secondary rounded-full overflow-hidden">
              <motion.div 
                className={cn("bg-primary", sizeClasses[size].bar)}
                initial={{ width: 0 }}
                animate={{ width: `${progress !== null ? progress : 100}%` }}
                transition={{ 
                  duration: progress !== null ? 0.3 : 1.5,
                  ease: progress !== null ? "easeOut" : "linear",
                  repeat: progress !== null ? 0 : Infinity,
                  repeatType: "reverse"
                }}
              />
            </div>
            {progress !== null && (
              <div className="text-right text-xs text-muted-foreground">{Math.round(progress)}%</div>
            )}
          </div>
        );
      }

      if (type === 'dots') {
        return (
          <div className="flex flex-col items-center space-y-2">
            {loadingText && <div>{loadingText}</div>}
            <div className="flex space-x-2">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className={cn(
                    "rounded-full bg-primary",
                    size === 'sm' ? 'h-1.5 w-1.5' : size === 'md' ? 'h-2 w-2' : 'h-3 w-3'
                  )}
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                />
              ))}
            </div>
            {progress !== null && (
              <div className="text-xs text-muted-foreground">{Math.round(progress)}%</div>
            )}
          </div>
        );
      }
    }

    // Default: nothing to show
    return null;
  };

  return (
    <div className={cn("flex justify-center items-center", sizeClasses[size].container, className)}>
      {renderContent()}
    </div>
  );
};

export default LoadingIndicator;