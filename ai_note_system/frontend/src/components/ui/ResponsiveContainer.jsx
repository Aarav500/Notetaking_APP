import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

/**
 * Screen size breakpoints
 */
const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

/**
 * ResponsiveContainer component that adapts content based on screen size
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Default content
 * @param {React.ReactNode} props.smallScreen - Content to show on small screens
 * @param {React.ReactNode} props.mediumScreen - Content to show on medium screens
 * @param {React.ReactNode} props.largeScreen - Content to show on large screens
 * @param {boolean} props.hideOnMobile - Whether to hide content on mobile screens
 * @param {boolean} props.hideOnTablet - Whether to hide content on tablet screens
 * @param {boolean} props.hideOnDesktop - Whether to hide content on desktop screens
 * @param {string} props.className - Additional CSS classes
 */
const ResponsiveContainer = ({
  children,
  smallScreen,
  mediumScreen,
  largeScreen,
  hideOnMobile = false,
  hideOnTablet = false,
  hideOnDesktop = false,
  className = '',
}) => {
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 0
  );
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Don't render anything during SSR or before mount
  if (!isMounted) {
    return null;
  }

  // Determine screen size
  const isMobile = windowWidth < breakpoints.md;
  const isTablet = windowWidth >= breakpoints.md && windowWidth < breakpoints.lg;
  const isDesktop = windowWidth >= breakpoints.lg;

  // Check if content should be hidden based on screen size
  if ((isMobile && hideOnMobile) || (isTablet && hideOnTablet) || (isDesktop && hideOnDesktop)) {
    return null;
  }

  // Determine which content to render based on screen size
  let content = children;
  if (isMobile && smallScreen !== undefined) {
    content = smallScreen;
  } else if (isTablet && mediumScreen !== undefined) {
    content = mediumScreen;
  } else if (isDesktop && largeScreen !== undefined) {
    content = largeScreen;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      {content}
    </motion.div>
  );
};

/**
 * Hook to get current screen size and breakpoint information
 * @returns {Object} Screen size information
 */
export const useScreenSize = () => {
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 0
  );
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Don't provide accurate information during SSR or before mount
  if (!isMounted) {
    return {
      width: 0,
      isMobile: false,
      isTablet: false,
      isDesktop: false,
      isLargeDesktop: false,
      breakpoint: null,
    };
  }

  // Determine current breakpoint
  let breakpoint = 'xs';
  if (windowWidth >= breakpoints['2xl']) breakpoint = '2xl';
  else if (windowWidth >= breakpoints.xl) breakpoint = 'xl';
  else if (windowWidth >= breakpoints.lg) breakpoint = 'lg';
  else if (windowWidth >= breakpoints.md) breakpoint = 'md';
  else if (windowWidth >= breakpoints.sm) breakpoint = 'sm';

  return {
    width: windowWidth,
    isMobile: windowWidth < breakpoints.md,
    isTablet: windowWidth >= breakpoints.md && windowWidth < breakpoints.lg,
    isDesktop: windowWidth >= breakpoints.lg,
    isLargeDesktop: windowWidth >= breakpoints.xl,
    breakpoint,
  };
};

/**
 * Component that only renders on mobile screens
 */
export const MobileOnly = ({ children, className = '' }) => {
  const { isMobile } = useScreenSize();
  return isMobile ? <div className={className}>{children}</div> : null;
};

/**
 * Component that only renders on tablet screens
 */
export const TabletOnly = ({ children, className = '' }) => {
  const { isTablet } = useScreenSize();
  return isTablet ? <div className={className}>{children}</div> : null;
};

/**
 * Component that only renders on desktop screens
 */
export const DesktopOnly = ({ children, className = '' }) => {
  const { isDesktop } = useScreenSize();
  return isDesktop ? <div className={className}>{children}</div> : null;
};

/**
 * Component that renders on tablet and larger screens
 */
export const TabletAndAbove = ({ children, className = '' }) => {
  const { isMobile } = useScreenSize();
  return !isMobile ? <div className={className}>{children}</div> : null;
};

/**
 * Component that renders on mobile and tablet screens
 */
export const MobileAndTablet = ({ children, className = '' }) => {
  const { isDesktop } = useScreenSize();
  return !isDesktop ? <div className={className}>{children}</div> : null;
};

export default ResponsiveContainer;