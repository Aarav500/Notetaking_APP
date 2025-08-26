import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { GripVertical } from 'lucide-react';

/**
 * A resizable split screen component with smooth animations
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.left - Content for the left panel
 * @param {React.ReactNode} props.right - Content for the right panel
 * @param {number} props.initialLeftWidth - Initial width of left panel in percentage (1-99)
 * @param {number} props.minLeftWidth - Minimum width of left panel in percentage
 * @param {number} props.maxLeftWidth - Maximum width of left panel in percentage
 * @param {Function} props.onResize - Callback when resize happens, receives leftWidth percentage
 * @param {string} props.className - Additional CSS classes
 */
const ResizableSplitScreen = ({
  left,
  right,
  initialLeftWidth = 50,
  minLeftWidth = 20,
  maxLeftWidth = 80,
  onResize,
  className = '',
}) => {
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);
  const initialX = useRef(0);
  const initialLeftWidthRef = useRef(0);

  // Handle mouse down on the divider
  const handleMouseDown = (e) => {
    setIsDragging(true);
    initialX.current = e.clientX;
    initialLeftWidthRef.current = leftWidth;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  // Handle touch start on the divider
  const handleTouchStart = (e) => {
    setIsDragging(true);
    initialX.current = e.touches[0].clientX;
    initialLeftWidthRef.current = leftWidth;
    document.body.style.userSelect = 'none';
  };

  // Handle mouse move
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !containerRef.current) return;
      
      const containerWidth = containerRef.current.offsetWidth;
      const deltaX = e.clientX - initialX.current;
      const deltaPercentage = (deltaX / containerWidth) * 100;
      const newLeftWidth = Math.min(
        Math.max(initialLeftWidthRef.current + deltaPercentage, minLeftWidth),
        maxLeftWidth
      );
      
      setLeftWidth(newLeftWidth);
      if (onResize) onResize(newLeftWidth);
    };

    const handleTouchMove = (e) => {
      if (!isDragging || !containerRef.current) return;
      
      const containerWidth = containerRef.current.offsetWidth;
      const deltaX = e.touches[0].clientX - initialX.current;
      const deltaPercentage = (deltaX / containerWidth) * 100;
      const newLeftWidth = Math.min(
        Math.max(initialLeftWidthRef.current + deltaPercentage, minLeftWidth),
        maxLeftWidth
      );
      
      setLeftWidth(newLeftWidth);
      if (onResize) onResize(newLeftWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchend', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, minLeftWidth, maxLeftWidth, onResize]);

  return (
    <div 
      ref={containerRef} 
      className={`flex h-full w-full overflow-hidden ${className}`}
    >
      {/* Left panel */}
      <motion.div
        className="h-full overflow-auto"
        style={{ width: `${leftWidth}%` }}
        animate={{ width: `${leftWidth}%` }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {left}
      </motion.div>

      {/* Resizer */}
      <div
        className={`relative w-1 h-full bg-border cursor-col-resize flex items-center justify-center z-10 hover:bg-primary/50 transition-colors ${
          isDragging ? 'bg-primary' : ''
        }`}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
      >
        <div className="absolute flex items-center justify-center w-6 h-10 bg-background border border-border rounded-full">
          <GripVertical className="h-4 w-4 text-muted-foreground" />
        </div>
      </div>

      {/* Right panel */}
      <motion.div
        className="h-full overflow-auto"
        style={{ width: `${100 - leftWidth}%` }}
        animate={{ width: `${100 - leftWidth}%` }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {right}
      </motion.div>
    </div>
  );
};

export default ResizableSplitScreen;