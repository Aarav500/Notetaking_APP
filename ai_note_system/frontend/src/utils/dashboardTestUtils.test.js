/**
 * Tests for dashboard test utilities
 */
import dashboardTestUtils from './dashboardTestUtils';
import dashboardUtils from './dashboardUtils';
import useUserStore from '@/store/useUserStore';
import useReadingStore from '@/store/useReadingStore';
import useFlashcardStore from '@/store/useFlashcardStore';
import useNotesStore from '@/store/useNotesStore';
import useVisualizationsStore from '@/store/useVisualizationsStore';
import useDashboardStore from '@/store/useDashboardStore';

/**
 * Test suite for dashboard test utilities
 */
describe('Dashboard Test Utilities', () => {
  // Mock store states
  beforeEach(() => {
    // Reset all stores to their initial state
    useUserStore.getState().resetStore();
    useReadingStore.getState().resetStore();
    useFlashcardStore.getState().resetStore();
    useNotesStore.getState().resetStore();
    useVisualizationsStore.getState().resetStore();
    useDashboardStore.getState().resetStore();
  });

  describe('testUserStatsDisplay', () => {
    it('should return user stats', () => {
      const result = dashboardTestUtils.testUserStatsDisplay();
      
      expect(result.success).toBe(true);
      expect(result.stats).toHaveProperty('level');
      expect(result.stats).toHaveProperty('xp');
      expect(result.stats).toHaveProperty('xpToNextLevel');
      expect(result.stats).toHaveProperty('streaks');
      expect(result.stats).toHaveProperty('xpPercentage');
    });
  });

  describe('testRecentNotesDisplay', () => {
    it('should return recent notes', () => {
      const result = dashboardTestUtils.testRecentNotesDisplay(3);
      
      expect(result.success).toBe(true);
      expect(Array.isArray(result.notes)).toBe(true);
      expect(result.notes.length).toBeLessThanOrEqual(3);
      
      if (result.notes.length > 0) {
        expect(result.notes[0]).toHaveProperty('id');
        expect(result.notes[0]).toHaveProperty('title');
        expect(result.notes[0]).toHaveProperty('excerpt');
        expect(result.notes[0]).toHaveProperty('category');
        expect(result.notes[0]).toHaveProperty('lastEdited');
      }
    });
  });

  describe('testRecentBooksDisplay', () => {
    it('should return recent books', () => {
      const result = dashboardTestUtils.testRecentBooksDisplay(3);
      
      expect(result.success).toBe(true);
      expect(Array.isArray(result.books)).toBe(true);
      expect(result.books.length).toBeLessThanOrEqual(3);
      
      if (result.books.length > 0) {
        expect(result.books[0]).toHaveProperty('id');
        expect(result.books[0]).toHaveProperty('title');
        expect(result.books[0]).toHaveProperty('author');
        expect(result.books[0]).toHaveProperty('coverImage');
        expect(result.books[0]).toHaveProperty('progress');
      }
    });
  });

  describe('testProgressHeatmapDisplay', () => {
    it('should return activity data for heatmap', () => {
      const result = dashboardTestUtils.testProgressHeatmapDisplay(30);
      
      expect(result.success).toBe(true);
      expect(result.activityData).toBeDefined();
      expect(result.maxActivity).toBeDefined();
      expect(result.daysWithActivity).toBeDefined();
      expect(result.activityPercentage).toBeDefined();
      
      // Test data transformation with dashboard utils
      const heatmapData = dashboardUtils.generateHeatmapData(
        Object.entries(result.activityData).map(([date, count]) => ({ date, count }))
      );
      
      expect(Array.isArray(heatmapData)).toBe(true);
      if (heatmapData.length > 0) {
        expect(heatmapData[0]).toHaveProperty('date');
        expect(heatmapData[0]).toHaveProperty('count');
        expect(heatmapData[0]).toHaveProperty('color');
      }
    });
  });

  describe('testKnowledgeGraphDisplay', () => {
    it('should return knowledge graph data', () => {
      const result = dashboardTestUtils.testKnowledgeGraphDisplay();
      
      expect(result.success).toBe(true);
      expect(result.nodeCount).toBeDefined();
      expect(result.edgeCount).toBeDefined();
      
      // Graph might be null if no knowledge graphs exist
      if (result.graph) {
        expect(result.graph).toHaveProperty('id');
        expect(result.graph).toHaveProperty('title');
        expect(result.graph).toHaveProperty('type', 'knowledge_graph');
      }
    });
  });

  describe('testFlashcardStatsDisplay', () => {
    it('should return flashcard statistics', () => {
      const result = dashboardTestUtils.testFlashcardStatsDisplay();
      
      expect(result.success).toBe(true);
      expect(result.stats).toHaveProperty('totalCards');
      expect(result.stats).toHaveProperty('cardsStudied');
      expect(result.stats).toHaveProperty('cardsLearned');
      expect(result.stats).toHaveProperty('accuracy');
      expect(result.stats).toHaveProperty('completionRate');
      
      // Test data transformation with dashboard utils
      const derivedStats = dashboardUtils.calculateDerivedStats(result.stats);
      expect(derivedStats).toHaveProperty('accuracy');
      expect(derivedStats).toHaveProperty('completionRate');
    });
  });

  describe('testReadingStatsDisplay', () => {
    it('should return reading statistics', () => {
      const result = dashboardTestUtils.testReadingStatsDisplay();
      
      expect(result.success).toBe(true);
      expect(result.stats).toHaveProperty('totalBooks');
      expect(result.stats).toHaveProperty('booksStarted');
      expect(result.stats).toHaveProperty('booksCompleted');
      expect(result.stats).toHaveProperty('totalPages');
      expect(result.stats).toHaveProperty('pagesRead');
      expect(result.stats).toHaveProperty('readingStreak');
    });
  });

  describe('testProjectsDisplay', () => {
    it('should return projects data', () => {
      const result = dashboardTestUtils.testProjectsDisplay();
      
      expect(result.success).toBe(true);
      expect(Array.isArray(result.projects)).toBe(true);
      
      if (result.projects.length > 0) {
        expect(result.projects[0]).toHaveProperty('id');
        expect(result.projects[0]).toHaveProperty('title');
        expect(result.projects[0]).toHaveProperty('description');
        expect(result.projects[0]).toHaveProperty('progress');
        expect(result.projects[0]).toHaveProperty('itemCounts');
      }
    });
  });

  describe('testAchievementsDisplay', () => {
    it('should return achievements data', () => {
      const result = dashboardTestUtils.testAchievementsDisplay();
      
      expect(result.success).toBe(true);
      expect(result.achievements).toHaveProperty('unlocked');
      expect(result.achievements).toHaveProperty('inProgress');
      expect(Array.isArray(result.achievements.unlocked)).toBe(true);
      expect(Array.isArray(result.achievements.inProgress)).toBe(true);
    });
  });

  describe('testAllDashboardComponents', () => {
    it('should test all dashboard components', () => {
      const result = dashboardTestUtils.testAllDashboardComponents();
      
      expect(result).toHaveProperty('userStats');
      expect(result).toHaveProperty('recentNotes');
      expect(result).toHaveProperty('recentBooks');
      expect(result).toHaveProperty('progressHeatmap');
      expect(result).toHaveProperty('knowledgeGraph');
      expect(result).toHaveProperty('flashcardStats');
      expect(result).toHaveProperty('readingStats');
      expect(result).toHaveProperty('projects');
      expect(result).toHaveProperty('achievements');
      expect(result).toHaveProperty('overallSuccess');
      expect(result).toHaveProperty('successRate');
      
      // All individual tests should be successful
      expect(result.userStats.success).toBe(true);
      expect(result.recentNotes.success).toBe(true);
      expect(result.recentBooks.success).toBe(true);
      expect(result.progressHeatmap.success).toBe(true);
      expect(result.knowledgeGraph.success).toBe(true);
      expect(result.flashcardStats.success).toBe(true);
      expect(result.readingStats.success).toBe(true);
      expect(result.projects.success).toBe(true);
      expect(result.achievements.success).toBe(true);
    });
  });

  describe('verifyComponentRendering', () => {
    it('should verify component rendering', () => {
      // Mock component with props
      const mockComponent = {
        props: {
          title: 'Dashboard',
          data: [1, 2, 3],
          onAction: jest.fn(),
        },
      };
      
      const expectedProps = {
        title: 'Dashboard',
        data: [1, 2, 3],
      };
      
      const result = dashboardTestUtils.verifyComponentRendering(mockComponent, expectedProps);
      
      expect(result.success).toBe(true);
      expect(result.propsMatch).toBe(true);
      expect(result.renderedProps).toEqual(mockComponent.props);
    });
    
    it('should handle missing component', () => {
      const result = dashboardTestUtils.verifyComponentRendering(null, {});
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('Component is undefined');
    });
  });
});

/**
 * Test suite for dashboard utilities
 */
describe('Dashboard Utilities', () => {
  describe('formatDate', () => {
    it('should format date strings correctly', () => {
      const date = '2025-07-30';
      
      expect(dashboardUtils.formatDate(date, 'short')).toBeDefined();
      expect(dashboardUtils.formatDate(date, 'medium')).toBeDefined();
      expect(dashboardUtils.formatDate(date, 'long')).toBeDefined();
      expect(dashboardUtils.formatDate(date, 'month')).toBeDefined();
      expect(dashboardUtils.formatDate(date, 'monthYear')).toBeDefined();
      expect(dashboardUtils.formatDate(date, 'weekday')).toBeDefined();
    });
  });
  
  describe('formatNumber', () => {
    it('should format numbers with appropriate units', () => {
      expect(dashboardUtils.formatNumber(0)).toBe('0');
      expect(dashboardUtils.formatNumber(999)).toBe('999');
      expect(dashboardUtils.formatNumber(1000)).toBe('1K');
      expect(dashboardUtils.formatNumber(1500)).toBe('1.5K');
      expect(dashboardUtils.formatNumber(1000000)).toBe('1M');
      expect(dashboardUtils.formatNumber(-1500)).toBe('-1.5K');
    });
  });
  
  describe('formatDuration', () => {
    it('should format durations correctly', () => {
      expect(dashboardUtils.formatDuration(0)).toBe('0 minutes');
      expect(dashboardUtils.formatDuration(30)).toBe('30 seconds');
      expect(dashboardUtils.formatDuration(90)).toBe('1 minute 30 seconds');
      expect(dashboardUtils.formatDuration(3600)).toBe('1 hour 0 minute');
      expect(dashboardUtils.formatDuration(3661)).toBe('1 hour 1 minute');
      
      // Short format
      expect(dashboardUtils.formatDuration(0, true)).toBe('0m');
      expect(dashboardUtils.formatDuration(30, true)).toBe('30s');
      expect(dashboardUtils.formatDuration(90, true)).toBe('1m 30s');
      expect(dashboardUtils.formatDuration(3600, true)).toBe('1h 0m');
    });
  });
  
  describe('formatPercentage', () => {
    it('should format percentages correctly', () => {
      expect(dashboardUtils.formatPercentage(0)).toBe('0%');
      expect(dashboardUtils.formatPercentage(50)).toBe('50%');
      expect(dashboardUtils.formatPercentage(99.9)).toBe('99.9%');
      expect(dashboardUtils.formatPercentage(100)).toBe('100%');
      expect(dashboardUtils.formatPercentage(33.333, 2)).toBe('33.33%');
    });
  });
  
  describe('calculateDerivedStats', () => {
    it('should calculate derived statistics', () => {
      const data = {
        total: 100,
        completed: 75,
        correct: 80,
        incorrect: 20,
        sum: 500,
        count: 10,
      };
      
      const result = dashboardUtils.calculateDerivedStats(data);
      
      expect(result.completionRate).toBe(75);
      expect(result.accuracy).toBe(80);
      expect(result.average).toBe(50);
    });
  });
  
  describe('generateTimeSeriesChartData', () => {
    it('should generate time series chart data', () => {
      const data = [
        { date: '2025-07-01', value: 10, otherValue: 5 },
        { date: '2025-07-02', value: 15, otherValue: 8 },
        { date: '2025-07-03', value: 12, otherValue: 6 },
      ];
      
      const result = dashboardUtils.generateTimeSeriesChartData(data, {
        valueFields: ['value', 'otherValue'],
        labels: ['Value', 'Other Value'],
      });
      
      expect(result.labels.length).toBe(3);
      expect(result.datasets.length).toBe(2);
      expect(result.datasets[0].label).toBe('Value');
      expect(result.datasets[1].label).toBe('Other Value');
      expect(result.datasets[0].data).toEqual([10, 15, 12]);
      expect(result.datasets[1].data).toEqual([5, 8, 6]);
    });
  });
  
  describe('generateHeatmapData', () => {
    it('should generate heatmap data', () => {
      const data = [
        { date: '2025-07-01', count: 0 },
        { date: '2025-07-02', count: 2 },
        { date: '2025-07-03', count: 5 },
      ];
      
      const result = dashboardUtils.generateHeatmapData(data);
      
      expect(result.length).toBe(3);
      expect(result[0].date).toBe('2025-07-01');
      expect(result[0].count).toBe(0);
      expect(result[0].color).toBe('#ebedf0'); // No activity color
      
      expect(result[1].count).toBe(2);
      expect(result[1].color).not.toBe('#ebedf0'); // Should have activity color
      
      expect(result[2].count).toBe(5);
      expect(result[2].color).not.toBe('#ebedf0'); // Should have activity color
    });
  });
  
  describe('calculateStreakStats', () => {
    it('should calculate streak statistics', () => {
      const today = new Date().toISOString().split('T')[0];
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      const twoDaysAgo = new Date(Date.now() - 2 * 86400000).toISOString().split('T')[0];
      
      const data = [
        { date: twoDaysAgo, count: 1 },
        { date: yesterday, count: 2 },
        { date: today, count: 3 },
      ];
      
      const result = dashboardUtils.calculateStreakStats(data);
      
      expect(result.currentStreak).toBe(3);
      expect(result.longestStreak).toBe(3);
      expect(result.totalDays).toBe(3);
    });
    
    it('should handle broken streaks', () => {
      const today = new Date().toISOString().split('T')[0];
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      const threeDaysAgo = new Date(Date.now() - 3 * 86400000).toISOString().split('T')[0];
      
      const data = [
        { date: threeDaysAgo, count: 1 },
        { date: yesterday, count: 2 },
        { date: today, count: 3 },
      ];
      
      const result = dashboardUtils.calculateStreakStats(data);
      
      expect(result.currentStreak).toBe(2); // Today and yesterday
      expect(result.longestStreak).toBe(2);
      expect(result.totalDays).toBe(3);
    });
  });
});