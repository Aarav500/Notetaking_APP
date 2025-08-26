/**
 * Utility functions for dashboard components
 */

/**
 * Format a date string into various formats
 * 
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type: 'short', 'medium', 'long', 'month', 'monthYear', 'weekday'
 * @returns {string} - Formatted date string
 */
export const formatDate = (date, format = 'medium') => {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  
  // Return empty string for invalid dates
  if (isNaN(dateObj.getTime())) return '';
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString(undefined, { 
        month: 'numeric', 
        day: 'numeric' 
      });
    case 'medium':
      return dateObj.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    case 'long':
      return dateObj.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    case 'month':
      return dateObj.toLocaleDateString(undefined, { month: 'short' });
    case 'monthYear':
      return dateObj.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short' 
      });
    case 'weekday':
      return dateObj.toLocaleDateString(undefined, { weekday: 'short' });
    default:
      return dateObj.toLocaleDateString();
  }
};

/**
 * Format a number with appropriate units (K, M, B)
 * 
 * @param {number} num - Number to format
 * @param {number} digits - Number of decimal places
 * @returns {string} - Formatted number
 */
export const formatNumber = (num, digits = 1) => {
  if (num === null || num === undefined) return '';
  if (num === 0) return '0';
  
  const isNegative = num < 0;
  const absNum = Math.abs(num);
  
  if (absNum < 1000) {
    return isNegative ? `-${absNum}` : `${absNum}`;
  }
  
  const units = ['', 'K', 'M', 'B', 'T'];
  const exponent = Math.min(Math.floor(Math.log10(absNum) / 3), units.length - 1);
  const formattedNum = (absNum / Math.pow(1000, exponent)).toFixed(digits);
  
  // Remove trailing zeros after decimal point
  const trimmedNum = formattedNum.replace(/\.0+$/, '');
  
  return `${isNegative ? '-' : ''}${trimmedNum}${units[exponent]}`;
};

/**
 * Format a duration in seconds to a readable string
 * 
 * @param {number} seconds - Duration in seconds
 * @param {boolean} short - Whether to use short format
 * @returns {string} - Formatted duration
 */
export const formatDuration = (seconds, short = false) => {
  if (seconds === 0) return short ? '0m' : '0 minutes';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  let result = '';
  
  if (hours > 0) {
    result += short ? `${hours}h ` : `${hours} hour${hours !== 1 ? 's' : ''} `;
  }
  
  if (minutes > 0 || hours > 0) {
    result += short ? `${minutes}m ` : `${minutes} minute${minutes !== 1 ? 's' : ''} `;
  }
  
  if (remainingSeconds > 0 && hours === 0) {
    result += short ? `${remainingSeconds}s` : `${remainingSeconds} second${remainingSeconds !== 1 ? 's' : ''}`;
  }
  
  return result.trim();
};

/**
 * Format a percentage value
 * 
 * @param {number} value - Percentage value
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted percentage
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '';
  
  // Handle whole numbers without decimal places
  if (Number.isInteger(value)) {
    return `${value}%`;
  }
  
  return `${value.toFixed(decimals)}%`;
};

/**
 * Calculate derived statistics from raw data
 * 
 * @param {Object} data - Raw statistics data
 * @returns {Object} - Derived statistics
 */
export const calculateDerivedStats = (data) => {
  const result = {};
  
  // Calculate completion rate
  if ('total' in data && 'completed' in data && data.total > 0) {
    result.completionRate = (data.completed / data.total) * 100;
  }
  
  // Calculate accuracy
  if ('correct' in data && 'incorrect' in data) {
    const total = data.correct + data.incorrect;
    result.accuracy = total > 0 ? (data.correct / total) * 100 : 0;
  }
  
  // Calculate average
  if ('sum' in data && 'count' in data && data.count > 0) {
    result.average = data.sum / data.count;
  }
  
  return result;
};

/**
 * Generate data for time series charts
 * 
 * @param {Array} data - Array of data points with date and values
 * @param {Object} options - Chart options
 * @returns {Object} - Chart data
 */
export const generateTimeSeriesChartData = (data, options = {}) => {
  const {
    valueFields = ['value'],
    labels = [],
    colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444'],
  } = options;
  
  // Sort data by date
  const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
  
  // Extract dates for labels
  const chartLabels = sortedData.map(item => formatDate(item.date, 'short'));
  
  // Create datasets
  const datasets = valueFields.map((field, index) => {
    return {
      label: labels[index] || field,
      data: sortedData.map(item => item[field] || 0),
      borderColor: colors[index % colors.length],
      backgroundColor: `${colors[index % colors.length]}33`, // Add transparency
      tension: 0.3,
    };
  });
  
  return {
    labels: chartLabels,
    datasets,
  };
};

/**
 * Generate data for heatmap visualization
 * 
 * @param {Array} data - Array of data points with date and count
 * @returns {Array} - Processed data for heatmap
 */
export const generateHeatmapData = (data) => {
  // Define color scale for activity levels
  const colorScale = [
    '#ebedf0', // No activity
    '#9be9a8', // Level 1
    '#40c463', // Level 2
    '#30a14e', // Level 3
    '#216e39', // Level 4
    '#0d4a26', // Level 5
  ];
  
  // Find maximum count to normalize colors
  const maxCount = Math.max(...data.map(item => item.count), 5);
  
  // Process data for heatmap
  return data.map(item => {
    const count = item.count || 0;
    
    // Determine color based on activity level
    let colorIndex = 0;
    if (count > 0) {
      // Scale count to 1-5 range for color index
      colorIndex = Math.min(Math.ceil((count / maxCount) * 5), 5);
    }
    
    return {
      date: item.date,
      count,
      color: colorScale[colorIndex],
    };
  });
};

/**
 * Calculate streak statistics from activity data
 * 
 * @param {Array} data - Array of data points with date and count
 * @returns {Object} - Streak statistics
 */
export const calculateStreakStats = (data) => {
  // Sort data by date
  const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
  
  let currentStreak = 0;
  let longestStreak = 0;
  let currentStreakDays = [];
  let longestStreakDays = [];
  
  // Calculate streaks
  for (let i = 0; i < sortedData.length; i++) {
    const item = sortedData[i];
    
    if (item.count > 0) {
      // Check if this day continues the streak
      if (i === 0 || isConsecutiveDay(sortedData[i-1].date, item.date)) {
        currentStreak++;
        currentStreakDays.push(item.date);
      } else {
        // Streak broken
        currentStreak = 1;
        currentStreakDays = [item.date];
      }
      
      // Update longest streak if current streak is longer
      if (currentStreak > longestStreak) {
        longestStreak = currentStreak;
        longestStreakDays = [...currentStreakDays];
      }
    } else {
      // No activity, reset current streak
      currentStreak = 0;
      currentStreakDays = [];
    }
  }
  
  return {
    currentStreak,
    longestStreak,
    currentStreakDays,
    longestStreakDays,
    totalDays: sortedData.filter(item => item.count > 0).length,
  };
};

/**
 * Check if two dates are consecutive days
 * 
 * @param {string} date1 - First date
 * @param {string} date2 - Second date
 * @returns {boolean} - Whether the dates are consecutive
 */
const isConsecutiveDay = (date1, date2) => {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  
  // Set time to midnight to compare only dates
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);
  
  // Calculate difference in days
  const diffTime = d2.getTime() - d1.getTime();
  const diffDays = diffTime / (1000 * 60 * 60 * 24);
  
  return diffDays === 1;
};

export default {
  formatDate,
  formatNumber,
  formatDuration,
  formatPercentage,
  calculateDerivedStats,
  generateTimeSeriesChartData,
  generateHeatmapData,
  calculateStreakStats,
};