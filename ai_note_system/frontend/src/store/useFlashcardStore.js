import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Mock data for initial flashcards
const initialFlashcards = [
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
];

// Mock data for initial decks
const initialDecks = [
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
];

// Mock data for study sessions
const initialStudySessions = [
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
];

// Spaced repetition algorithm (simplified SM-2)
const calculateNextReview = (card, quality) => {
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
};

const useFlashcardStore = create(
  persist(
    (set, get) => ({
      flashcards: initialFlashcards,
      decks: initialDecks,
      studySessions: initialStudySessions,
      activeStudyDeckId: null,
      activeStudyCards: [],
      currentCardIndex: 0,
      
      // Getters
      getFlashcardById: (id) => {
        const { flashcards } = get();
        return flashcards.find(card => card.id === id) || null;
      },
      
      getDeckById: (id) => {
        const { decks } = get();
        return decks.find(deck => deck.id === id) || null;
      },
      
      getFlashcardsForDeck: (deckId) => {
        const { flashcards } = get();
        const deck = get().getDeckById(deckId);
        
        if (!deck) return [];
        
        return flashcards.filter(card => deck.cardIds.includes(card.id));
      },
      
      getFlashcardsBySource: (sourceType, sourceId) => {
        const { flashcards } = get();
        return flashcards.filter(card => 
          card.sourceType === sourceType && card.sourceId === sourceId
        );
      },
      
      getFlashcardsByTags: (tags) => {
        const { flashcards } = get();
        return flashcards.filter(card => 
          tags.some(tag => card.tags.includes(tag))
        );
      },
      
      getDueFlashcards: (deckId = null) => {
        const { flashcards } = get();
        const now = new Date();
        
        let dueCards = flashcards.filter(card => 
          new Date(card.nextReviewDate) <= now
        );
        
        if (deckId) {
          const deck = get().getDeckById(deckId);
          if (deck) {
            dueCards = dueCards.filter(card => deck.cardIds.includes(card.id));
          }
        }
        
        return dueCards;
      },
      
      getStudySessionsForDeck: (deckId) => {
        const { studySessions } = get();
        return studySessions.filter(session => session.deckId === deckId);
      },
      
      getStudyStats: (deckId = null) => {
        const { flashcards, studySessions } = get();
        
        let relevantSessions = studySessions;
        let relevantCards = flashcards;
        
        if (deckId) {
          const deck = get().getDeckById(deckId);
          if (deck) {
            relevantSessions = studySessions.filter(session => session.deckId === deckId);
            relevantCards = flashcards.filter(card => deck.cardIds.includes(card.id));
          }
        }
        
        const totalCards = relevantCards.length;
        const cardsStudied = relevantCards.filter(card => card.reviewCount > 0).length;
        const cardsLearned = relevantCards.filter(card => card.streak >= 2).length;
        const totalReviews = relevantCards.reduce((sum, card) => sum + card.reviewCount, 0);
        
        const totalSessions = relevantSessions.length;
        const totalStudyTime = relevantSessions.reduce((sum, session) => sum + session.duration, 0);
        const totalCorrect = relevantSessions.reduce((sum, session) => sum + session.correctAnswers, 0);
        const totalIncorrect = relevantSessions.reduce((sum, session) => sum + session.incorrectAnswers, 0);
        
        // Calculate current streak (days in a row with study sessions)
        // In a real app, this would use actual timestamps and more sophisticated logic
        const studyStreak = 5; // Mock value
        
        // Calculate average study session duration (in seconds)
        const avgSessionDuration = totalSessions > 0 ? Math.round(totalStudyTime / totalSessions) : 0;
        
        // Calculate average cards per session
        const avgCardsPerSession = totalSessions > 0 ? 
          Math.round((totalCorrect + totalIncorrect) / totalSessions * 10) / 10 : 0;
        
        // Calculate retention rate (percentage of cards with streak >= 1)
        const retentionRate = totalCards > 0 ? 
          (relevantCards.filter(card => card.streak >= 1).length / totalCards) * 100 : 0;
        
        // Get last study session date
        const lastStudySession = relevantSessions.length > 0 ?
          relevantSessions.sort((a, b) => new Date(b.date) - new Date(a.date))[0].date : null;
        
        return {
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
          studyStreak,
          avgSessionDuration,
          avgCardsPerSession,
          retentionRate,
          lastStudySession,
        };
      },
      
      // Get learning progress over time
      getLearningProgressOverTime: (days = 30) => {
        const { flashcards, studySessions } = get();
        
        // Create a map of dates to review counts and accuracy
        const progressMap = {};
        const today = new Date();
        
        // Initialize all dates in the range
        for (let i = 0; i < days; i++) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateString = date.toISOString().split('T')[0];
          progressMap[dateString] = {
            reviews: 0,
            correct: 0,
            incorrect: 0,
            newCards: 0,
            learnedCards: 0,
          };
        }
        
        // Process study sessions
        studySessions.forEach(session => {
          const sessionDate = new Date(session.date);
          // Only include sessions within the specified time range
          const daysDiff = Math.floor((today - sessionDate) / (1000 * 60 * 60 * 24));
          
          if (daysDiff >= 0 && daysDiff < days) {
            const dateString = sessionDate.toISOString().split('T')[0];
            
            if (progressMap[dateString]) {
              progressMap[dateString].reviews += session.cardsStudied;
              progressMap[dateString].correct += session.correctAnswers;
              progressMap[dateString].incorrect += session.incorrectAnswers;
            }
          }
        });
        
        // Process cards to determine when they were first studied and when they were learned
        flashcards.forEach(card => {
          if (card.lastReviewed) {
            const firstReviewDate = new Date(card.createdAt);
            const daysDiff = Math.floor((today - firstReviewDate) / (1000 * 60 * 60 * 24));
            
            if (daysDiff >= 0 && daysDiff < days) {
              const dateString = firstReviewDate.toISOString().split('T')[0];
              
              if (progressMap[dateString]) {
                progressMap[dateString].newCards += 1;
              }
            }
            
            // If card is learned (streak >= 2), count when it was learned
            if (card.streak >= 2 && card.lastReviewed) {
              const learnedDate = new Date(card.lastReviewed);
              const learnedDaysDiff = Math.floor((today - learnedDate) / (1000 * 60 * 60 * 24));
              
              if (learnedDaysDiff >= 0 && learnedDaysDiff < days) {
                const dateString = learnedDate.toISOString().split('T')[0];
                
                if (progressMap[dateString]) {
                  progressMap[dateString].learnedCards += 1;
                }
              }
            }
          }
        });
        
        // Convert to array format for charts
        const timeline = Object.entries(progressMap).map(([date, data]) => ({
          date,
          reviews: data.reviews,
          correct: data.correct,
          incorrect: data.incorrect,
          accuracy: data.reviews > 0 ? (data.correct / data.reviews) * 100 : 0,
          newCards: data.newCards,
          learnedCards: data.learnedCards,
        })).sort((a, b) => new Date(a.date) - new Date(b.date));
        
        return timeline;
      },
      
      // Get flashcard difficulty distribution
      getFlashcardDifficultyDistribution: (deckId = null) => {
        const { flashcards } = get();
        
        let relevantCards = flashcards;
        
        if (deckId) {
          const deck = get().getDeckById(deckId);
          if (deck) {
            relevantCards = flashcards.filter(card => deck.cardIds.includes(card.id));
          }
        }
        
        // Count cards by difficulty
        const difficultyCount = {
          easy: 0,
          medium: 0,
          hard: 0,
        };
        
        relevantCards.forEach(card => {
          if (card.difficulty) {
            difficultyCount[card.difficulty] = (difficultyCount[card.difficulty] || 0) + 1;
          }
        });
        
        // Count cards by ease factor ranges
        const easeFactorRanges = {
          'Very Easy (2.5+)': 0,
          'Easy (2.2-2.5)': 0,
          'Medium (1.8-2.2)': 0,
          'Hard (1.5-1.8)': 0,
          'Very Hard (<1.5)': 0,
        };
        
        relevantCards.forEach(card => {
          if (card.easeFactor) {
            if (card.easeFactor >= 2.5) {
              easeFactorRanges['Very Easy (2.5+)']++;
            } else if (card.easeFactor >= 2.2) {
              easeFactorRanges['Easy (2.2-2.5)']++;
            } else if (card.easeFactor >= 1.8) {
              easeFactorRanges['Medium (1.8-2.2)']++;
            } else if (card.easeFactor >= 1.5) {
              easeFactorRanges['Hard (1.5-1.8)']++;
            } else {
              easeFactorRanges['Very Hard (<1.5)']++;
            }
          }
        });
        
        // Count cards by review count ranges
        const reviewCountRanges = {
          'New (0)': 0,
          'Few (1-2)': 0,
          'Some (3-5)': 0,
          'Many (6-10)': 0,
          'Mastered (>10)': 0,
        };
        
        relevantCards.forEach(card => {
          if (card.reviewCount === 0) {
            reviewCountRanges['New (0)']++;
          } else if (card.reviewCount <= 2) {
            reviewCountRanges['Few (1-2)']++;
          } else if (card.reviewCount <= 5) {
            reviewCountRanges['Some (3-5)']++;
          } else if (card.reviewCount <= 10) {
            reviewCountRanges['Many (6-10)']++;
          } else {
            reviewCountRanges['Mastered (>10)']++;
          }
        });
        
        return {
          byDifficulty: Object.entries(difficultyCount).map(([difficulty, count]) => ({
            difficulty,
            count,
            percentage: relevantCards.length > 0 ? (count / relevantCards.length) * 100 : 0,
          })),
          byEaseFactor: Object.entries(easeFactorRanges).map(([range, count]) => ({
            range,
            count,
            percentage: relevantCards.length > 0 ? (count / relevantCards.length) * 100 : 0,
          })),
          byReviewCount: Object.entries(reviewCountRanges).map(([range, count]) => ({
            range,
            count,
            percentage: relevantCards.length > 0 ? (count / relevantCards.length) * 100 : 0,
          })),
          totalCards: relevantCards.length,
        };
      },
      
      // Actions - Flashcards
      createFlashcard: (cardData) => {
        const { flashcards } = get();
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
        
        set({ flashcards: [newCard, ...flashcards] });
        
        // If deckId is provided, add the card to the deck
        if (cardData.deckId) {
          get().addCardToDeck(cardData.deckId, newCard.id);
        }
        
        return newCard;
      },
      
      updateFlashcard: (id, updates) => {
        const { flashcards } = get();
        const updatedFlashcards = flashcards.map(card => 
          card.id === id ? { ...card, ...updates } : card
        );
        
        set({ flashcards: updatedFlashcards });
        return updatedFlashcards.find(card => card.id === id);
      },
      
      deleteFlashcard: (id) => {
        const { flashcards, decks } = get();
        
        // Remove the card from all decks
        const updatedDecks = decks.map(deck => ({
          ...deck,
          cardIds: deck.cardIds.filter(cardId => cardId !== id),
        }));
        
        // Remove the card from flashcards
        const updatedFlashcards = flashcards.filter(card => card.id !== id);
        
        set({ 
          flashcards: updatedFlashcards,
          decks: updatedDecks,
        });
      },
      
      reviewFlashcard: (id, quality) => {
        const { flashcards } = get();
        const card = flashcards.find(card => card.id === id);
        
        if (!card) return null;
        
        // Calculate next review parameters
        const reviewUpdates = calculateNextReview(card, quality);
        
        // Update the flashcard
        const updatedFlashcards = flashcards.map(c => 
          c.id === id ? { ...c, ...reviewUpdates } : c
        );
        
        set({ flashcards: updatedFlashcards });
        return updatedFlashcards.find(c => c.id === id);
      },
      
      // Actions - Decks
      createDeck: (deckData) => {
        const { decks } = get();
        const newDeck = {
          id: `deck-${Date.now()}`,
          createdAt: new Date().toISOString(),
          lastStudied: null,
          cardIds: [],
          ...deckData,
        };
        
        set({ decks: [newDeck, ...decks] });
        return newDeck;
      },
      
      updateDeck: (id, updates) => {
        const { decks } = get();
        const updatedDecks = decks.map(deck => 
          deck.id === id ? { ...deck, ...updates } : deck
        );
        
        set({ decks: updatedDecks });
        return updatedDecks.find(deck => deck.id === id);
      },
      
      deleteDeck: (id) => {
        const { decks } = get();
        const updatedDecks = decks.filter(deck => deck.id !== id);
        
        set({ decks: updatedDecks });
      },
      
      addCardToDeck: (deckId, cardId) => {
        const { decks } = get();
        const deck = decks.find(deck => deck.id === deckId);
        
        if (!deck || deck.cardIds.includes(cardId)) return false;
        
        const updatedDecks = decks.map(d => 
          d.id === deckId 
            ? { ...d, cardIds: [...d.cardIds, cardId] } 
            : d
        );
        
        set({ decks: updatedDecks });
        return true;
      },
      
      removeCardFromDeck: (deckId, cardId) => {
        const { decks } = get();
        const deck = decks.find(deck => deck.id === deckId);
        
        if (!deck || !deck.cardIds.includes(cardId)) return false;
        
        const updatedDecks = decks.map(d => 
          d.id === deckId 
            ? { ...d, cardIds: d.cardIds.filter(id => id !== cardId) } 
            : d
        );
        
        set({ decks: updatedDecks });
        return true;
      },
      
      // Actions - Study Sessions
      startStudySession: (deckId) => {
        const deck = get().getDeckById(deckId);
        if (!deck) return false;
        
        // Get due cards for this deck
        const dueCards = get().getDueFlashcards(deckId);
        
        // If no due cards, use all cards in the deck
        const cardsToStudy = dueCards.length > 0 
          ? dueCards 
          : get().getFlashcardsForDeck(deckId);
        
        // Shuffle the cards
        const shuffledCards = [...cardsToStudy].sort(() => Math.random() - 0.5);
        
        set({ 
          activeStudyDeckId: deckId,
          activeStudyCards: shuffledCards,
          currentCardIndex: 0,
        });
        
        return true;
      },
      
      endStudySession: (sessionData) => {
        const { studySessions, activeStudyDeckId, decks } = get();
        
        if (!activeStudyDeckId) return null;
        
        // Create new study session
        const newSession = {
          id: `session-${Date.now()}`,
          date: new Date().toISOString(),
          deckId: activeStudyDeckId,
          ...sessionData,
        };
        
        // Update deck's lastStudied date
        const updatedDecks = decks.map(deck => 
          deck.id === activeStudyDeckId 
            ? { ...deck, lastStudied: new Date().toISOString() } 
            : deck
        );
        
        set({ 
          studySessions: [newSession, ...studySessions],
          decks: updatedDecks,
          activeStudyDeckId: null,
          activeStudyCards: [],
          currentCardIndex: 0,
        });
        
        return newSession;
      },
      
      nextCard: () => {
        const { currentCardIndex, activeStudyCards } = get();
        
        if (currentCardIndex >= activeStudyCards.length - 1) {
          return false; // No more cards
        }
        
        set({ currentCardIndex: currentCardIndex + 1 });
        return true;
      },
      
      previousCard: () => {
        const { currentCardIndex } = get();
        
        if (currentCardIndex <= 0) {
          return false; // Already at first card
        }
        
        set({ currentCardIndex: currentCardIndex - 1 });
        return true;
      },
      
      getCurrentCard: () => {
        const { activeStudyCards, currentCardIndex } = get();
        
        if (activeStudyCards.length === 0 || currentCardIndex >= activeStudyCards.length) {
          return null;
        }
        
        return activeStudyCards[currentCardIndex];
      },
      
      // Import/Export
      importFlashcards: (importedFlashcards) => {
        const { flashcards } = get();
        const existingIds = new Set(flashcards.map(card => card.id));
        
        const newFlashcards = importedFlashcards.filter(card => !existingIds.has(card.id));
        const mergedFlashcards = [...flashcards, ...newFlashcards];
        
        set({ flashcards: mergedFlashcards });
        return newFlashcards.length;
      },
      
      importDecks: (importedDecks) => {
        const { decks } = get();
        const existingIds = new Set(decks.map(deck => deck.id));
        
        const newDecks = importedDecks.filter(deck => !existingIds.has(deck.id));
        const mergedDecks = [...decks, ...newDecks];
        
        set({ decks: mergedDecks });
        return newDecks.length;
      },
      
      exportFlashcards: () => {
        return get().flashcards;
      },
      
      exportDecks: () => {
        return get().decks;
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({ 
          flashcards: [],
          decks: [],
          studySessions: [],
          activeStudyDeckId: null,
          activeStudyCards: [],
          currentCardIndex: 0,
        });
      }
    }),
    {
      name: 'flashcards-storage', // Name for localStorage
      partialize: (state) => ({ 
        flashcards: state.flashcards,
        decks: state.decks,
        studySessions: state.studySessions,
      }), // Only persist necessary state
    }
  )
);

export default useFlashcardStore;