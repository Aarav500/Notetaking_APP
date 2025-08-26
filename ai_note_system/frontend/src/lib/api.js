import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error cases
    if (error.response) {
      // Server responded with a status code outside of 2xx range
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth-token');
          // In a real app, you might use a store action here
          // store.dispatch(logout());
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden
          console.error('Access forbidden:', error.response.data);
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.response.data);
          break;
        case 500:
          // Server error
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.data);
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
const endpoints = {
  // Auth endpoints
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
    resetPassword: (token, newPassword) => api.post('/auth/reset-password', { token, newPassword }),
    verifyEmail: (token) => api.post('/auth/verify-email', { token }),
    refreshToken: () => api.post('/auth/refresh-token'),
    logout: () => api.post('/auth/logout'),
    me: () => api.get('/auth/me'),
  },
  
  // User endpoints
  user: {
    getProfile: () => api.get('/user/profile'),
    updateProfile: (userData) => api.put('/user/profile', userData),
    updatePassword: (passwordData) => api.put('/user/password', passwordData),
    updateAvatar: (formData) => api.put('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
    deleteAccount: () => api.delete('/user/account'),
  },
  
  // Notes endpoints
  notes: {
    getAll: (params) => api.get('/notes', { params }),
    getById: (id) => api.get(`/notes/${id}`),
    create: (noteData) => api.post('/notes', noteData),
    update: (id, noteData) => api.put(`/notes/${id}`, noteData),
    delete: (id) => api.delete(`/notes/${id}`),
    bulkDelete: (ids) => api.post('/notes/bulk-delete', { ids }),
    addTag: (id, tag) => api.post(`/notes/${id}/tags`, { tag }),
    removeTag: (id, tag) => api.delete(`/notes/${id}/tags/${tag}`),
    bulkAddTag: (ids, tag) => api.post('/notes/bulk-add-tag', { ids, tag }),
    bulkRemoveTag: (ids, tag) => api.post('/notes/bulk-remove-tag', { ids, tag }),
    export: (format = 'json') => api.get('/notes/export', { 
      params: { format },
      responseType: 'blob',
    }),
    import: (formData) => api.post('/notes/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
  },
  
  // Visualizations endpoints
  visualizations: {
    getAll: (params) => api.get('/visualizations', { params }),
    getById: (id) => api.get(`/visualizations/${id}`),
    getByNoteId: (noteId) => api.get('/visualizations', { params: { noteId } }),
    create: (vizData) => api.post('/visualizations', vizData),
    update: (id, vizData) => api.put(`/visualizations/${id}`, vizData),
    delete: (id) => api.delete(`/visualizations/${id}`),
    bulkDelete: (ids) => api.post('/visualizations/bulk-delete', { ids }),
    generate: (noteId, type, title) => api.post('/visualizations/generate', { noteId, type, title }),
    export: (id, format = 'png') => api.get(`/visualizations/${id}/export`, { 
      params: { format },
      responseType: 'blob',
    }),
  },
  
  // Processing endpoints
  processing: {
    processText: (text, options) => api.post('/processing/text', { text, options }),
    processPdf: (formData, options) => api.post('/processing/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: options,
    }),
    processImage: (formData, options) => api.post('/processing/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: options,
    }),
    processYoutube: (youtubeUrl, options) => api.post('/processing/youtube', { youtubeUrl, options }),
    processUrl: (url, options) => api.post('/processing/url', { url, options }),
    processVoice: (formData, options) => api.post('/processing/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: options,
    }),
  },
  
  // Reading endpoints
  reading: {
    // Books/Documents
    getBooks: (params) => api.get('/reading/books', { params }),
    getBookById: (id) => api.get(`/reading/books/${id}`),
    uploadBook: (formData) => api.post('/reading/books/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
    updateBook: (id, bookData) => api.put(`/reading/books/${id}`, bookData),
    deleteBook: (id) => api.delete(`/reading/books/${id}`),
    
    // PDF Operations
    getPdfContent: (id, page) => api.get(`/reading/books/${id}/content`, { params: { page } }),
    getPdfThumbnail: (id, page) => api.get(`/reading/books/${id}/thumbnail/${page}`, { responseType: 'blob' }),
    getPdfToc: (id) => api.get(`/reading/books/${id}/toc`),
    
    // Annotations
    getAnnotations: (bookId, page = null) => api.get(`/reading/books/${bookId}/annotations`, { 
      params: { page } 
    }),
    createAnnotation: (bookId, annotationData) => api.post(`/reading/books/${bookId}/annotations`, annotationData),
    updateAnnotation: (bookId, annotationId, annotationData) => api.put(
      `/reading/books/${bookId}/annotations/${annotationId}`, 
      annotationData
    ),
    deleteAnnotation: (bookId, annotationId) => api.delete(`/reading/books/${bookId}/annotations/${annotationId}`),
    
    // Bookmarks
    getBookmarks: (bookId) => api.get(`/reading/books/${bookId}/bookmarks`),
    addBookmark: (bookId, page) => api.post(`/reading/books/${bookId}/bookmarks`, { page }),
    removeBookmark: (bookId, page) => api.delete(`/reading/books/${bookId}/bookmarks/${page}`),
    
    // Reading Progress
    updateReadingProgress: (bookId, progressData) => api.put(`/reading/books/${bookId}/progress`, progressData),
    getReadingStats: () => api.get('/reading/stats'),
  },
  
  // Flashcard endpoints
  flashcards: {
    // Cards
    getCards: (params) => api.get('/flashcards/cards', { params }),
    getCardById: (id) => api.get(`/flashcards/cards/${id}`),
    createCard: (cardData) => api.post('/flashcards/cards', cardData),
    updateCard: (id, cardData) => api.put(`/flashcards/cards/${id}`, cardData),
    deleteCard: (id) => api.delete(`/flashcards/cards/${id}`),
    reviewCard: (id, reviewData) => api.post(`/flashcards/cards/${id}/review`, reviewData),
    
    // Decks
    getDecks: (params) => api.get('/flashcards/decks', { params }),
    getDeckById: (id) => api.get(`/flashcards/decks/${id}`),
    createDeck: (deckData) => api.post('/flashcards/decks', deckData),
    updateDeck: (id, deckData) => api.put(`/flashcards/decks/${id}`, deckData),
    deleteDeck: (id) => api.delete(`/flashcards/decks/${id}`),
    
    // Deck-Card Operations
    getCardsInDeck: (deckId) => api.get(`/flashcards/decks/${deckId}/cards`),
    addCardToDeck: (deckId, cardId) => api.post(`/flashcards/decks/${deckId}/cards`, { cardId }),
    removeCardFromDeck: (deckId, cardId) => api.delete(`/flashcards/decks/${deckId}/cards/${cardId}`),
    
    // Study Sessions
    getStudySessions: (params) => api.get('/flashcards/study-sessions', { params }),
    startStudySession: (deckId) => api.post('/flashcards/study-sessions/start', { deckId }),
    endStudySession: (sessionData) => api.post('/flashcards/study-sessions/end', sessionData),
    
    // Due Cards
    getDueCards: (deckId = null) => api.get('/flashcards/due-cards', { params: { deckId } }),
    
    // Stats
    getFlashcardStats: () => api.get('/flashcards/stats'),
  },
  
  // Progress tracking endpoints
  progress: {
    // User Progress
    getProgress: () => api.get('/progress'),
    updateProgress: (progressData) => api.put('/progress', progressData),
    
    // XP and Leveling
    getXp: () => api.get('/progress/xp'),
    addXp: (amount, reason) => api.post('/progress/xp', { amount, reason }),
    
    // Achievements
    getAchievements: (category = null) => api.get('/progress/achievements', { params: { category } }),
    getUnlockedAchievements: () => api.get('/progress/achievements/unlocked'),
    unlockAchievement: (achievementId) => api.post(`/progress/achievements/${achievementId}/unlock`),
    updateAchievementProgress: (achievementId, progress) => api.put(
      `/progress/achievements/${achievementId}/progress`, 
      { progress }
    ),
    
    // Streaks
    getStreaks: () => api.get('/progress/streaks'),
    updateStreak: (type, value) => api.put('/progress/streaks', { type, value }),
    resetStreak: (type) => api.delete(`/progress/streaks/${type}`),
    
    // Activity
    getActivity: (days = 30) => api.get('/progress/activity', { params: { days } }),
    recordActivity: (level) => api.post('/progress/activity', { level }),
    
    // Projects
    getProjects: () => api.get('/progress/projects'),
    getProjectById: (id) => api.get(`/progress/projects/${id}`),
    createProject: (projectData) => api.post('/progress/projects', projectData),
    updateProject: (id, projectData) => api.put(`/progress/projects/${id}`, projectData),
    deleteProject: (id) => api.delete(`/progress/projects/${id}`),
    addItemToProject: (projectId, itemType, itemId) => api.post(
      `/progress/projects/${projectId}/items`, 
      { itemType, itemId }
    ),
    removeItemFromProject: (projectId, itemType, itemId) => api.delete(
      `/progress/projects/${projectId}/items/${itemType}/${itemId}`
    ),
  },
  
  // AI features endpoints
  ai: {
    // Summarization
    summarizeText: (text) => api.post('/ai/summarize/text', { text }),
    summarizePage: (bookId, page) => api.post('/ai/summarize/page', { bookId, page }),
    summarizeBook: (bookId) => api.post('/ai/summarize/book', { bookId }),
    
    // Question Answering
    askQuestion: (question, context) => api.post('/ai/ask', { question, context }),
    
    // Flashcard Generation
    generateFlashcards: (text, options) => api.post('/ai/generate/flashcards', { text, options }),
    generateFlashcardsFromPage: (bookId, page, options) => api.post(
      '/ai/generate/flashcards/page', 
      { bookId, page, options }
    ),
    
    // Knowledge Graph
    generateKnowledgeGraph: (noteIds) => api.post('/ai/generate/knowledge-graph', { noteIds }),
  },
  
  // Search endpoints
  search: {
    search: (query, filters) => api.get('/search', { params: { query, ...filters } }),
    recentSearches: () => api.get('/search/recent'),
    clearRecentSearches: () => api.delete('/search/recent'),
  },
  
  // Settings endpoints
  settings: {
    get: () => api.get('/settings'),
    update: (settings) => api.put('/settings', settings),
    reset: () => api.post('/settings/reset'),
    export: () => api.get('/settings/export'),
    import: (settings) => api.post('/settings/import', settings),
  },
};

// Mock API implementation for development
const mockApi = {
  // Auth endpoints
  auth: {
    login: async (credentials) => {
      console.log('Mock API: Login', credentials);
      // Simulate successful login
      localStorage.setItem('auth-token', 'mock-token-12345');
      return {
        data: {
          user: {
            id: 'user-1',
            name: 'Alex Johnson',
            email: credentials.email,
            avatar: 'https://via.placeholder.com/150',
          },
          token: 'mock-token-12345',
        },
      };
    },
    register: async (userData) => {
      console.log('Mock API: Register', userData);
      // Simulate successful registration
      localStorage.setItem('auth-token', 'mock-token-12345');
      return {
        data: {
          user: {
            id: `user-${Date.now()}`,
            name: userData.name,
            email: userData.email,
            avatar: 'https://via.placeholder.com/150',
          },
          token: 'mock-token-12345',
        },
      };
    },
    forgotPassword: async (email) => {
      console.log('Mock API: Forgot Password', email);
      // Simulate successful password reset request
      return {
        data: {
          message: 'Password reset email sent',
        },
      };
    },
    resetPassword: async (token, newPassword) => {
      console.log('Mock API: Reset Password', { token, newPassword });
      // Simulate successful password reset
      return {
        data: {
          message: 'Password reset successful',
        },
      };
    },
    logout: async () => {
      console.log('Mock API: Logout');
      // Simulate successful logout
      localStorage.removeItem('auth-token');
      return {
        data: {
          message: 'Logout successful',
        },
      };
    },
    me: async () => {
      console.log('Mock API: Get Current User');
      // Simulate getting current user
      return {
        data: {
          user: {
            id: 'user-1',
            name: 'Alex Johnson',
            email: 'alex.johnson@example.com',
            avatar: 'https://via.placeholder.com/150',
          },
        },
      };
    },
  },
  
  // Notes endpoints
  notes: {
    getAll: async (params) => {
      console.log('Mock API: Get All Notes', params);
      // Simulate getting all notes
      const mockNotes = [
        { 
          id: 1, 
          title: 'Machine Learning Fundamentals', 
          excerpt: 'An overview of machine learning concepts...',
          category: 'AI', 
          date: '2025-07-28', 
          tags: ['ML', 'AI', 'Neural Networks'],
          starred: true
        },
        { 
          id: 2, 
          title: 'React Hooks Deep Dive', 
          excerpt: 'Exploring React hooks including useState...',
          category: 'Programming', 
          date: '2025-07-25', 
          tags: ['React', 'JavaScript', 'Hooks'],
          starred: false
        },
      ];
      
      return {
        data: {
          notes: mockNotes,
          total: mockNotes.length,
        },
      };
    },
    getById: async (id) => {
      console.log('Mock API: Get Note by ID', id);
      // Simulate getting a note by ID
      const mockNote = { 
        id: parseInt(id), 
        title: 'Machine Learning Fundamentals', 
        content: '# Machine Learning Fundamentals\n\nDetailed content here...',
        category: 'AI', 
        date: '2025-07-28', 
        lastEdited: '2025-07-29T14:30:00',
        tags: ['ML', 'AI', 'Neural Networks'],
        starred: true
      };
      
      return {
        data: {
          note: mockNote,
        },
      };
    },
    create: async (noteData) => {
      console.log('Mock API: Create Note', noteData);
      // Simulate creating a note
      return {
        data: {
          note: {
            id: Date.now(),
            date: new Date().toISOString().split('T')[0],
            lastEdited: new Date().toISOString(),
            starred: false,
            ...noteData,
          },
        },
      };
    },
    update: async (id, noteData) => {
      console.log('Mock API: Update Note', { id, noteData });
      // Simulate updating a note
      return {
        data: {
          note: {
            id: parseInt(id),
            ...noteData,
            lastEdited: new Date().toISOString(),
          },
        },
      };
    },
    delete: async (id) => {
      console.log('Mock API: Delete Note', id);
      // Simulate deleting a note
      return {
        data: {
          message: 'Note deleted successfully',
        },
      };
    },
  },
  
  // Visualizations endpoints
  visualizations: {
    getAll: async (params) => {
      console.log('Mock API: Get All Visualizations', params);
      // Simulate getting all visualizations
      const mockVisualizations = [
        {
          id: 1,
          title: 'Machine Learning Concepts',
          type: 'mindmap',
          date: '2025-07-28',
          sourceNote: 'Machine Learning Fundamentals',
          sourceNoteId: 1,
          thumbnail: 'https://via.placeholder.com/400x250?text=Mind+Map',
          description: 'Mind map of key machine learning concepts and their relationships',
        },
        {
          id: 2,
          title: 'Neural Network Architecture',
          type: 'flowchart',
          date: '2025-07-26',
          sourceNote: 'Deep Learning Architectures',
          sourceNoteId: 3,
          thumbnail: 'https://via.placeholder.com/400x250?text=Flowchart',
          description: 'Flowchart showing the architecture of a neural network',
        },
      ];
      
      return {
        data: {
          visualizations: mockVisualizations,
          total: mockVisualizations.length,
        },
      };
    },
    generate: async (noteId, type, title) => {
      console.log('Mock API: Generate Visualization', { noteId, type, title });
      // Simulate generating a visualization
      return {
        data: {
          visualization: {
            id: Date.now(),
            title: title || `${type.charAt(0).toUpperCase() + type.slice(1)} of Note ${noteId}`,
            type,
            date: new Date().toISOString().split('T')[0],
            sourceNote: `Note ${noteId}`,
            sourceNoteId: parseInt(noteId),
            thumbnail: `https://via.placeholder.com/400x250?text=${type.replace('_', '+')}`,
            description: `Auto-generated ${type} for Note ${noteId}`,
            data: {}, // This would be the actual visualization data
          },
        },
      };
    },
  },
  
  // Processing endpoints
  processing: {
    processText: async (text, options) => {
      console.log('Mock API: Process Text', { text, options });
      // Simulate processing text
      return {
        data: {
          result: {
            summary: 'This is a summary of the processed text...',
            keypoints: ['Key point 1', 'Key point 2', 'Key point 3'],
            questions: options.questions ? ['Question 1?', 'Question 2?'] : [],
            glossary: options.glossary ? [{ term: 'Term 1', definition: 'Definition 1' }] : [],
          },
        },
      };
    },
  },
  
  // Reading endpoints
  reading: {
    // Mock books data
    mockBooks: [
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
      },
    ],
    
    // Mock annotations data
    mockAnnotations: {
      1: [ // Book ID 1
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
      2: [ // Book ID 2
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
      3: [ // Book ID 3
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
    },
    
    // Mock bookmarks data
    mockBookmarks: {
      1: [12, 45, 78, 120], // Book ID 1
      2: [34, 65, 102],     // Book ID 2
      3: [87, 145, 200],    // Book ID 3
    },
    
    // Books/Documents
    getBooks: async (params) => {
      console.log('Mock API: Get Books', params);
      return {
        data: {
          books: mockApi.reading.mockBooks,
          total: mockApi.reading.mockBooks.length,
        },
      };
    },
    
    getBookById: async (id) => {
      console.log('Mock API: Get Book by ID', id);
      const book = mockApi.reading.mockBooks.find(book => book.id === parseInt(id));
      
      if (!book) {
        return Promise.reject({ response: { status: 404, data: 'Book not found' } });
      }
      
      return {
        data: {
          book,
        },
      };
    },
    
    uploadBook: async (formData) => {
      console.log('Mock API: Upload Book', formData);
      // Simulate book upload
      const newBook = {
        id: Date.now(),
        title: formData.get('title') || 'New Book',
        author: formData.get('author') || 'Unknown Author',
        coverImage: 'https://via.placeholder.com/150x200?text=New+Book',
        totalPages: Math.floor(Math.random() * 300) + 100, // Random page count
        currentPage: 1,
        lastRead: new Date().toISOString(),
        progress: 0,
        format: 'pdf',
        path: `/documents/book-${Date.now()}.pdf`,
      };
      
      // Add to mock books
      mockApi.reading.mockBooks.push(newBook);
      
      return {
        data: {
          book: newBook,
          message: 'Book uploaded successfully',
        },
      };
    },
    
    updateBook: async (id, bookData) => {
      console.log('Mock API: Update Book', { id, bookData });
      const bookIndex = mockApi.reading.mockBooks.findIndex(book => book.id === parseInt(id));
      
      if (bookIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Book not found' } });
      }
      
      // Update book
      const updatedBook = {
        ...mockApi.reading.mockBooks[bookIndex],
        ...bookData,
        lastRead: new Date().toISOString(),
      };
      
      mockApi.reading.mockBooks[bookIndex] = updatedBook;
      
      return {
        data: {
          book: updatedBook,
        },
      };
    },
    
    deleteBook: async (id) => {
      console.log('Mock API: Delete Book', id);
      const bookIndex = mockApi.reading.mockBooks.findIndex(book => book.id === parseInt(id));
      
      if (bookIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Book not found' } });
      }
      
      // Remove book
      mockApi.reading.mockBooks.splice(bookIndex, 1);
      
      return {
        data: {
          message: 'Book deleted successfully',
        },
      };
    },
    
    // PDF Operations
    getPdfContent: async (id, page) => {
      console.log('Mock API: Get PDF Content', { id, page });
      // Simulate PDF content (would be binary data in a real API)
      return {
        data: {
          content: 'Mock PDF content for page ' + page,
          pageNumber: parseInt(page),
          totalPages: mockApi.reading.mockBooks.find(book => book.id === parseInt(id))?.totalPages || 100,
        },
      };
    },
    
    getPdfThumbnail: async (id, page) => {
      console.log('Mock API: Get PDF Thumbnail', { id, page });
      // Simulate PDF thumbnail (would be binary data in a real API)
      return {
        data: `Mock PDF thumbnail for book ${id}, page ${page}`,
      };
    },
    
    getPdfToc: async (id) => {
      console.log('Mock API: Get PDF TOC', id);
      // Simulate table of contents
      return {
        data: {
          toc: [
            { title: 'Chapter 1: Introduction', page: 1 },
            { title: 'Chapter 2: Basic Concepts', page: 15 },
            { title: 'Chapter 3: Advanced Topics', page: 45 },
            { title: 'Chapter 4: Case Studies', page: 78 },
            { title: 'Chapter 5: Future Directions', page: 120 },
          ],
        },
      };
    },
    
    // Annotations
    getAnnotations: async (bookId, page = null) => {
      console.log('Mock API: Get Annotations', { bookId, page });
      const bookAnnotations = mockApi.reading.mockAnnotations[bookId] || [];
      
      // Filter by page if provided
      const filteredAnnotations = page 
        ? bookAnnotations.filter(anno => anno.page === parseInt(page))
        : bookAnnotations;
      
      return {
        data: {
          annotations: filteredAnnotations,
          total: filteredAnnotations.length,
        },
      };
    },
    
    createAnnotation: async (bookId, annotationData) => {
      console.log('Mock API: Create Annotation', { bookId, annotationData });
      const newAnnotation = {
        id: `anno-${Date.now()}`,
        createdAt: new Date().toISOString(),
        ...annotationData,
      };
      
      // Initialize book annotations array if it doesn't exist
      if (!mockApi.reading.mockAnnotations[bookId]) {
        mockApi.reading.mockAnnotations[bookId] = [];
      }
      
      // Add annotation
      mockApi.reading.mockAnnotations[bookId].push(newAnnotation);
      
      return {
        data: {
          annotation: newAnnotation,
        },
      };
    },
    
    updateAnnotation: async (bookId, annotationId, annotationData) => {
      console.log('Mock API: Update Annotation', { bookId, annotationId, annotationData });
      const bookAnnotations = mockApi.reading.mockAnnotations[bookId] || [];
      const annotationIndex = bookAnnotations.findIndex(anno => anno.id === annotationId);
      
      if (annotationIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Annotation not found' } });
      }
      
      // Update annotation
      const updatedAnnotation = {
        ...bookAnnotations[annotationIndex],
        ...annotationData,
      };
      
      bookAnnotations[annotationIndex] = updatedAnnotation;
      
      return {
        data: {
          annotation: updatedAnnotation,
        },
      };
    },
    
    deleteAnnotation: async (bookId, annotationId) => {
      console.log('Mock API: Delete Annotation', { bookId, annotationId });
      const bookAnnotations = mockApi.reading.mockAnnotations[bookId] || [];
      const annotationIndex = bookAnnotations.findIndex(anno => anno.id === annotationId);
      
      if (annotationIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Annotation not found' } });
      }
      
      // Remove annotation
      bookAnnotations.splice(annotationIndex, 1);
      
      return {
        data: {
          message: 'Annotation deleted successfully',
        },
      };
    },
    
    // Bookmarks
    getBookmarks: async (bookId) => {
      console.log('Mock API: Get Bookmarks', bookId);
      const bookmarks = mockApi.reading.mockBookmarks[bookId] || [];
      
      return {
        data: {
          bookmarks,
        },
      };
    },
    
    addBookmark: async (bookId, page) => {
      console.log('Mock API: Add Bookmark', { bookId, page });
      // Initialize book bookmarks array if it doesn't exist
      if (!mockApi.reading.mockBookmarks[bookId]) {
        mockApi.reading.mockBookmarks[bookId] = [];
      }
      
      // Add bookmark if it doesn't exist
      if (!mockApi.reading.mockBookmarks[bookId].includes(page)) {
        mockApi.reading.mockBookmarks[bookId].push(page);
        // Sort bookmarks
        mockApi.reading.mockBookmarks[bookId].sort((a, b) => a - b);
      }
      
      return {
        data: {
          bookmarks: mockApi.reading.mockBookmarks[bookId],
        },
      };
    },
    
    removeBookmark: async (bookId, page) => {
      console.log('Mock API: Remove Bookmark', { bookId, page });
      if (!mockApi.reading.mockBookmarks[bookId]) {
        return Promise.reject({ response: { status: 404, data: 'Book not found' } });
      }
      
      // Remove bookmark
      mockApi.reading.mockBookmarks[bookId] = mockApi.reading.mockBookmarks[bookId]
        .filter(p => p !== parseInt(page));
      
      return {
        data: {
          bookmarks: mockApi.reading.mockBookmarks[bookId],
        },
      };
    },
    
    // Reading Progress
    updateReadingProgress: async (bookId, progressData) => {
      console.log('Mock API: Update Reading Progress', { bookId, progressData });
      const bookIndex = mockApi.reading.mockBooks.findIndex(book => book.id === parseInt(bookId));
      
      if (bookIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Book not found' } });
      }
      
      // Update book progress
      const book = mockApi.reading.mockBooks[bookIndex];
      const updatedBook = {
        ...book,
        currentPage: progressData.currentPage || book.currentPage,
        progress: progressData.progress || (progressData.currentPage / book.totalPages * 100),
        lastRead: new Date().toISOString(),
      };
      
      mockApi.reading.mockBooks[bookIndex] = updatedBook;
      
      return {
        data: {
          book: updatedBook,
        },
      };
    },
    
    getReadingStats: async () => {
      console.log('Mock API: Get Reading Stats');
      // Calculate stats from mock data
      const totalBooks = mockApi.reading.mockBooks.length;
      const booksStarted = mockApi.reading.mockBooks.filter(book => book.progress > 0).length;
      const booksCompleted = mockApi.reading.mockBooks.filter(book => book.progress >= 99.9).length;
      const totalPages = mockApi.reading.mockBooks.reduce((sum, book) => sum + book.totalPages, 0);
      const pagesRead = mockApi.reading.mockBooks.reduce(
        (sum, book) => sum + Math.floor(book.totalPages * (book.progress / 100)), 
        0
      );
      
      return {
        data: {
          stats: {
            totalBooks,
            booksStarted,
            booksCompleted,
            totalPages,
            pagesRead,
            readingStreak: 7, // Mock value
            averageReadingSpeed: 25, // pages per hour
            totalReadingTime: 3240, // minutes
          },
        },
      };
    },
  },
  
  // Flashcard endpoints
  flashcards: {
    // Mock flashcards data
    mockCards: [
      {
        id: 'fc-1',
        front: 'What is machine learning?',
        back: 'Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from data.',
        sourceType: 'book',
        sourceId: 1, // Book ID
        sourcePage: 12,
        sourceTitle: 'Machine Learning Fundamentals',
        tags: ['AI', 'ML', 'Basics'],
        difficulty: 'medium', // 'easy', 'medium', 'hard'
        createdAt: '2025-07-20T10:20:00',
        lastReviewed: '2025-07-29T15:30:00',
        nextReviewDate: '2025-08-01T15:30:00',
        reviewCount: 3,
        interval: 3, // days until next review
        easeFactor: 2.5, // SRS algorithm parameter
        streak: 2, // consecutive correct reviews
      },
      {
        id: 'fc-2',
        front: 'What is a neural network?',
        back: 'A neural network is a computational model inspired by the structure and function of the human brain, consisting of interconnected nodes (neurons) organized in layers.',
        sourceType: 'book',
        sourceId: 1, // Book ID
        sourcePage: 45,
        sourceTitle: 'Machine Learning Fundamentals',
        tags: ['AI', 'ML', 'Neural Networks'],
        difficulty: 'hard',
        createdAt: '2025-07-22T16:35:00',
        lastReviewed: '2025-07-28T09:15:00',
        nextReviewDate: '2025-07-30T09:15:00',
        reviewCount: 2,
        interval: 2,
        easeFactor: 2.2,
        streak: 1,
      },
      {
        id: 'fc-3',
        front: 'What is the Compound Component pattern in React?',
        back: 'The Compound Component pattern allows you to create components that share state implicitly, providing a more declarative and flexible API.',
        sourceType: 'book',
        sourceId: 2, // Book ID
        sourcePage: 34,
        sourceTitle: 'Advanced React Patterns',
        tags: ['React', 'Patterns', 'Components'],
        difficulty: 'medium',
        createdAt: '2025-07-23T11:30:00',
        lastReviewed: '2025-07-27T14:20:00',
        nextReviewDate: '2025-07-31T14:20:00',
        reviewCount: 2,
        interval: 4,
        easeFactor: 2.7,
        streak: 2,
      },
      {
        id: 'fc-4',
        front: 'What is a binary search tree?',
        back: 'A binary search tree is a binary tree where each node has at most two children, and all nodes in the left subtree have values less than the node\'s value, while all nodes in the right subtree have values greater than the node\'s value.',
        sourceType: 'book',
        sourceId: 3, // Book ID
        sourcePage: 87,
        sourceTitle: 'Data Structures and Algorithms',
        tags: ['DSA', 'Trees', 'Search'],
        difficulty: 'hard',
        createdAt: '2025-07-24T14:15:00',
        lastReviewed: null, // Not reviewed yet
        nextReviewDate: '2025-07-24T14:15:00', // Initial review date is creation date
        reviewCount: 0,
        interval: 0,
        easeFactor: 2.5, // Default ease factor
        streak: 0,
      },
    ],
    
    // Mock decks data
    mockDecks: [
      {
        id: 'deck-1',
        name: 'Machine Learning',
        description: 'Flashcards for machine learning concepts',
        tags: ['AI', 'ML'],
        createdAt: '2025-07-20T10:00:00',
        lastStudied: '2025-07-29T15:30:00',
        cardIds: ['fc-1', 'fc-2'],
      },
      {
        id: 'deck-2',
        name: 'React Patterns',
        description: 'Advanced React design patterns',
        tags: ['React', 'Patterns'],
        createdAt: '2025-07-23T11:00:00',
        lastStudied: '2025-07-27T14:20:00',
        cardIds: ['fc-3'],
      },
      {
        id: 'deck-3',
        name: 'Data Structures',
        description: 'Common data structures and algorithms',
        tags: ['DSA', 'Algorithms'],
        createdAt: '2025-07-24T14:00:00',
        lastStudied: null,
        cardIds: ['fc-4'],
      },
    ],
    
    // Mock study sessions data
    mockStudySessions: [
      {
        id: 'session-1',
        date: '2025-07-29T15:30:00',
        deckId: 'deck-1',
        duration: 600, // seconds
        cardsStudied: 2,
        correctAnswers: 2,
        incorrectAnswers: 0,
      },
      {
        id: 'session-2',
        date: '2025-07-27T14:20:00',
        deckId: 'deck-2',
        duration: 300, // seconds
        cardsStudied: 1,
        correctAnswers: 1,
        incorrectAnswers: 0,
      },
    ],
    
    // Spaced repetition algorithm (simplified SM-2)
    calculateNextReview: (card, quality) => {
      // quality: 0-5 rating of how well the user remembered the card
      // 0: complete blackout, 5: perfect recall
      
      let { interval, easeFactor, streak } = card;
      
      // Update ease factor based on quality
      easeFactor = Math.max(1.3, easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)));
      
      // Update interval based on quality and previous interval
      if (quality < 3) {
        // If quality is less than 3, reset streak and interval
        streak = 0;
        interval = 1;
      } else {
        // If quality is 3 or higher, increase streak and calculate new interval
        streak += 1;
        
        if (streak === 1) {
          interval = 1;
        } else if (streak === 2) {
          interval = 6;
        } else {
          interval = Math.round(interval * easeFactor);
        }
      }
      
      // Calculate next review date
      const nextReviewDate = new Date();
      nextReviewDate.setDate(nextReviewDate.getDate() + interval);
      
      return {
        interval,
        easeFactor,
        streak,
        nextReviewDate: nextReviewDate.toISOString(),
        lastReviewed: new Date().toISOString(),
        reviewCount: card.reviewCount + 1,
      };
    },
    
    // Cards
    getCards: async (params) => {
      console.log('Mock API: Get Flashcards', params);
      
      // Filter cards based on params
      let filteredCards = [...mockApi.flashcards.mockCards];
      
      if (params?.tags) {
        const tags = Array.isArray(params.tags) ? params.tags : [params.tags];
        filteredCards = filteredCards.filter(card => 
          tags.some(tag => card.tags.includes(tag))
        );
      }
      
      if (params?.difficulty) {
        filteredCards = filteredCards.filter(card => card.difficulty === params.difficulty);
      }
      
      if (params?.sourceType && params?.sourceId) {
        filteredCards = filteredCards.filter(card => 
          card.sourceType === params.sourceType && card.sourceId === parseInt(params.sourceId)
        );
      }
      
      return {
        data: {
          cards: filteredCards,
          total: filteredCards.length,
        },
      };
    },
    
    getCardById: async (id) => {
      console.log('Mock API: Get Flashcard by ID', id);
      const card = mockApi.flashcards.mockCards.find(card => card.id === id);
      
      if (!card) {
        return Promise.reject({ response: { status: 404, data: 'Flashcard not found' } });
      }
      
      return {
        data: {
          card,
        },
      };
    },
    
    createCard: async (cardData) => {
      console.log('Mock API: Create Flashcard', cardData);
      const newCard = {
        id: `fc-${Date.now()}`,
        createdAt: new Date().toISOString(),
        lastReviewed: null,
        nextReviewDate: new Date().toISOString(), // Initial review date is creation date
        reviewCount: 0,
        interval: 0,
        easeFactor: 2.5, // Default ease factor
        streak: 0,
        ...cardData,
      };
      
      // Add to mock cards
      mockApi.flashcards.mockCards.push(newCard);
      
      // If deckId is provided, add the card to the deck
      if (cardData.deckId) {
        const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === cardData.deckId);
        if (deckIndex !== -1) {
          mockApi.flashcards.mockDecks[deckIndex].cardIds.push(newCard.id);
        }
      }
      
      return {
        data: {
          card: newCard,
        },
      };
    },
    
    updateCard: async (id, cardData) => {
      console.log('Mock API: Update Flashcard', { id, cardData });
      const cardIndex = mockApi.flashcards.mockCards.findIndex(card => card.id === id);
      
      if (cardIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Flashcard not found' } });
      }
      
      // Update card
      const updatedCard = {
        ...mockApi.flashcards.mockCards[cardIndex],
        ...cardData,
      };
      
      mockApi.flashcards.mockCards[cardIndex] = updatedCard;
      
      return {
        data: {
          card: updatedCard,
        },
      };
    },
    
    deleteCard: async (id) => {
      console.log('Mock API: Delete Flashcard', id);
      const cardIndex = mockApi.flashcards.mockCards.findIndex(card => card.id === id);
      
      if (cardIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Flashcard not found' } });
      }
      
      // Remove card from all decks
      mockApi.flashcards.mockDecks.forEach(deck => {
        const cardIdIndex = deck.cardIds.indexOf(id);
        if (cardIdIndex !== -1) {
          deck.cardIds.splice(cardIdIndex, 1);
        }
      });
      
      // Remove card
      mockApi.flashcards.mockCards.splice(cardIndex, 1);
      
      return {
        data: {
          message: 'Flashcard deleted successfully',
        },
      };
    },
    
    reviewCard: async (id, reviewData) => {
      console.log('Mock API: Review Flashcard', { id, reviewData });
      const cardIndex = mockApi.flashcards.mockCards.findIndex(card => card.id === id);
      
      if (cardIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Flashcard not found' } });
      }
      
      const card = mockApi.flashcards.mockCards[cardIndex];
      
      // Calculate next review parameters
      const quality = reviewData.quality || 3; // Default to medium quality
      const reviewUpdates = mockApi.flashcards.calculateNextReview(card, quality);
      
      // Update card
      const updatedCard = {
        ...card,
        ...reviewUpdates,
      };
      
      mockApi.flashcards.mockCards[cardIndex] = updatedCard;
      
      return {
        data: {
          card: updatedCard,
        },
      };
    },
    
    // Decks
    getDecks: async (params) => {
      console.log('Mock API: Get Decks', params);
      
      // Filter decks based on params
      let filteredDecks = [...mockApi.flashcards.mockDecks];
      
      if (params?.tags) {
        const tags = Array.isArray(params.tags) ? params.tags : [params.tags];
        filteredDecks = filteredDecks.filter(deck => 
          tags.some(tag => deck.tags.includes(tag))
        );
      }
      
      return {
        data: {
          decks: filteredDecks,
          total: filteredDecks.length,
        },
      };
    },
    
    getDeckById: async (id) => {
      console.log('Mock API: Get Deck by ID', id);
      const deck = mockApi.flashcards.mockDecks.find(deck => deck.id === id);
      
      if (!deck) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      return {
        data: {
          deck,
        },
      };
    },
    
    createDeck: async (deckData) => {
      console.log('Mock API: Create Deck', deckData);
      const newDeck = {
        id: `deck-${Date.now()}`,
        createdAt: new Date().toISOString(),
        lastStudied: null,
        cardIds: [],
        ...deckData,
      };
      
      // Add to mock decks
      mockApi.flashcards.mockDecks.push(newDeck);
      
      return {
        data: {
          deck: newDeck,
        },
      };
    },
    
    updateDeck: async (id, deckData) => {
      console.log('Mock API: Update Deck', { id, deckData });
      const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === id);
      
      if (deckIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      // Update deck
      const updatedDeck = {
        ...mockApi.flashcards.mockDecks[deckIndex],
        ...deckData,
      };
      
      mockApi.flashcards.mockDecks[deckIndex] = updatedDeck;
      
      return {
        data: {
          deck: updatedDeck,
        },
      };
    },
    
    deleteDeck: async (id) => {
      console.log('Mock API: Delete Deck', id);
      const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === id);
      
      if (deckIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      // Remove deck
      mockApi.flashcards.mockDecks.splice(deckIndex, 1);
      
      return {
        data: {
          message: 'Deck deleted successfully',
        },
      };
    },
    
    // Deck-Card Operations
    getCardsInDeck: async (deckId) => {
      console.log('Mock API: Get Cards in Deck', deckId);
      const deck = mockApi.flashcards.mockDecks.find(deck => deck.id === deckId);
      
      if (!deck) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      const cards = mockApi.flashcards.mockCards.filter(card => deck.cardIds.includes(card.id));
      
      return {
        data: {
          cards,
          total: cards.length,
        },
      };
    },
    
    addCardToDeck: async (deckId, cardId) => {
      console.log('Mock API: Add Card to Deck', { deckId, cardId });
      const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === deckId);
      
      if (deckIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      const cardExists = mockApi.flashcards.mockCards.some(card => card.id === cardId.cardId);
      
      if (!cardExists) {
        return Promise.reject({ response: { status: 404, data: 'Card not found' } });
      }
      
      // Add card to deck if not already there
      if (!mockApi.flashcards.mockDecks[deckIndex].cardIds.includes(cardId.cardId)) {
        mockApi.flashcards.mockDecks[deckIndex].cardIds.push(cardId.cardId);
      }
      
      return {
        data: {
          deck: mockApi.flashcards.mockDecks[deckIndex],
        },
      };
    },
    
    removeCardFromDeck: async (deckId, cardId) => {
      console.log('Mock API: Remove Card from Deck', { deckId, cardId });
      const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === deckId);
      
      if (deckIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      // Remove card from deck
      const cardIdIndex = mockApi.flashcards.mockDecks[deckIndex].cardIds.indexOf(cardId);
      
      if (cardIdIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Card not in deck' } });
      }
      
      mockApi.flashcards.mockDecks[deckIndex].cardIds.splice(cardIdIndex, 1);
      
      return {
        data: {
          deck: mockApi.flashcards.mockDecks[deckIndex],
        },
      };
    },
    
    // Study Sessions
    getStudySessions: async (params) => {
      console.log('Mock API: Get Study Sessions', params);
      
      // Filter sessions based on params
      let filteredSessions = [...mockApi.flashcards.mockStudySessions];
      
      if (params?.deckId) {
        filteredSessions = filteredSessions.filter(session => session.deckId === params.deckId);
      }
      
      return {
        data: {
          sessions: filteredSessions,
          total: filteredSessions.length,
        },
      };
    },
    
    startStudySession: async (deckId) => {
      console.log('Mock API: Start Study Session', { deckId });
      const deck = mockApi.flashcards.mockDecks.find(deck => deck.id === deckId.deckId);
      
      if (!deck) {
        return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
      }
      
      // Get cards in deck
      const cards = mockApi.flashcards.mockCards.filter(card => deck.cardIds.includes(card.id));
      
      // Get due cards (cards with nextReviewDate <= now)
      const now = new Date();
      const dueCards = cards.filter(card => 
        !card.lastReviewed || new Date(card.nextReviewDate) <= now
      );
      
      // If no due cards, use all cards
      const cardsToStudy = dueCards.length > 0 ? dueCards : cards;
      
      // Shuffle cards
      const shuffledCards = [...cardsToStudy].sort(() => Math.random() - 0.5);
      
      return {
        data: {
          sessionId: `session-${Date.now()}`,
          deckId: deckId.deckId,
          cards: shuffledCards,
          total: shuffledCards.length,
        },
      };
    },
    
    endStudySession: async (sessionData) => {
      console.log('Mock API: End Study Session', sessionData);
      
      // Create new session record
      const newSession = {
        id: sessionData.sessionId || `session-${Date.now()}`,
        date: new Date().toISOString(),
        ...sessionData,
      };
      
      // Add to mock sessions
      mockApi.flashcards.mockStudySessions.push(newSession);
      
      // Update deck's lastStudied date
      const deckIndex = mockApi.flashcards.mockDecks.findIndex(deck => deck.id === sessionData.deckId);
      
      if (deckIndex !== -1) {
        mockApi.flashcards.mockDecks[deckIndex].lastStudied = new Date().toISOString();
      }
      
      return {
        data: {
          session: newSession,
        },
      };
    },
    
    // Due Cards
    getDueCards: async (deckId = null) => {
      console.log('Mock API: Get Due Cards', { deckId });
      
      // Get all cards or cards in specific deck
      let cards = [...mockApi.flashcards.mockCards];
      
      if (deckId) {
        const deck = mockApi.flashcards.mockDecks.find(deck => deck.id === deckId);
        
        if (!deck) {
          return Promise.reject({ response: { status: 404, data: 'Deck not found' } });
        }
        
        cards = cards.filter(card => deck.cardIds.includes(card.id));
      }
      
      // Get due cards (cards with nextReviewDate <= now)
      const now = new Date();
      const dueCards = cards.filter(card => 
        !card.lastReviewed || new Date(card.nextReviewDate) <= now
      );
      
      return {
        data: {
          cards: dueCards,
          total: dueCards.length,
        },
      };
    },
    
    // Stats
    getFlashcardStats: async () => {
      console.log('Mock API: Get Flashcard Stats');
      
      // Calculate stats from mock data
      const totalCards = mockApi.flashcards.mockCards.length;
      const cardsStudied = mockApi.flashcards.mockCards.filter(card => card.reviewCount > 0).length;
      const cardsLearned = mockApi.flashcards.mockCards.filter(card => card.streak >= 2).length;
      const totalReviews = mockApi.flashcards.mockCards.reduce((sum, card) => sum + card.reviewCount, 0);
      
      const totalSessions = mockApi.flashcards.mockStudySessions.length;
      const totalStudyTime = mockApi.flashcards.mockStudySessions.reduce((sum, session) => sum + session.duration, 0);
      const totalCorrect = mockApi.flashcards.mockStudySessions.reduce((sum, session) => sum + session.correctAnswers, 0);
      const totalIncorrect = mockApi.flashcards.mockStudySessions.reduce((sum, session) => sum + session.incorrectAnswers, 0);
      
      return {
        data: {
          stats: {
            totalCards,
            cardsStudied,
            cardsLearned,
            totalReviews,
            totalSessions,
            totalStudyTime,
            totalCorrect,
            totalIncorrect,
            accuracy: totalCorrect + totalIncorrect > 0 
              ? (totalCorrect / (totalCorrect + totalIncorrect)) * 100 
              : 0,
            completionRate: totalCards > 0 ? (cardsLearned / totalCards) * 100 : 0,
            studyStreak: 5, // Mock value
          },
        },
      };
    },
  },
  
  // Progress tracking endpoints
  progress: {
    // Mock progress data
    mockProgress: {
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
        {
          id: 'achievement-4',
          title: 'Speed Reader',
          description: 'Read 50 pages in a day',
          icon: 'zap',
          unlockedAt: null,
          progress: 0,
          category: 'reading',
        },
        {
          id: 'achievement-5',
          title: 'Perfect Recall',
          description: 'Get 10 flashcards correct in a row',
          icon: 'check',
          unlockedAt: null,
          progress: 0,
          category: 'flashcards',
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
    },
    
    // Level thresholds (XP required for each level)
    levelThresholds: [
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
    ],
    
    // Calculate level and XP to next level based on total XP
    calculateLevel: (totalXp) => {
      let level = 1;
      let xpToNextLevel = mockApi.progress.levelThresholds[1];
      
      for (let i = 1; i < mockApi.progress.levelThresholds.length; i++) {
        if (totalXp >= mockApi.progress.levelThresholds[i]) {
          level = i + 1;
          xpToNextLevel = mockApi.progress.levelThresholds[i + 1] || mockApi.progress.levelThresholds[i] * 1.5;
        } else {
          xpToNextLevel = mockApi.progress.levelThresholds[i];
          break;
        }
      }
      
      return { level, xpToNextLevel };
    },
    
    // User Progress
    getProgress: async () => {
      console.log('Mock API: Get Progress');
      return {
        data: {
          progress: mockApi.progress.mockProgress,
        },
      };
    },
    
    updateProgress: async (progressData) => {
      console.log('Mock API: Update Progress', progressData);
      
      // Update progress data
      mockApi.progress.mockProgress = {
        ...mockApi.progress.mockProgress,
        ...progressData,
      };
      
      return {
        data: {
          progress: mockApi.progress.mockProgress,
        },
      };
    },
    
    // XP and Leveling
    getXp: async () => {
      console.log('Mock API: Get XP');
      const { level, xp, xpToNextLevel, totalXp } = mockApi.progress.mockProgress;
      
      return {
        data: {
          xp: {
            current: xp,
            total: totalXp,
            toNextLevel: xpToNextLevel,
            level,
          },
        },
      };
    },
    
    addXp: async (amount, reason) => {
      console.log('Mock API: Add XP', { amount, reason });
      
      // Update XP
      const newTotalXp = mockApi.progress.mockProgress.totalXp + amount;
      const { level, xpToNextLevel } = mockApi.progress.calculateLevel(newTotalXp);
      
      // Calculate XP within the current level
      const xp = newTotalXp - (mockApi.progress.levelThresholds[level - 1] || 0);
      
      // Update progress
      mockApi.progress.mockProgress = {
        ...mockApi.progress.mockProgress,
        level,
        xp,
        xpToNextLevel,
        totalXp: newTotalXp,
      };
      
      return {
        data: {
          xp: {
            current: xp,
            total: newTotalXp,
            toNextLevel: xpToNextLevel,
            level,
            gained: amount,
            reason,
          },
        },
      };
    },
    
    // Achievements
    getAchievements: async (category = null) => {
      console.log('Mock API: Get Achievements', { category });
      
      let achievements = [...mockApi.progress.mockProgress.achievements];
      
      // Filter by category if provided
      if (category) {
        achievements = achievements.filter(achievement => achievement.category === category.category);
      }
      
      return {
        data: {
          achievements,
          total: achievements.length,
        },
      };
    },
    
    getUnlockedAchievements: async () => {
      console.log('Mock API: Get Unlocked Achievements');
      
      const unlockedAchievements = mockApi.progress.mockProgress.achievements.filter(
        achievement => achievement.unlockedAt !== null
      );
      
      return {
        data: {
          achievements: unlockedAchievements,
          total: unlockedAchievements.length,
        },
      };
    },
    
    unlockAchievement: async (achievementId) => {
      console.log('Mock API: Unlock Achievement', achievementId);
      
      const achievementIndex = mockApi.progress.mockProgress.achievements.findIndex(
        achievement => achievement.id === achievementId
      );
      
      if (achievementIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Achievement not found' } });
      }
      
      // If already unlocked, do nothing
      if (mockApi.progress.mockProgress.achievements[achievementIndex].unlockedAt !== null) {
        return {
          data: {
            achievement: mockApi.progress.mockProgress.achievements[achievementIndex],
            alreadyUnlocked: true,
          },
        };
      }
      
      // Unlock achievement
      mockApi.progress.mockProgress.achievements[achievementIndex] = {
        ...mockApi.progress.mockProgress.achievements[achievementIndex],
        unlockedAt: new Date().toISOString(),
        progress: 100,
      };
      
      return {
        data: {
          achievement: mockApi.progress.mockProgress.achievements[achievementIndex],
          xpAwarded: 50, // XP reward for unlocking achievement
        },
      };
    },
    
    updateAchievementProgress: async (achievementId, progress) => {
      console.log('Mock API: Update Achievement Progress', { achievementId, progress });
      
      const achievementIndex = mockApi.progress.mockProgress.achievements.findIndex(
        achievement => achievement.id === achievementId
      );
      
      if (achievementIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Achievement not found' } });
      }
      
      // If already unlocked, do nothing
      if (mockApi.progress.mockProgress.achievements[achievementIndex].unlockedAt !== null) {
        return {
          data: {
            achievement: mockApi.progress.mockProgress.achievements[achievementIndex],
            alreadyUnlocked: true,
          },
        };
      }
      
      // Update progress
      mockApi.progress.mockProgress.achievements[achievementIndex] = {
        ...mockApi.progress.mockProgress.achievements[achievementIndex],
        progress: Math.min(100, progress.progress),
      };
      
      // If progress reached 100%, unlock the achievement
      if (progress.progress >= 100) {
        mockApi.progress.mockProgress.achievements[achievementIndex].unlockedAt = new Date().toISOString();
        
        return {
          data: {
            achievement: mockApi.progress.mockProgress.achievements[achievementIndex],
            unlocked: true,
            xpAwarded: 50, // XP reward for unlocking achievement
          },
        };
      }
      
      return {
        data: {
          achievement: mockApi.progress.mockProgress.achievements[achievementIndex],
        },
      };
    },
    
    // Streaks
    getStreaks: async () => {
      console.log('Mock API: Get Streaks');
      
      return {
        data: {
          streaks: mockApi.progress.mockProgress.streaks,
        },
      };
    },
    
    updateStreak: async (type, value) => {
      console.log('Mock API: Update Streak', { type, value });
      
      // Update streak
      mockApi.progress.mockProgress.streaks = {
        ...mockApi.progress.mockProgress.streaks,
        [type.type]: value.value !== undefined ? value.value : (mockApi.progress.mockProgress.streaks[type.type] || 0) + 1,
      };
      
      return {
        data: {
          streaks: mockApi.progress.mockProgress.streaks,
        },
      };
    },
    
    resetStreak: async (type) => {
      console.log('Mock API: Reset Streak', type);
      
      // Reset streak
      mockApi.progress.mockProgress.streaks = {
        ...mockApi.progress.mockProgress.streaks,
        [type]: 0,
      };
      
      return {
        data: {
          streaks: mockApi.progress.mockProgress.streaks,
        },
      };
    },
    
    // Activity
    getActivity: async (days = 30) => {
      console.log('Mock API: Get Activity', { days });
      
      const activity = { ...mockApi.progress.mockProgress.activity };
      const today = new Date();
      const result = {};
      
      // Get activity for the specified number of days
      for (let i = 0; i < days; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateString = date.toISOString().split('T')[0];
        result[dateString] = activity[dateString] || 0;
      }
      
      return {
        data: {
          activity: result,
        },
      };
    },
    
    recordActivity: async (level) => {
      console.log('Mock API: Record Activity', { level });
      
      const today = new Date().toISOString().split('T')[0];
      
      // Get current activity level for today
      const currentLevel = mockApi.progress.mockProgress.activity[today] || 0;
      
      // Update activity with the higher level
      const newLevel = Math.max(currentLevel, level.level);
      
      mockApi.progress.mockProgress.activity = {
        ...mockApi.progress.mockProgress.activity,
        [today]: newLevel,
      };
      
      return {
        data: {
          activity: {
            [today]: newLevel,
          },
        },
      };
    },
    
    // Projects
    getProjects: async () => {
      console.log('Mock API: Get Projects');
      
      return {
        data: {
          projects: mockApi.progress.mockProgress.projects,
          total: mockApi.progress.mockProgress.projects.length,
        },
      };
    },
    
    getProjectById: async (id) => {
      console.log('Mock API: Get Project by ID', id);
      
      const project = mockApi.progress.mockProgress.projects.find(project => project.id === id);
      
      if (!project) {
        return Promise.reject({ response: { status: 404, data: 'Project not found' } });
      }
      
      return {
        data: {
          project,
        },
      };
    },
    
    createProject: async (projectData) => {
      console.log('Mock API: Create Project', projectData);
      
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
      
      // Add to projects
      mockApi.progress.mockProgress.projects.push(newProject);
      
      return {
        data: {
          project: newProject,
        },
      };
    },
    
    updateProject: async (id, projectData) => {
      console.log('Mock API: Update Project', { id, projectData });
      
      const projectIndex = mockApi.progress.mockProgress.projects.findIndex(project => project.id === id);
      
      if (projectIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Project not found' } });
      }
      
      // Update project
      const updatedProject = {
        ...mockApi.progress.mockProgress.projects[projectIndex],
        ...projectData,
        lastUpdated: new Date().toISOString(),
      };
      
      mockApi.progress.mockProgress.projects[projectIndex] = updatedProject;
      
      return {
        data: {
          project: updatedProject,
        },
      };
    },
    
    deleteProject: async (id) => {
      console.log('Mock API: Delete Project', id);
      
      const projectIndex = mockApi.progress.mockProgress.projects.findIndex(project => project.id === id);
      
      if (projectIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Project not found' } });
      }
      
      // Remove project
      mockApi.progress.mockProgress.projects.splice(projectIndex, 1);
      
      return {
        data: {
          message: 'Project deleted successfully',
        },
      };
    },
    
    addItemToProject: async (projectId, itemType, itemId) => {
      console.log('Mock API: Add Item to Project', { projectId, itemType, itemId });
      
      const projectIndex = mockApi.progress.mockProgress.projects.findIndex(project => project.id === projectId);
      
      if (projectIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Project not found' } });
      }
      
      const project = mockApi.progress.mockProgress.projects[projectIndex];
      
      // Check if item type is valid
      if (!project.items[itemType.itemType]) {
        return Promise.reject({ response: { status: 400, data: 'Invalid item type' } });
      }
      
      // Check if item already exists in project
      if (project.items[itemType.itemType].includes(itemId.itemId)) {
        return {
          data: {
            project,
            message: 'Item already in project',
          },
        };
      }
      
      // Add item to project
      project.items[itemType.itemType].push(itemId.itemId);
      project.lastUpdated = new Date().toISOString();
      
      return {
        data: {
          project,
        },
      };
    },
    
    removeItemFromProject: async (projectId, itemType, itemId) => {
      console.log('Mock API: Remove Item from Project', { projectId, itemType, itemId });
      
      const projectIndex = mockApi.progress.mockProgress.projects.findIndex(project => project.id === projectId);
      
      if (projectIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Project not found' } });
      }
      
      const project = mockApi.progress.mockProgress.projects[projectIndex];
      
      // Check if item type is valid
      if (!project.items[itemType]) {
        return Promise.reject({ response: { status: 400, data: 'Invalid item type' } });
      }
      
      // Remove item from project
      const itemIndex = project.items[itemType].indexOf(itemId);
      
      if (itemIndex === -1) {
        return Promise.reject({ response: { status: 404, data: 'Item not in project' } });
      }
      
      project.items[itemType].splice(itemIndex, 1);
      project.lastUpdated = new Date().toISOString();
      
      return {
        data: {
          project,
        },
      };
    },
  },
  
  // AI features endpoints
  ai: {
    // Summarization
    summarizeText: async (text) => {
      console.log('Mock API: Summarize Text', { text });
      
      // Simulate text summarization
      return {
        data: {
          summary: 'This is a summary of the provided text. It covers the main points and key concepts in a concise manner.',
          keyPoints: [
            'Key point 1 extracted from the text',
            'Key point 2 extracted from the text',
            'Key point 3 extracted from the text',
          ],
        },
      };
    },
    
    summarizePage: async (bookId, page) => {
      console.log('Mock API: Summarize Page', { bookId, page });
      
      // Simulate page summarization
      return {
        data: {
          summary: `This is a summary of page ${page.page} from book ${bookId.bookId}. It covers the main points and key concepts discussed on this page.`,
          keyPoints: [
            `Key point 1 from page ${page.page}`,
            `Key point 2 from page ${page.page}`,
            `Key point 3 from page ${page.page}`,
          ],
        },
      };
    },
    
    summarizeBook: async (bookId) => {
      console.log('Mock API: Summarize Book', { bookId });
      
      // Simulate book summarization
      return {
        data: {
          summary: `This is a comprehensive summary of the book (ID: ${bookId.bookId}). It covers the main themes, arguments, and conclusions presented throughout the book.`,
          keyPoints: [
            'Key point 1 from the book',
            'Key point 2 from the book',
            'Key point 3 from the book',
            'Key point 4 from the book',
            'Key point 5 from the book',
          ],
          chapterSummaries: [
            { title: 'Chapter 1', summary: 'Summary of chapter 1' },
            { title: 'Chapter 2', summary: 'Summary of chapter 2' },
            { title: 'Chapter 3', summary: 'Summary of chapter 3' },
          ],
        },
      };
    },
    
    // Question Answering
    askQuestion: async (question, context) => {
      console.log('Mock API: Ask Question', { question, context });
      
      // Simulate question answering
      return {
        data: {
          answer: `Here is the answer to your question: "${question.question}". This answer is based on the provided context and relevant information from the document.`,
          confidence: 0.92,
          relatedQuestions: [
            'Related question 1?',
            'Related question 2?',
            'Related question 3?',
          ],
        },
      };
    },
    
    // Flashcard Generation
    generateFlashcards: async (text, options) => {
      console.log('Mock API: Generate Flashcards', { text, options });
      
      // Simulate flashcard generation
      const numCards = options?.count || 5;
      const flashcards = [];
      
      for (let i = 1; i <= numCards; i++) {
        flashcards.push({
          front: `Question ${i} generated from the provided text?`,
          back: `Answer ${i} generated from the provided text.`,
          difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)],
          tags: ['AI-Generated', 'Auto'],
        });
      }
      
      return {
        data: {
          flashcards,
          total: flashcards.length,
        },
      };
    },
    
    generateFlashcardsFromPage: async (bookId, page, options) => {
      console.log('Mock API: Generate Flashcards from Page', { bookId, page, options });
      
      // Simulate flashcard generation from page
      const numCards = options?.count || 3;
      const flashcards = [];
      
      for (let i = 1; i <= numCards; i++) {
        flashcards.push({
          front: `Question ${i} from page ${page.page} of book ${bookId.bookId}?`,
          back: `Answer ${i} from page ${page.page} of book ${bookId.bookId}.`,
          difficulty: ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)],
          tags: ['AI-Generated', 'Auto'],
          sourceType: 'book',
          sourceId: bookId.bookId,
          sourcePage: page.page,
        });
      }
      
      return {
        data: {
          flashcards,
          total: flashcards.length,
        },
      };
    },
    
    // Knowledge Graph
    generateKnowledgeGraph: async (noteIds) => {
      console.log('Mock API: Generate Knowledge Graph', { noteIds });
      
      // Simulate knowledge graph generation
      const nodes = [
        { id: 'concept-1', label: 'Machine Learning', type: 'concept', size: 30 },
        { id: 'concept-2', label: 'Neural Networks', type: 'concept', size: 25 },
        { id: 'concept-3', label: 'Deep Learning', type: 'concept', size: 25 },
        { id: 'concept-4', label: 'Supervised Learning', type: 'concept', size: 20 },
        { id: 'concept-5', label: 'Unsupervised Learning', type: 'concept', size: 20 },
        { id: 'concept-6', label: 'Reinforcement Learning', type: 'concept', size: 20 },
        { id: 'concept-7', label: 'CNN', type: 'technique', size: 15 },
        { id: 'concept-8', label: 'RNN', type: 'technique', size: 15 },
        { id: 'concept-9', label: 'Transformer', type: 'technique', size: 15 },
        { id: 'concept-10', label: 'Classification', type: 'task', size: 15 },
        { id: 'concept-11', label: 'Regression', type: 'task', size: 15 },
        { id: 'concept-12', label: 'Clustering', type: 'task', size: 15 },
      ];
      
      const edges = [
        { source: 'concept-1', target: 'concept-2', label: 'includes' },
        { source: 'concept-1', target: 'concept-4', label: 'includes' },
        { source: 'concept-1', target: 'concept-5', label: 'includes' },
        { source: 'concept-1', target: 'concept-6', label: 'includes' },
        { source: 'concept-2', target: 'concept-3', label: 'related_to' },
        { source: 'concept-2', target: 'concept-7', label: 'includes' },
        { source: 'concept-2', target: 'concept-8', label: 'includes' },
        { source: 'concept-2', target: 'concept-9', label: 'includes' },
        { source: 'concept-4', target: 'concept-10', label: 'used_for' },
        { source: 'concept-4', target: 'concept-11', label: 'used_for' },
        { source: 'concept-5', target: 'concept-12', label: 'used_for' },
        { source: 'concept-3', target: 'concept-7', label: 'uses' },
        { source: 'concept-3', target: 'concept-9', label: 'uses' },
      ];
      
      return {
        data: {
          graph: {
            nodes,
            edges,
          },
          sourceNotes: noteIds.noteIds,
          concepts: nodes.length,
          relationships: edges.length,
        },
      };
    },
  },
  
  // Search endpoints
  search: {
    search: async (query, filters) => {
      console.log('Mock API: Search', { query, filters });
      // Simulate search results
      return {
        data: {
          results: {
            notes: [
              { 
                id: 1, 
                title: 'Machine Learning Fundamentals', 
                excerpt: 'An overview of machine learning concepts...',
                category: 'AI', 
                date: '2025-07-28', 
                tags: ['ML', 'AI', 'Neural Networks'],
                starred: true
              },
            ],
            visualizations: [
              {
                id: 1,
                title: 'Machine Learning Concepts',
                type: 'mindmap',
                date: '2025-07-28',
                sourceNote: 'Machine Learning Fundamentals',
                sourceNoteId: 1,
                thumbnail: 'https://via.placeholder.com/400x250?text=Mind+Map',
                description: 'Mind map of key machine learning concepts and their relationships',
              },
            ],
            total: 2,
          },
        },
      };
    },
    recentSearches: async () => {
      console.log('Mock API: Get Recent Searches');
      // Simulate getting recent searches
      return {
        data: {
          searches: ['machine learning', 'neural networks', 'react hooks'],
        },
      };
    },
  },
  
  // Settings endpoints
  settings: {
    get: async () => {
      console.log('Mock API: Get Settings');
      // Simulate getting settings
      return {
        data: {
          settings: {
            theme: 'system',
            fontSize: 'medium',
            emailNotifications: true,
            // ... other settings
          },
        },
      };
    },
    update: async (settings) => {
      console.log('Mock API: Update Settings', settings);
      // Simulate updating settings
      return {
        data: {
          settings,
          message: 'Settings updated successfully',
        },
      };
    },
  },
};

// Determine whether to use the real API or mock API
const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true';
const apiService = useMockApi ? mockApi : endpoints;

export default apiService;