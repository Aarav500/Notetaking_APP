import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Mock user data
const initialUser = {
  id: 'user-1',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatar: 'https://via.placeholder.com/150',
  joinDate: '2025-01-15',
  role: 'user', // 'user', 'admin'
  isAuthenticated: true,
};

// Initial progress data
const initialProgress = {
  level: 5,
  xp: 1250,
  xpToNextLevel: 2000,
  totalXp: 7250,
  streaks: {
    reading: 7, // days in a row with reading activity
    flashcards: 5, // days in a row with flashcard reviews
    notes: 3, // days in a row with note creation/editing
  },
  achievements: [
    {
      id: 'achievement-1',
      title: 'Bookworm',
      description: 'Read for 7 days in a row',
      icon: 'book',
      unlockedAt: '2025-07-25T10:30:00',
      progress: 100, // percentage
      category: 'reading',
    },
    {
      id: 'achievement-2',
      title: 'Memory Master',
      description: 'Review 100 flashcards',
      icon: 'brain',
      unlockedAt: '2025-07-20T15:45:00',
      progress: 100,
      category: 'flashcards',
    },
    {
      id: 'achievement-3',
      title: 'Knowledge Explorer',
      description: 'Create 10 notes',
      icon: 'map',
      unlockedAt: null,
      progress: 70, // 7/10 notes created
      category: 'notes',
    },
  ],
  stats: {
    reading: {
      totalBooksStarted: 5,
      totalBooksCompleted: 2,
      totalPagesRead: 746,
      totalReadingTime: 3240, // minutes
      averageReadingSpeed: 25, // pages per hour
      lastReadingSession: '2025-07-29T14:30:00',
    },
    flashcards: {
      totalCards: 42,
      totalReviews: 156,
      correctAnswers: 132,
      incorrectAnswers: 24,
      accuracy: 84.6, // percentage
      totalStudyTime: 720, // minutes
      lastStudySession: '2025-07-29T15:30:00',
    },
    notes: {
      totalNotes: 28,
      totalAnnotations: 64,
      totalTags: 35,
      lastNoteCreated: '2025-07-28T11:20:00',
      lastNoteEdited: '2025-07-29T09:45:00',
    },
  },
  activity: {
    // Last 30 days of activity (1-5 scale, 0 = no activity)
    // Format: 'YYYY-MM-DD': activityLevel
    '2025-07-29': 4,
    '2025-07-28': 5,
    '2025-07-27': 3,
    '2025-07-26': 2,
    '2025-07-25': 4,
    '2025-07-24': 3,
    '2025-07-23': 5,
    '2025-07-22': 4,
    '2025-07-21': 2,
    '2025-07-20': 3,
    '2025-07-19': 0,
    '2025-07-18': 1,
    '2025-07-17': 3,
    '2025-07-16': 4,
    '2025-07-15': 2,
    // ... more dates
  },
  projects: [
    {
      id: 'project-1',
      title: 'Machine Learning Study',
      description: 'Notes and flashcards for ML course',
      createdAt: '2025-07-01T10:00:00',
      lastUpdated: '2025-07-29T14:30:00',
      progress: 65, // percentage
      items: {
        books: [1], // book IDs
        notes: [1, 2], // note IDs
        decks: [1], // flashcard deck IDs
      },
    },
    {
      id: 'project-2',
      title: 'React Patterns',
      description: 'Advanced React design patterns',
      createdAt: '2025-07-10T15:20:00',
      lastUpdated: '2025-07-27T14:20:00',
      progress: 40,
      items: {
        books: [2],
        notes: [3],
        decks: [2],
      },
    },
  ],
};

// XP rewards for different actions
const xpRewards = {
  readPage: 2,
  completeBook: 100,
  createNote: 10,
  editNote: 5,
  createFlashcard: 5,
  reviewFlashcard: 1,
  completeStudySession: 20,
  dailyStreak: 15,
  unlockAchievement: 50,
};

// Level thresholds (XP required for each level)
const levelThresholds = [
  0,      // Level 1
  1000,   // Level 2
  2500,   // Level 3
  4500,   // Level 4
  7000,   // Level 5
  10000,  // Level 6
  13500,  // Level 7
  17500,  // Level 8
  22000,  // Level 9
  27000,  // Level 10
  // ... more levels
];

// Calculate level and XP to next level based on total XP
const calculateLevel = (totalXp) => {
  let level = 1;
  let xpToNextLevel = levelThresholds[1];
  
  for (let i = 1; i < levelThresholds.length; i++) {
    if (totalXp >= levelThresholds[i]) {
      level = i + 1;
      xpToNextLevel = levelThresholds[i + 1] || levelThresholds[i] * 1.5;
    } else {
      xpToNextLevel = levelThresholds[i];
      break;
    }
  }
  
  return { level, xpToNextLevel };
};

// Achievement definitions
const achievementDefinitions = [
  {
    id: 'achievement-1',
    title: 'Bookworm',
    description: 'Read for 7 days in a row',
    icon: 'book',
    category: 'reading',
    condition: (stats) => stats.reading.streaks?.reading >= 7,
  },
  {
    id: 'achievement-2',
    title: 'Memory Master',
    description: 'Review 100 flashcards',
    icon: 'brain',
    category: 'flashcards',
    condition: (stats) => stats.flashcards.totalReviews >= 100,
  },
  {
    id: 'achievement-3',
    title: 'Knowledge Explorer',
    description: 'Create 10 notes',
    icon: 'map',
    category: 'notes',
    condition: (stats) => stats.notes.totalNotes >= 10,
  },
  {
    id: 'achievement-4',
    title: 'Speed Reader',
    description: 'Read 50 pages in a day',
    icon: 'zap',
    category: 'reading',
    condition: (stats, dailyStats) => dailyStats?.pagesRead >= 50,
  },
  {
    id: 'achievement-5',
    title: 'Perfect Recall',
    description: 'Get 10 flashcards correct in a row',
    icon: 'check',
    category: 'flashcards',
    condition: (stats, dailyStats) => dailyStats?.flashcardStreak >= 10,
  },
  // ... more achievements
];

const useUserStore = create(
  persist(
    (set, get) => ({
      user: initialUser,
      progress: initialProgress,
      
      // Getters
      getUser: () => get().user,
      
      getProgress: () => get().progress,
      
      getLevel: () => get().progress.level,
      
      getXp: () => ({
        current: get().progress.xp,
        total: get().progress.totalXp,
        toNextLevel: get().progress.xpToNextLevel,
      }),
      
      getStreaks: () => get().progress.streaks,
      
      getAchievements: (category = null) => {
        const { achievements } = get().progress;
        
        if (!category) return achievements;
        
        return achievements.filter(achievement => achievement.category === category);
      },
      
      getUnlockedAchievements: () => {
        const { achievements } = get().progress;
        return achievements.filter(achievement => achievement.unlockedAt !== null);
      },
      
      getStats: (category = null) => {
        const { stats } = get().progress;
        
        if (!category) return stats;
        
        return stats[category] || null;
      },
      
      getActivity: (days = 30) => {
        const { activity } = get().progress;
        const today = new Date();
        const result = {};
        
        // Get activity for the specified number of days
        for (let i = 0; i < days; i++) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateString = date.toISOString().split('T')[0];
          result[dateString] = activity[dateString] || 0;
        }
        
        return result;
      },
      
      // Get XP history over time
      getXpHistory: (days = 30) => {
        // In a real app, this would use actual XP history data
        // For now, we'll generate mock data
        const today = new Date();
        const result = [];
        
        // Generate XP data for each day
        for (let i = days - 1; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateString = date.toISOString().split('T')[0];
          
          // Generate random XP gain for the day (more recent days tend to have more XP)
          const dayFactor = 1 + ((days - i) / days); // Increases as we get closer to today
          const baseXP = Math.floor(Math.random() * 50) * dayFactor;
          const xpGain = Math.max(0, Math.floor(baseXP));
          
          result.push({
            date: dateString,
            xp: xpGain,
          });
        }
        
        // Add cumulative XP
        let cumulativeXP = 0;
        result.forEach(day => {
          cumulativeXP += day.xp;
          day.cumulativeXP = cumulativeXP;
        });
        
        return result;
      },
      
      // Get activity heatmap data
      getActivityHeatmap: (days = 90) => {
        const { activity } = get().progress;
        const today = new Date();
        const result = [];
        
        // Get activity for the specified number of days
        for (let i = days - 1; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateString = date.toISOString().split('T')[0];
          
          // Get activity level (0-5) or generate random activity for missing days
          let activityLevel = activity[dateString];
          
          // If no activity data exists for this date, generate some random data
          // with higher probability of activity on weekdays and recent days
          if (activityLevel === undefined) {
            const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            const recencyFactor = 1 - (i / days); // 0 to 1, higher for more recent days
            
            // Lower probability on weekends and for older dates
            const activityProbability = isWeekend ? 0.3 : 0.7;
            const adjustedProbability = activityProbability * (0.5 + recencyFactor * 0.5);
            
            if (Math.random() < adjustedProbability) {
              // Generate random activity level (1-5)
              activityLevel = Math.floor(Math.random() * 5) + 1;
            } else {
              activityLevel = 0;
            }
          }
          
          result.push({
            date: dateString,
            count: activityLevel,
            level: activityLevel,
          });
        }
        
        return result;
      },
      
      // Get achievement progress statistics
      getAchievementStats: () => {
        const { achievements } = get().progress;
        
        // Count achievements by category
        const categoryCounts = {};
        achievements.forEach(achievement => {
          const category = achievement.category;
          categoryCounts[category] = categoryCounts[category] || { total: 0, unlocked: 0 };
          categoryCounts[category].total += 1;
          
          if (achievement.unlockedAt !== null) {
            categoryCounts[category].unlocked += 1;
          }
        });
        
        // Calculate overall statistics
        const totalAchievements = achievements.length;
        const unlockedAchievements = achievements.filter(a => a.unlockedAt !== null).length;
        const inProgressAchievements = achievements.filter(a => a.unlockedAt === null && a.progress > 0).length;
        const notStartedAchievements = achievements.filter(a => a.unlockedAt === null && a.progress === 0).length;
        
        // Calculate average progress for in-progress achievements
        const inProgressAverage = inProgressAchievements > 0 
          ? achievements
              .filter(a => a.unlockedAt === null && a.progress > 0)
              .reduce((sum, a) => sum + a.progress, 0) / inProgressAchievements
          : 0;
        
        // Calculate category completion percentages
        const categoryCompletion = Object.entries(categoryCounts).map(([category, counts]) => ({
          category,
          total: counts.total,
          unlocked: counts.unlocked,
          percentage: (counts.unlocked / counts.total) * 100,
        }));
        
        // Get recently unlocked achievements
        const recentlyUnlocked = achievements
          .filter(a => a.unlockedAt !== null)
          .sort((a, b) => new Date(b.unlockedAt) - new Date(a.unlockedAt))
          .slice(0, 5)
          .map(a => ({
            id: a.id,
            title: a.title,
            category: a.category,
            unlockedAt: a.unlockedAt,
          }));
        
        return {
          total: totalAchievements,
          unlocked: unlockedAchievements,
          inProgress: inProgressAchievements,
          notStarted: notStartedAchievements,
          completionPercentage: (unlockedAchievements / totalAchievements) * 100,
          inProgressAverage,
          categoryCompletion,
          recentlyUnlocked,
        };
      },
      
      getProjects: () => get().progress.projects,
      
      getProjectById: (id) => {
        const { projects } = get().progress;
        return projects.find(project => project.id === id) || null;
      },
      
      // Actions - User
      updateUser: (userData) => {
        set(state => ({
          user: { ...state.user, ...userData },
        }));
      },
      
      // Actions - XP and Leveling
      addXp: (amount, reason = '') => {
        const { progress } = get();
        const newTotalXp = progress.totalXp + amount;
        const { level, xpToNextLevel } = calculateLevel(newTotalXp);
        
        // Calculate XP within the current level
        const xp = newTotalXp - (levelThresholds[level - 1] || 0);
        
        set(state => ({
          progress: {
            ...state.progress,
            level,
            xp,
            xpToNextLevel,
            totalXp: newTotalXp,
          },
        }));
        
        // Check if leveled up
        if (level > progress.level) {
          // In a real app, you might want to trigger a level-up notification or animation
          console.log(`Leveled up to ${level}!`);
        }
        
        return { newTotalXp, level, xp, xpToNextLevel };
      },
      
      // Actions - Streaks
      updateStreak: (type, value = null) => {
        const { progress } = get();
        
        // If value is null, increment the streak
        const newValue = value !== null ? value : (progress.streaks[type] || 0) + 1;
        
        set(state => ({
          progress: {
            ...state.progress,
            streaks: {
              ...state.progress.streaks,
              [type]: newValue,
            },
          },
        }));
        
        // If streak milestone reached, check for achievements
        get().checkAchievements();
        
        return newValue;
      },
      
      resetStreak: (type) => {
        set(state => ({
          progress: {
            ...state.progress,
            streaks: {
              ...state.progress.streaks,
              [type]: 0,
            },
          },
        }));
      },
      
      // Actions - Achievements
      checkAchievements: () => {
        const { progress } = get();
        const { stats, achievements } = progress;
        
        // Get daily stats (in a real app, this would be calculated from actual daily activity)
        const dailyStats = {
          pagesRead: 35,
          flashcardStreak: 8,
          notesCreated: 2,
        };
        
        // Check each achievement definition
        achievementDefinitions.forEach(definition => {
          // Skip already unlocked achievements
          const existingAchievement = achievements.find(a => a.id === definition.id);
          if (existingAchievement && existingAchievement.unlockedAt !== null) return;
          
          // Check if achievement condition is met
          const isUnlocked = definition.condition(stats, dailyStats);
          
          // If condition is met and achievement not already unlocked, unlock it
          if (isUnlocked) {
            get().unlockAchievement(definition.id);
          }
        });
      },
      
      unlockAchievement: (achievementId) => {
        const { progress } = get();
        const { achievements } = progress;
        
        // Find the achievement
        const achievementIndex = achievements.findIndex(a => a.id === achievementId);
        if (achievementIndex === -1) return false;
        
        // If already unlocked, do nothing
        if (achievements[achievementIndex].unlockedAt !== null) return false;
        
        // Update the achievement
        const updatedAchievements = [...achievements];
        updatedAchievements[achievementIndex] = {
          ...updatedAchievements[achievementIndex],
          unlockedAt: new Date().toISOString(),
          progress: 100,
        };
        
        set(state => ({
          progress: {
            ...state.progress,
            achievements: updatedAchievements,
          },
        }));
        
        // Award XP for unlocking achievement
        get().addXp(xpRewards.unlockAchievement, `Unlocked achievement: ${achievements[achievementIndex].title}`);
        
        return true;
      },
      
      updateAchievementProgress: (achievementId, progressValue) => {
        const { progress } = get();
        const { achievements } = progress;
        
        // Find the achievement
        const achievementIndex = achievements.findIndex(a => a.id === achievementId);
        if (achievementIndex === -1) return false;
        
        // If already unlocked, do nothing
        if (achievements[achievementIndex].unlockedAt !== null) return false;
        
        // Update the achievement progress
        const updatedAchievements = [...achievements];
        updatedAchievements[achievementIndex] = {
          ...updatedAchievements[achievementIndex],
          progress: Math.min(100, progressValue),
        };
        
        // If progress reached 100%, unlock the achievement
        if (progressValue >= 100) {
          updatedAchievements[achievementIndex].unlockedAt = new Date().toISOString();
          
          // Award XP for unlocking achievement
          get().addXp(xpRewards.unlockAchievement, `Unlocked achievement: ${achievements[achievementIndex].title}`);
        }
        
        set(state => ({
          progress: {
            ...state.progress,
            achievements: updatedAchievements,
          },
        }));
        
        return true;
      },
      
      // Actions - Stats
      updateStats: (category, updates) => {
        const { progress } = get();
        
        if (!progress.stats[category]) return false;
        
        set(state => ({
          progress: {
            ...state.progress,
            stats: {
              ...state.progress.stats,
              [category]: {
                ...state.progress.stats[category],
                ...updates,
              },
            },
          },
        }));
        
        // Check for achievements after stats update
        get().checkAchievements();
        
        return true;
      },
      
      // Actions - Activity
      recordActivity: (level = 1) => {
        const today = new Date().toISOString().split('T')[0];
        const { activity } = get().progress;
        
        // Get current activity level for today
        const currentLevel = activity[today] || 0;
        
        // Update activity with the higher level
        const newLevel = Math.max(currentLevel, level);
        
        set(state => ({
          progress: {
            ...state.progress,
            activity: {
              ...state.progress.activity,
              [today]: newLevel,
            },
          },
        }));
        
        return newLevel;
      },
      
      // Actions - Projects
      createProject: (projectData) => {
        const { projects } = get().progress;
        
        const newProject = {
          id: `project-${Date.now()}`,
          createdAt: new Date().toISOString(),
          lastUpdated: new Date().toISOString(),
          progress: 0,
          items: {
            books: [],
            notes: [],
            decks: [],
          },
          ...projectData,
        };
        
        set(state => ({
          progress: {
            ...state.progress,
            projects: [newProject, ...projects],
          },
        }));
        
        return newProject;
      },
      
      updateProject: (id, updates) => {
        const { projects } = get().progress;
        
        // Find the project
        const projectIndex = projects.findIndex(p => p.id === id);
        if (projectIndex === -1) return false;
        
        // Update the project
        const updatedProjects = [...projects];
        updatedProjects[projectIndex] = {
          ...updatedProjects[projectIndex],
          ...updates,
          lastUpdated: new Date().toISOString(),
        };
        
        set(state => ({
          progress: {
            ...state.progress,
            projects: updatedProjects,
          },
        }));
        
        return updatedProjects[projectIndex];
      },
      
      deleteProject: (id) => {
        const { projects } = get().progress;
        
        set(state => ({
          progress: {
            ...state.progress,
            projects: projects.filter(p => p.id !== id),
          },
        }));
        
        return true;
      },
      
      addItemToProject: (projectId, itemType, itemId) => {
        const { projects } = get().progress;
        
        // Find the project
        const project = projects.find(p => p.id === projectId);
        if (!project) return false;
        
        // Check if item type is valid
        if (!project.items[itemType]) return false;
        
        // Check if item already exists in project
        if (project.items[itemType].includes(itemId)) return false;
        
        // Add item to project
        const updatedProjects = projects.map(p => 
          p.id === projectId 
            ? { 
                ...p, 
                items: {
                  ...p.items,
                  [itemType]: [...p.items[itemType], itemId],
                },
                lastUpdated: new Date().toISOString(),
              } 
            : p
        );
        
        set(state => ({
          progress: {
            ...state.progress,
            projects: updatedProjects,
          },
        }));
        
        return true;
      },
      
      removeItemFromProject: (projectId, itemType, itemId) => {
        const { projects } = get().progress;
        
        // Find the project
        const project = projects.find(p => p.id === projectId);
        if (!project) return false;
        
        // Check if item type is valid
        if (!project.items[itemType]) return false;
        
        // Remove item from project
        const updatedProjects = projects.map(p => 
          p.id === projectId 
            ? { 
                ...p, 
                items: {
                  ...p.items,
                  [itemType]: p.items[itemType].filter(id => id !== itemId),
                },
                lastUpdated: new Date().toISOString(),
              } 
            : p
        );
        
        set(state => ({
          progress: {
            ...state.progress,
            projects: updatedProjects,
          },
        }));
        
        return true;
      },
      
      updateProjectProgress: (projectId, progressValue) => {
        return get().updateProject(projectId, { progress: progressValue });
      },
      
      // Reading-related actions
      recordPageRead: (bookId) => {
        // Update reading stats
        get().updateStats('reading', {
          totalPagesRead: get().progress.stats.reading.totalPagesRead + 1,
          lastReadingSession: new Date().toISOString(),
        });
        
        // Update reading streak
        get().updateStreak('reading');
        
        // Record activity
        get().recordActivity(2); // Medium activity level
        
        // Award XP
        get().addXp(xpRewards.readPage, 'Read a page');
        
        return true;
      },
      
      recordBookCompleted: (bookId) => {
        // Update reading stats
        get().updateStats('reading', {
          totalBooksCompleted: get().progress.stats.reading.totalBooksCompleted + 1,
          lastReadingSession: new Date().toISOString(),
        });
        
        // Record high activity
        get().recordActivity(5); // Highest activity level
        
        // Award XP
        get().addXp(xpRewards.completeBook, 'Completed a book');
        
        return true;
      },
      
      // Flashcard-related actions
      recordFlashcardReview: (cardId, isCorrect) => {
        // Update flashcard stats
        get().updateStats('flashcards', {
          totalReviews: get().progress.stats.flashcards.totalReviews + 1,
          correctAnswers: get().progress.stats.flashcards.correctAnswers + (isCorrect ? 1 : 0),
          incorrectAnswers: get().progress.stats.flashcards.incorrectAnswers + (isCorrect ? 0 : 1),
          accuracy: (get().progress.stats.flashcards.correctAnswers + (isCorrect ? 1 : 0)) / 
                   (get().progress.stats.flashcards.totalReviews + 1) * 100,
          lastStudySession: new Date().toISOString(),
        });
        
        // Update flashcard streak
        get().updateStreak('flashcards');
        
        // Record activity
        get().recordActivity(2); // Medium activity level
        
        // Award XP
        get().addXp(xpRewards.reviewFlashcard, 'Reviewed a flashcard');
        
        return true;
      },
      
      recordStudySessionCompleted: (sessionData) => {
        // Update flashcard stats
        get().updateStats('flashcards', {
          totalStudyTime: get().progress.stats.flashcards.totalStudyTime + 
                         (sessionData.duration / 60), // Convert seconds to minutes
          lastStudySession: new Date().toISOString(),
        });
        
        // Record high activity
        get().recordActivity(4); // High activity level
        
        // Award XP
        get().addXp(xpRewards.completeStudySession, 'Completed a study session');
        
        return true;
      },
      
      // Note-related actions
      recordNoteCreated: (noteId) => {
        // Update note stats
        get().updateStats('notes', {
          totalNotes: get().progress.stats.notes.totalNotes + 1,
          lastNoteCreated: new Date().toISOString(),
          lastNoteEdited: new Date().toISOString(),
        });
        
        // Update note streak
        get().updateStreak('notes');
        
        // Record activity
        get().recordActivity(3); // Medium-high activity level
        
        // Award XP
        get().addXp(xpRewards.createNote, 'Created a note');
        
        return true;
      },
      
      recordNoteEdited: (noteId) => {
        // Update note stats
        get().updateStats('notes', {
          lastNoteEdited: new Date().toISOString(),
        });
        
        // Record activity
        get().recordActivity(2); // Medium activity level
        
        // Award XP
        get().addXp(xpRewards.editNote, 'Edited a note');
        
        return true;
      },
      
      recordAnnotationCreated: (annotationId) => {
        // Update note stats
        get().updateStats('notes', {
          totalAnnotations: get().progress.stats.notes.totalAnnotations + 1,
          lastNoteEdited: new Date().toISOString(),
        });
        
        // Record activity
        get().recordActivity(2); // Medium activity level
        
        return true;
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({
          user: {
            ...initialUser,
            isAuthenticated: false,
          },
          progress: initialProgress,
        });
      },
    }),
    {
      name: 'user-storage', // Name for localStorage
      partialize: (state) => ({ 
        user: {
          id: state.user.id,
          name: state.user.name,
          email: state.user.email,
          avatar: state.user.avatar,
          role: state.user.role,
          isAuthenticated: state.user.isAuthenticated,
        },
        progress: state.progress,
      }),
    }
  )
);

export default useUserStore;