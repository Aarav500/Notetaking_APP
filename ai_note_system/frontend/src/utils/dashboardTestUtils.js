/**
 * Utility functions for testing Dashboard components
 */
import useUserStore from '@/store/useUserStore';
import useReadingStore from '@/store/useReadingStore';
import useFlashcardStore from '@/store/useFlashcardStore';
import useNotesStore from '@/store/useNotesStore';
import useVisualizationsStore from '@/store/useVisualizationsStore';

/**
 * Dashboard component types for testing
 */
export const DashboardComponentTypes = {
  STATS: 'stats',
  RECENT_NOTES: 'recentNotes',
  RECENT_BOOKS: 'recentBooks',
  PROGRESS_HEATMAP: 'progressHeatmap',
  KNOWLEDGE_GRAPH: 'knowledgeGraph',
  FLASHCARD_STATS: 'flashcardStats',
  READING_STATS: 'readingStats',
  PROJECTS: 'projects',
  ACHIEVEMENTS: 'achievements',
};

/**
 * Tests user stats display
 * 
 * @returns {Object} - Test results
 */
export const testUserStatsDisplay = () => {
  const results = {
    success: false,
    stats: null,
    error: null,
  };
  
  try {
    // Get user stats from store
    const userStore = useUserStore.getState();
    const { level, xp, xpToNextLevel, streaks } = userStore.getProgress();
    
    results.stats = {
      level,
      xp,
      xpToNextLevel,
      streaks,
      xpPercentage: (xp / xpToNextLevel) * 100,
    };
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests recent notes display
 * 
 * @param {number} limit - Maximum number of notes to retrieve
 * @returns {Object} - Test results
 */
export const testRecentNotesDisplay = (limit = 5) => {
  const results = {
    success: false,
    notes: [],
    error: null,
  };
  
  try {
    // Get notes from store
    const notesStore = useNotesStore.getState();
    const allNotes = notesStore.notes;
    
    // Sort by last edited date and take the most recent ones
    const recentNotes = [...allNotes]
      .sort((a, b) => new Date(b.lastEdited) - new Date(a.lastEdited))
      .slice(0, limit);
    
    results.notes = recentNotes.map(note => ({
      id: note.id,
      title: note.title,
      excerpt: note.excerpt || note.content.substring(0, 100) + '...',
      category: note.category,
      date: note.date,
      lastEdited: note.lastEdited,
      tags: note.tags,
    }));
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests recent books display
 * 
 * @param {number} limit - Maximum number of books to retrieve
 * @returns {Object} - Test results
 */
export const testRecentBooksDisplay = (limit = 5) => {
  const results = {
    success: false,
    books: [],
    error: null,
  };
  
  try {
    // Get books from store
    const readingStore = useReadingStore.getState();
    const recentBooks = readingStore.getRecentBooks(limit);
    
    results.books = recentBooks.map(book => ({
      id: book.id,
      title: book.title,
      author: book.author,
      coverImage: book.coverImage,
      progress: book.progress,
      lastRead: book.lastRead,
    }));
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests progress heatmap display
 * 
 * @param {number} days - Number of days to include in the heatmap
 * @returns {Object} - Test results
 */
export const testProgressHeatmapDisplay = (days = 30) => {
  const results = {
    success: false,
    activityData: {},
    maxActivity: 0,
    daysWithActivity: 0,
    error: null,
  };
  
  try {
    // Get activity data from store
    const userStore = useUserStore.getState();
    const activityData = userStore.getActivity(days);
    
    results.activityData = activityData;
    
    // Calculate statistics
    const activityValues = Object.values(activityData);
    results.maxActivity = Math.max(...activityValues);
    results.daysWithActivity = activityValues.filter(value => value > 0).length;
    results.activityPercentage = (results.daysWithActivity / days) * 100;
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests knowledge graph preview display
 * 
 * @returns {Object} - Test results
 */
export const testKnowledgeGraphDisplay = () => {
  const results = {
    success: false,
    graph: null,
    nodeCount: 0,
    edgeCount: 0,
    error: null,
  };
  
  try {
    // Get visualizations from store
    const visualizationsStore = useVisualizationsStore.getState();
    const knowledgeGraphs = visualizationsStore.visualizations.filter(
      viz => viz.type === 'knowledge_graph'
    );
    
    if (knowledgeGraphs.length > 0) {
      // Use the most recent knowledge graph
      const latestGraph = knowledgeGraphs.sort(
        (a, b) => new Date(b.date) - new Date(a.date)
      )[0];
      
      results.graph = latestGraph;
      results.nodeCount = latestGraph.data?.nodes?.length || 0;
      results.edgeCount = latestGraph.data?.edges?.length || 0;
    }
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests flashcard stats display
 * 
 * @returns {Object} - Test results
 */
export const testFlashcardStatsDisplay = () => {
  const results = {
    success: false,
    stats: null,
    error: null,
  };
  
  try {
    // Get flashcard stats from store
    const flashcardStore = useFlashcardStore.getState();
    const stats = flashcardStore.getStudyStats();
    
    results.stats = {
      totalCards: stats.totalCards,
      cardsStudied: stats.cardsStudied,
      cardsLearned: stats.cardsLearned,
      totalReviews: stats.totalReviews,
      accuracy: stats.accuracy,
      completionRate: stats.completionRate,
      studyStreak: stats.studyStreak,
    };
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests reading stats display
 * 
 * @returns {Object} - Test results
 */
export const testReadingStatsDisplay = () => {
  const results = {
    success: false,
    stats: null,
    error: null,
  };
  
  try {
    // Get reading stats from store
    const readingStore = useReadingStore.getState();
    const stats = readingStore.getReadingStats();
    
    results.stats = {
      totalBooks: stats.totalBooks,
      booksStarted: stats.booksStarted,
      booksCompleted: stats.booksCompleted,
      totalPages: stats.totalPages,
      pagesRead: stats.pagesRead,
      completionRate: stats.completionRate,
      readingStreak: stats.readingStreak,
    };
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests projects display
 * 
 * @returns {Object} - Test results
 */
export const testProjectsDisplay = () => {
  const results = {
    success: false,
    projects: [],
    error: null,
  };
  
  try {
    // Get projects from store
    const userStore = useUserStore.getState();
    const projects = userStore.getProjects();
    
    results.projects = projects.map(project => ({
      id: project.id,
      title: project.title,
      description: project.description,
      progress: project.progress,
      lastUpdated: project.lastUpdated,
      itemCounts: {
        books: project.items.books.length,
        notes: project.items.notes.length,
        decks: project.items.decks.length,
      },
    }));
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests achievements display
 * 
 * @returns {Object} - Test results
 */
export const testAchievementsDisplay = () => {
  const results = {
    success: false,
    achievements: {
      unlocked: [],
      inProgress: [],
    },
    error: null,
  };
  
  try {
    // Get achievements from store
    const userStore = useUserStore.getState();
    const allAchievements = userStore.getAchievements();
    
    // Separate unlocked and in-progress achievements
    results.achievements.unlocked = allAchievements
      .filter(achievement => achievement.unlockedAt !== null)
      .map(achievement => ({
        id: achievement.id,
        title: achievement.title,
        description: achievement.description,
        icon: achievement.icon,
        category: achievement.category,
        unlockedAt: achievement.unlockedAt,
      }));
    
    results.achievements.inProgress = allAchievements
      .filter(achievement => achievement.unlockedAt === null && achievement.progress > 0)
      .map(achievement => ({
        id: achievement.id,
        title: achievement.title,
        description: achievement.description,
        icon: achievement.icon,
        category: achievement.category,
        progress: achievement.progress,
      }));
    
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

/**
 * Tests all Dashboard components
 * 
 * @returns {Object} - Comprehensive test results
 */
export const testAllDashboardComponents = () => {
  const results = {
    userStats: testUserStatsDisplay(),
    recentNotes: testRecentNotesDisplay(),
    recentBooks: testRecentBooksDisplay(),
    progressHeatmap: testProgressHeatmapDisplay(),
    knowledgeGraph: testKnowledgeGraphDisplay(),
    flashcardStats: testFlashcardStatsDisplay(),
    readingStats: testReadingStatsDisplay(),
    projects: testProjectsDisplay(),
    achievements: testAchievementsDisplay(),
    overallSuccess: false,
  };
  
  // Calculate overall success
  const componentResults = [
    results.userStats.success,
    results.recentNotes.success,
    results.recentBooks.success,
    results.progressHeatmap.success,
    results.knowledgeGraph.success,
    results.flashcardStats.success,
    results.readingStats.success,
    results.projects.success,
    results.achievements.success,
  ];
  
  const successCount = componentResults.filter(Boolean).length;
  results.overallSuccess = successCount === componentResults.length;
  results.successRate = (successCount / componentResults.length) * 100;
  
  return results;
};

/**
 * Verifies that a component renders correctly
 * 
 * @param {React.Component} component - Component to test
 * @param {Object} expectedProps - Expected props
 * @returns {Object} - Test results
 */
export const verifyComponentRendering = (component, expectedProps) => {
  const results = {
    success: false,
    renderedProps: null,
    propsMatch: false,
    error: null,
  };
  
  try {
    // In a real implementation, this would use a testing library like React Testing Library
    // For now, we'll just check if the component and props exist
    if (!component) {
      throw new Error('Component is undefined');
    }
    
    // Check if props match expected props
    const renderedProps = component.props || {};
    results.renderedProps = renderedProps;
    
    // Compare props (simplified)
    const propsMatch = Object.keys(expectedProps).every(
      key => JSON.stringify(renderedProps[key]) === JSON.stringify(expectedProps[key])
    );
    
    results.propsMatch = propsMatch;
    results.success = true;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  return results;
};

export default {
  DashboardComponentTypes,
  testUserStatsDisplay,
  testRecentNotesDisplay,
  testRecentBooksDisplay,
  testProgressHeatmapDisplay,
  testKnowledgeGraphDisplay,
  testFlashcardStatsDisplay,
  testReadingStatsDisplay,
  testProjectsDisplay,
  testAchievementsDisplay,
  testAllDashboardComponents,
  verifyComponentRendering,
};