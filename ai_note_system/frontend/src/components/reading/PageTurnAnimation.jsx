import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

/**
 * Component that adds page turn animations to PDF pages
 * 
 * @param {Object} props
 * @param {number} props.pageNumber - Current page number
 * @param {number} props.previousPage - Previous page number for animation direction
 * @param {React.ReactNode} props.children - The PDF page content
 * @param {string} props.className - Additional CSS classes
 */
const PageTurnAnimation = ({ 
  pageNumber, 
  previousPage, 
  children, 
  className = '' 
}) => {
  const [direction, setDirection] = useState(0); // 0: initial, 1: forward, -1: backward
  
  useEffect(() => {
    if (previousPage === null) {
      setDirection(0);
    } else if (pageNumber > previousPage) {
      setDirection(1); // forward
    } else if (pageNumber < previousPage) {
      setDirection(-1); // backward
    }
  }, [pageNumber, previousPage]);
  
  // Animation variants
  const pageVariants = {
    initial: (direction) => ({
      opacity: 0,
      x: direction === 1 ? '100%' : direction === -1 ? '-100%' : 0,
      rotateY: direction === 1 ? 15 : direction === -1 ? -15 : 0,
      scale: 0.9,
    }),
    animate: {
      opacity: 1,
      x: 0,
      rotateY: 0,
      scale: 1,
      transition: {
        x: { type: 'spring', stiffness: 300, damping: 30 },
        opacity: { duration: 0.2 },
        rotateY: { duration: 0.4 },
        scale: { duration: 0.3 }
      }
    },
    exit: (direction) => ({
      opacity: 0,
      x: direction === 1 ? '-100%' : direction === -1 ? '100%' : 0,
      rotateY: direction === 1 ? -15 : direction === -1 ? 15 : 0,
      scale: 0.9,
      transition: {
        x: { type: 'spring', stiffness: 300, damping: 30 },
        opacity: { duration: 0.2 },
        rotateY: { duration: 0.4 },
        scale: { duration: 0.3 }
      }
    })
  };
  
  return (
    <AnimatePresence mode="wait" custom={direction}>
      <motion.div
        key={pageNumber}
        custom={direction}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className={`w-full h-full ${className}`}
        style={{ 
          perspective: '1000px',
          transformStyle: 'preserve-3d'
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

export default PageTurnAnimation;