import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Mock data for initial books/documents
const initialBooks = [
  {
    id: 1,
    title: 'Machine Learning Fundamentals',
    author: 'Alex Johnson',
    coverImage: 'https://via.placeholder.com/150x200?text=ML+Fundamentals',
    totalPages: 245,
    currentPage: 78,
    lastRead: '2025-07-28T14:30:00',
    progress: 31.8, // percentage
    format: 'pdf',
    path: '/documents/machine-learning-fundamentals.pdf',
    annotations: [
      {
        id: 'anno-1',
        type: 'highlight',
        content: 'Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from data.',
        color: 'yellow',
        page: 12,
        position: { x: 120, y: 350, width: 400, height: 20 },
        createdAt: '2025-07-20T10:15:00',
      },
      {
        id: 'anno-2',
        type: 'note',
        content: 'Remember to review the different types of neural networks',
        page: 45,
        position: { x: 200, y: 420, width: 300, height: 100 },
        createdAt: '2025-07-22T16:30:00',
      },
      {
        id: 'anno-3',
        type: 'highlight',
        content: 'Deep learning is a subset of machine learning that uses neural networks with many layers.',
        color: 'green',
        page: 78,
        position: { x: 150, y: 280, width: 380, height: 20 },
        createdAt: '2025-07-28T14:25:00',
      },
    ],
    bookmarks: [12, 45, 78, 120],
  },
  {
    id: 2,
    title: 'Advanced React Patterns',
    author: 'Sarah Chen',
    coverImage: 'https://via.placeholder.com/150x200?text=React+Patterns',
    totalPages: 189,
    currentPage: 65,
    lastRead: '2025-07-25T09:45:00',
    progress: 34.4, // percentage
    format: 'pdf',
    path: '/documents/advanced-react-patterns.pdf',
    annotations: [
      {
        id: 'anno-4',
        type: 'highlight',
        content: 'The Compound Component pattern allows you to create components that share state implicitly.',
        color: 'blue',
        page: 34,
        position: { x: 100, y: 250, width: 420, height: 20 },
        createdAt: '2025-07-23T11:20:00',
      },
      {
        id: 'anno-5',
        type: 'note',
        content: 'Try implementing this pattern in the next project',
        page: 35,
        position: { x: 150, y: 300, width: 300, height: 80 },
        createdAt: '2025-07-23T11:25:00',
      },
    ],
    bookmarks: [34, 65, 102],
  },
  {
    id: 3,
    title: 'Data Structures and Algorithms',
    author: 'Michael Roberts',
    coverImage: 'https://via.placeholder.com/150x200?text=DSA',
    totalPages: 312,
    currentPage: 145,
    lastRead: '2025-07-26T20:15:00',
    progress: 46.5, // percentage
    format: 'pdf',
    path: '/documents/data-structures-algorithms.pdf',
    annotations: [
      {
        id: 'anno-6',
        type: 'highlight',
        content: 'A binary search tree is a binary tree where each node has at most two children, and all nodes in the left subtree have values less than the node\'s value.',
        color: 'yellow',
        page: 87,
        position: { x: 120, y: 350, width: 400, height: 40 },
        createdAt: '2025-07-24T14:10:00',
      },
    ],
    bookmarks: [87, 145, 200],
  },
];

const useReadingStore = create(
  persist(
    (set, get) => ({
      books: initialBooks,
      activeBookId: null,
      viewMode: 'single', // 'single' or 'split'
      splitRatio: 0.5, // ratio for split screen (0.5 = 50% for each side)
      zoom: 1.0,
      isFullscreen: false,
      showAnnotations: true,
      showBookmarks: true,
      
      // Getters
      getActiveBook: () => {
        const { books, activeBookId } = get();
        return books.find(book => book.id === activeBookId) || null;
      },
      
      getBookById: (id) => {
        const { books } = get();
        return books.find(book => book.id === id) || null;
      },
      
      getRecentBooks: (limit = 5) => {
        const { books } = get();
        return [...books]
          .sort((a, b) => new Date(b.lastRead) - new Date(a.lastRead))
          .slice(0, limit);
      },
      
      getAnnotationsForBook: (bookId) => {
        const book = get().getBookById(bookId);
        return book ? book.annotations : [];
      },
      
      getAnnotationsForCurrentPage: () => {
        const book = get().getActiveBook();
        if (!book) return [];
        
        return book.annotations.filter(anno => anno.page === book.currentPage);
      },
      
      getBookmarksForBook: (bookId) => {
        const book = get().getBookById(bookId);
        return book ? book.bookmarks : [];
      },
      
      isCurrentPageBookmarked: () => {
        const book = get().getActiveBook();
        if (!book) return false;
        
        return book.bookmarks.includes(book.currentPage);
      },
      
      // Actions
      setActiveBook: (bookId) => set({ activeBookId: bookId }),
      
      addBook: (bookData) => {
        const { books } = get();
        const newBook = {
          id: Date.now(),
          currentPage: 1,
          lastRead: new Date().toISOString(),
          progress: 0,
          annotations: [],
          bookmarks: [],
          ...bookData,
        };
        
        set({ 
          books: [newBook, ...books],
          activeBookId: newBook.id
        });
        
        return newBook;
      },
      
      updateBook: (id, bookData) => {
        const { books } = get();
        const updatedBooks = books.map(book => 
          book.id === id ? { ...book, ...bookData } : book
        );
        
        set({ books: updatedBooks });
        return updatedBooks.find(book => book.id === id);
      },
      
      removeBook: (id) => {
        const { books, activeBookId } = get();
        const updatedBooks = books.filter(book => book.id !== id);
        
        // If the active book is being removed, clear the active book
        const newActiveBookId = activeBookId === id ? null : activeBookId;
        
        set({ 
          books: updatedBooks,
          activeBookId: newActiveBookId
        });
      },
      
      // Page navigation
      goToPage: (page) => {
        const { activeBookId, books } = get();
        if (!activeBookId) return;
        
        const book = books.find(book => book.id === activeBookId);
        if (!book) return;
        
        // Ensure page is within valid range
        const validPage = Math.max(1, Math.min(page, book.totalPages));
        
        const updatedBooks = books.map(b => 
          b.id === activeBookId 
            ? { 
                ...b, 
                currentPage: validPage,
                lastRead: new Date().toISOString(),
                progress: (validPage / b.totalPages) * 100
              } 
            : b
        );
        
        set({ books: updatedBooks });
        return validPage;
      },
      
      nextPage: () => {
        const book = get().getActiveBook();
        if (!book) return;
        
        return get().goToPage(book.currentPage + 1);
      },
      
      previousPage: () => {
        const book = get().getActiveBook();
        if (!book) return;
        
        return get().goToPage(book.currentPage - 1);
      },
      
      // Annotations
      addAnnotation: (bookId, annotation) => {
        const { books } = get();
        const book = books.find(book => book.id === bookId);
        if (!book) return null;
        
        const newAnnotation = {
          id: `anno-${Date.now()}`,
          createdAt: new Date().toISOString(),
          ...annotation,
        };
        
        const updatedBooks = books.map(b => 
          b.id === bookId 
            ? { 
                ...b, 
                annotations: [...b.annotations, newAnnotation],
                lastRead: new Date().toISOString(),
              } 
            : b
        );
        
        set({ books: updatedBooks });
        return newAnnotation;
      },
      
      updateAnnotation: (bookId, annotationId, updates) => {
        const { books } = get();
        const book = books.find(book => book.id === bookId);
        if (!book) return null;
        
        const updatedAnnotations = book.annotations.map(anno => 
          anno.id === annotationId ? { ...anno, ...updates } : anno
        );
        
        const updatedBooks = books.map(b => 
          b.id === bookId 
            ? { 
                ...b, 
                annotations: updatedAnnotations,
                lastRead: new Date().toISOString(),
              } 
            : b
        );
        
        set({ books: updatedBooks });
        return updatedAnnotations.find(anno => anno.id === annotationId);
      },
      
      removeAnnotation: (bookId, annotationId) => {
        const { books } = get();
        const book = books.find(book => book.id === bookId);
        if (!book) return false;
        
        const updatedAnnotations = book.annotations.filter(anno => anno.id !== annotationId);
        
        const updatedBooks = books.map(b => 
          b.id === bookId 
            ? { 
                ...b, 
                annotations: updatedAnnotations,
                lastRead: new Date().toISOString(),
              } 
            : b
        );
        
        set({ books: updatedBooks });
        return true;
      },
      
      // Bookmarks
      toggleBookmark: (bookId, page) => {
        const { books } = get();
        const book = books.find(book => book.id === bookId);
        if (!book) return false;
        
        let updatedBookmarks;
        if (book.bookmarks.includes(page)) {
          // Remove bookmark
          updatedBookmarks = book.bookmarks.filter(p => p !== page);
        } else {
          // Add bookmark
          updatedBookmarks = [...book.bookmarks, page].sort((a, b) => a - b);
        }
        
        const updatedBooks = books.map(b => 
          b.id === bookId 
            ? { 
                ...b, 
                bookmarks: updatedBookmarks,
                lastRead: new Date().toISOString(),
              } 
            : b
        );
        
        set({ books: updatedBooks });
        return !book.bookmarks.includes(page);
      },
      
      toggleCurrentPageBookmark: () => {
        const book = get().getActiveBook();
        if (!book) return false;
        
        return get().toggleBookmark(book.id, book.currentPage);
      },
      
      // View settings
      setViewMode: (mode) => {
        if (mode !== 'single' && mode !== 'split') return;
        set({ viewMode: mode });
      },
      
      setSplitRatio: (ratio) => {
        // Ensure ratio is between 0.2 and 0.8
        const validRatio = Math.max(0.2, Math.min(ratio, 0.8));
        set({ splitRatio: validRatio });
      },
      
      setZoom: (zoom) => {
        // Ensure zoom is between 0.5 and 3.0
        const validZoom = Math.max(0.5, Math.min(zoom, 3.0));
        set({ zoom: validZoom });
      },
      
      toggleFullscreen: () => {
        set(state => ({ isFullscreen: !state.isFullscreen }));
      },
      
      toggleAnnotationsVisibility: () => {
        set(state => ({ showAnnotations: !state.showAnnotations }));
      },
      
      toggleBookmarksVisibility: () => {
        set(state => ({ showBookmarks: !state.showBookmarks }));
      },
      
      // Reading statistics
      getReadingStats: () => {
        const { books } = get();
    
        const totalBooks = books.length;
        const booksStarted = books.filter(book => book.progress > 0).length;
        const booksCompleted = books.filter(book => book.progress >= 99.9).length;
    
        const totalPages = books.reduce((sum, book) => sum + book.totalPages, 0);
        const pagesRead = books.reduce((sum, book) => sum + Math.floor(book.totalPages * (book.progress / 100)), 0);
    
        const totalAnnotations = books.reduce((sum, book) => sum + book.annotations.length, 0);
        const totalBookmarks = books.reduce((sum, book) => sum + book.bookmarks.length, 0);
    
        // Calculate reading streak (days in a row with reading activity)
        // In a real app, this would use actual timestamps and more sophisticated logic
        const readingStreak = 7; // Mock value
    
        // Calculate average reading speed (pages per hour)
        // In a real app, this would be calculated from actual reading sessions
        const averageReadingSpeed = 25; // Mock value
    
        // Calculate total reading time in minutes (estimated)
        const totalReadingTime = pagesRead * 2; // Assuming 2 minutes per page on average
    
        return {
          totalBooks,
          booksStarted,
          booksCompleted,
          totalPages,
          pagesRead,
          totalAnnotations,
          totalBookmarks,
          readingStreak,
          completionRate: totalBooks > 0 ? (booksCompleted / totalBooks) * 100 : 0,
          averageReadingSpeed,
          totalReadingTime,
          lastReadingSession: books.length > 0 
            ? books.sort((a, b) => new Date(b.lastRead) - new Date(a.lastRead))[0].lastRead
            : null,
        };
      },
  
      // Get reading progress timeline data
      getReadingProgressTimeline: (days = 30) => {
        const { books } = get();
    
        // Create a map of dates to pages read
        const progressMap = {};
        const today = new Date();
    
        // Initialize all dates in the range with 0 pages
        for (let i = 0; i < days; i++) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateString = date.toISOString().split('T')[0];
          progressMap[dateString] = 0;
        }
    
        // In a real app, this would use actual reading history
        // For now, we'll generate some mock data
    
        // Simulate some reading activity over the past days
        const mockReadingDays = Math.floor(days * 0.7); // Read on 70% of days
        for (let i = 0; i < mockReadingDays; i++) {
          const randomDay = Math.floor(Math.random() * days);
          const date = new Date(today);
          date.setDate(date.getDate() - randomDay);
          const dateString = date.toISOString().split('T')[0];
      
          // Random pages read between 5 and 30
          progressMap[dateString] += Math.floor(Math.random() * 25) + 5;
        }
    
        // Convert to array format for charts
        const timeline = Object.entries(progressMap).map(([date, pages]) => ({
          date,
          pagesRead: pages,
        })).sort((a, b) => new Date(a.date) - new Date(b.date));
    
        return timeline;
      },
  
      // Get book categories statistics
      getBookCategoriesStats: () => {
        const { books } = get();
    
        // In a real app, books would have categories
        // For now, we'll assign mock categories based on titles
    
        const categories = {};
    
        books.forEach(book => {
          let category = 'Uncategorized';
      
          // Assign category based on title keywords (mock logic)
          if (book.title.toLowerCase().includes('machine learning') || 
              book.title.toLowerCase().includes('ai') ||
              book.title.toLowerCase().includes('data')) {
            category = 'Computer Science';
          } else if (book.title.toLowerCase().includes('react') || 
                    book.title.toLowerCase().includes('javascript') ||
                    book.title.toLowerCase().includes('programming')) {
            category = 'Programming';
          } else if (book.title.toLowerCase().includes('physics') || 
                    book.title.toLowerCase().includes('science') ||
                    book.title.toLowerCase().includes('quantum')) {
            category = 'Science';
          }
      
          // Increment category count
          categories[category] = (categories[category] || 0) + 1;
        });
    
        // Convert to array format for charts
        const categoriesArray = Object.entries(categories).map(([name, count]) => ({
          name,
          count,
          percentage: (count / books.length) * 100,
        }));
    
        return categoriesArray;
      },
      
      // Import/Export
      importBooks: (importedBooks) => {
        const { books } = get();
        const existingIds = new Set(books.map(book => book.id));
        
        const newBooks = importedBooks.filter(book => !existingIds.has(book.id));
        const mergedBooks = [...books, ...newBooks];
        
        set({ books: mergedBooks });
        return newBooks.length;
      },
      
      exportBooks: () => {
        return get().books;
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({ 
          books: [],
          activeBookId: null,
          viewMode: 'single',
          splitRatio: 0.5,
          zoom: 1.0,
          isFullscreen: false,
          showAnnotations: true,
          showBookmarks: true,
        });
      }
    }),
    {
      name: 'reading-storage', // Name for localStorage
      partialize: (state) => ({ 
        books: state.books,
        activeBookId: state.activeBookId,
        viewMode: state.viewMode,
        splitRatio: state.splitRatio,
        showAnnotations: state.showAnnotations,
        showBookmarks: state.showBookmarks,
      }), // Only persist necessary state
    }
  )
);

export default useReadingStore;