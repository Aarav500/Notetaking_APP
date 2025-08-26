import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import useUserStore from './useUserStore';
import useReadingStore from './useReadingStore';
import useFlashcardStore from './useFlashcardStore';
import useNotesStore from './useNotesStore';
import useVisualizationsStore from './useVisualizationsStore';

/**
 * Dashboard store that aggregates data from other stores for dashboard display
 * This provides a centralized place for dashboard-specific data and methods
 */
const useDashboardStore = create(
  persist(
    (set, get) => ({
      // Cache for dashboard data to improve performance
      cache: {
        lastUpdated: null,
        overview: null,
        recentActivity: null,
        stats: null,
      },
      
      // Cache expiration time in milliseconds (5 minutes)
      cacheExpiration: 5 * 60 * 1000,
      
      // Check if cache is valid
      isCacheValid: (cacheKey) => {
        const { cache, cacheExpiration } = get();
        if (!cache[cacheKey] || !cache.lastUpdated) return false;
        
        const now = Date.now();
        return (now - cache.lastUpdated) < cacheExpiration;
      },
      
      // Update cache
      updateCache: (cacheKey, data) => {
        set(state => ({
          cache: {
            ...state.cache,
            [cacheKey]: data,
            lastUpdated: Date.now(),
          }
        }));
      },
      
      // Clear cache
      clearCache: () => {
        set({
          cache: {
            lastUpdated: null,
            overview: null,
            recentActivity: null,
            stats: null,
          }
        });
      },
      
      // Get dashboard overview data
      getDashboardOverview: () => {
        // Check cache first
        if (get().isCacheValid('overview')) {
          return get().cache.overview;
        }
        
        // Get data from stores
        const userStore = useUserStore.getState();
        const readingStore = useReadingStore.getState();
        const flashcardStore = useFlashcardStore.getState();
        const notesStore = useNotesStore.getState();
        
        // User progress data
        const { level, xp, xpToNextLevel, streaks } = userStore.getProgress();
        
        // Reading stats
        const readingStats = readingStore.getReadingStats();
        
        // Flashcard stats
        const flashcardStats = flashcardStore.getStudyStats();
        
        // Notes count
        const notesCount = notesStore.notes.length;
        
        // Create overview object
        const overview = {
          user: {
            level,
            xp,
            xpToNextLevel,
            xpPercentage: (xp / xpToNextLevel) * 100,
            streaks,
          },
          reading: {
            booksCount: readingStats.totalBooks,
            pagesRead: readingStats.pagesRead,
            completionRate: readingStats.completionRate,
            readingStreak: readingStats.readingStreak,
          },
          flashcards: {
            cardsCount: flashcardStats.totalCards,
            cardsLearned: flashcardStats.cardsLearned,
            accuracy: flashcardStats.accuracy,
            studyStreak: flashcardStats.studyStreak,
          },
          notes: {
            count: notesCount,
          },
        };
        
        // Update cache
        get().updateCache('overview', overview);
        
        return overview;
      },
      
      // Get recent activity for dashboard
      getRecentActivity: (limit = 10) => {
        // Check cache first
        if (get().isCacheValid('recentActivity')) {
          return get().cache.recentActivity;
        }
        
        // Get data from stores
        const userStore = useUserStore.getState();
        const readingStore = useReadingStore.getState();
        const flashcardStore = useFlashcardStore.getState();
        const notesStore = useNotesStore.getState();
        
        // Get recent books
        const recentBooks = readingStore.getRecentBooks(limit).map(book => ({
          type: 'book',
          id: book.id,
          title: book.title,
          timestamp: new Date(book.lastRead).getTime(),
          data: book,
        }));
        
        // Get recent notes
        const recentNotes = [...notesStore.notes]
          .sort((a, b) => new Date(b.lastEdited) - new Date(a.lastEdited))
          .slice(0, limit)
          .map(note => ({
            type: 'note',
            id: note.id,
            title: note.title,
            timestamp: new Date(note.lastEdited).getTime(),
            data: note,
          }));
        
        // Get recent study sessions
        const recentSessions = flashcardStore.studySessions
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, limit)
          .map(session => ({
            type: 'study',
            id: session.id,
            title: `Study Session: ${flashcardStore.getDeckById(session.deckId)?.name || 'Unknown Deck'}`,
            timestamp: new Date(session.date).getTime(),
            data: session,
          }));
        
        // Combine and sort all recent activity
        const allActivity = [...recentBooks, ...recentNotes, ...recentSessions]
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, limit);
        
        // Update cache
        get().updateCache('recentActivity', allActivity);
        
        return allActivity;
      },
      
      // Get comprehensive stats for dashboard
      getDashboardStats: () => {
        // Check cache first
        if (get().isCacheValid('stats')) {
          return get().cache.stats;
        }
        
        // Get data from stores
        const userStore = useUserStore.getState();
        const readingStore = useReadingStore.getState();
        const flashcardStore = useFlashcardStore.getState();
        const notesStore = useNotesStore.getState();
        const visualizationsStore = useVisualizationsStore.getState();
        
        // Get activity data for heatmap
        const activityData = userStore.getActivity(30);
        
        // Get reading stats
        const readingStats = readingStore.getReadingStats();
        
        // Get flashcard stats
        const flashcardStats = flashcardStore.getStudyStats();
        
        // Get projects
        const projects = userStore.getProjects();
        
        // Get achievements
        const achievements = userStore.getAchievements();
        const unlockedAchievements = achievements.filter(a => a.unlockedAt !== null);
        const inProgressAchievements = achievements.filter(a => a.unlockedAt === null && a.progress > 0);
        
        // Get knowledge graphs
        const knowledgeGraphs = visualizationsStore.visualizations.filter(
          viz => viz.type === 'knowledge_graph'
        );
        
        // Get latest knowledge graph
        const latestKnowledgeGraph = knowledgeGraphs.length > 0
          ? knowledgeGraphs.sort((a, b) => new Date(b.date) - new Date(a.date))[0]
          : null;
        
        // Create stats object
        const stats = {
          activity: {
            data: activityData,
            daysWithActivity: Object.values(activityData).filter(value => value > 0).length,
            maxActivityLevel: Math.max(...Object.values(activityData), 0),
          },
          reading: readingStats,
          flashcards: flashcardStats,
          projects: {
            count: projects.length,
            inProgress: projects.filter(p => p.progress > 0 && p.progress < 100).length,
            completed: projects.filter(p => p.progress >= 100).length,
          },
          achievements: {
            total: achievements.length,
            unlocked: unlockedAchievements.length,
            inProgress: inProgressAchievements.length,
            completion: achievements.length > 0 
              ? (unlockedAchievements.length / achievements.length) * 100 
              : 0,
          },
          knowledgeGraph: latestKnowledgeGraph ? {
            id: latestKnowledgeGraph.id,
            title: latestKnowledgeGraph.title,
            nodeCount: latestKnowledgeGraph.data?.nodes?.length || 0,
            edgeCount: latestKnowledgeGraph.data?.edges?.length || 0,
          } : null,
        };
        
        // Update cache
        get().updateCache('stats', stats);
        
        return stats;
      },
      
      // Get recent books with enhanced data for dashboard
      getEnhancedRecentBooks: (limit = 5) => {
        const readingStore = useReadingStore.getState();
        const recentBooks = readingStore.getRecentBooks(limit);
        
        // Enhance books with additional data
        return recentBooks.map(book => {
          // Get annotations count
          const annotations = book.annotations || [];
          
          // Calculate reading time (estimated)
          const pagesRead = Math.floor(book.totalPages * (book.progress / 100));
          const estimatedReadingTime = pagesRead * 2; // 2 minutes per page (average)
          
          return {
            ...book,
            annotationsCount: annotations.length,
            estimatedReadingTime,
            daysActive: Math.floor(Math.random() * 10) + 1, // Mock data, would be calculated from reading history
          };
        });
      },
      
      // Get projects with enhanced data for dashboard
      getEnhancedProjects: () => {
        const userStore = useUserStore.getState();
        const projects = userStore.getProjects();
        
        // Enhance projects with additional data
        return projects.map(project => {
          // Calculate activity level (1-5)
          const activityLevel = Math.min(
            5, 
            Math.ceil(
              (new Date() - new Date(project.lastUpdated)) / (1000 * 60 * 60 * 24)
            )
          );
          
          // Calculate total items
          const totalItems = 
            project.items.books.length + 
            project.items.notes.length + 
            project.items.decks.length;
          
          return {
            ...project,
            activityLevel: 6 - activityLevel, // Invert so 5 is most active, 1 is least
            totalItems,
            daysActive: Math.floor(
              (new Date() - new Date(project.createdAt)) / (1000 * 60 * 60 * 24)
            ),
          };
        });
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({
          cache: {
            lastUpdated: null,
            overview: null,
            recentActivity: null,
            stats: null,
          }
        });
      }
    }),
    {
      name: 'dashboard-storage', // Name for localStorage
      partialize: (state) => ({ 
        cache: state.cache,
        cacheExpiration: state.cacheExpiration,
      }),
    }
  )
);

export default useDashboardStore;