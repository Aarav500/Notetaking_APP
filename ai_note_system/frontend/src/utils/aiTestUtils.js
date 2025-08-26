/**
 * Utility functions for testing AI features and flashcard creation
 */
import api from '@/lib/api';

/**
 * AI feature types supported by the system
 */
export const AIFeatureTypes = {
  SUMMARIZE_TEXT: 'summarizeText',
  SUMMARIZE_PAGE: 'summarizePage',
  SUMMARIZE_BOOK: 'summarizeBook',
  ASK_QUESTION: 'askQuestion',
  GENERATE_FLASHCARDS: 'generateFlashcards',
  GENERATE_FLASHCARDS_FROM_PAGE: 'generateFlashcardsFromPage',
  GENERATE_KNOWLEDGE_GRAPH: 'generateKnowledgeGraph',
};

/**
 * Difficulty levels for flashcards
 */
export const FlashcardDifficulty = {
  EASY: 'easy',
  MEDIUM: 'medium',
  HARD: 'hard',
};

/**
 * Creates a mock text sample for testing
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.topic - Topic of the text
 * @param {number} options.paragraphs - Number of paragraphs to generate
 * @param {boolean} options.includeHeadings - Whether to include headings
 * @param {boolean} options.includeKeyTerms - Whether to include key terms
 * @returns {string} - Generated text
 */
export const createMockText = ({
  topic = 'machine learning',
  paragraphs = 3,
  includeHeadings = true,
  includeKeyTerms = true,
} = {}) => {
  // Sample text templates based on topic
  const topics = {
    'machine learning': {
      title: 'Introduction to Machine Learning',
      paragraphs: [
        'Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data. Unlike traditional programming, where explicit instructions are provided, machine learning algorithms build models based on sample data to make predictions or decisions without being explicitly programmed to do so.',
        'There are several types of machine learning approaches. Supervised learning involves training a model on labeled data, where the desired output is known. Unsupervised learning involves finding patterns or relationships in data without labeled responses. Reinforcement learning involves training agents to make sequences of decisions by rewarding desired behaviors.',
        'Common machine learning algorithms include linear regression, logistic regression, decision trees, random forests, support vector machines, k-nearest neighbors, and neural networks. Each algorithm has its strengths and weaknesses, making them suitable for different types of problems and datasets.',
        'Deep learning is a subset of machine learning that uses neural networks with many layers (deep neural networks). These networks can automatically learn hierarchical features from data, making them particularly effective for tasks like image recognition, natural language processing, and speech recognition.',
      ],
      keyTerms: [
        { term: 'Supervised Learning', definition: 'A type of machine learning where the model is trained on labeled data' },
        { term: 'Unsupervised Learning', definition: 'A type of machine learning where the model finds patterns in unlabeled data' },
        { term: 'Neural Network', definition: 'A computational model inspired by the human brain that consists of interconnected nodes (neurons)' },
        { term: 'Overfitting', definition: 'When a model learns the training data too well, including its noise and outliers' },
      ],
    },
    'react': {
      title: 'React: A JavaScript Library for Building User Interfaces',
      paragraphs: [
        'React is a JavaScript library for building user interfaces, particularly single-page applications. It is maintained by Facebook and a community of individual developers and companies. React can be used as a base in the development of single-page or mobile applications.',
        'React uses a declarative paradigm that makes it easier to reason about your application and aims to be both efficient and flexible. It designs simple views for each state in your application, and React will efficiently update and render just the right components when your data changes.',
        'One of the key features of React is the concept of components. Components are reusable pieces of code that return React elements describing what should appear on the screen. They can accept inputs, called props, and return React elements describing what should appear on the screen.',
        'React also introduces the concept of the Virtual DOM. Instead of updating the browser DOM directly, React creates a virtual representation of the DOM in memory and uses a diffing algorithm to determine the most efficient way to update the browser DOM.',
      ],
      keyTerms: [
        { term: 'Component', definition: 'A reusable piece of code that returns React elements' },
        { term: 'Props', definition: 'Inputs that components can accept' },
        { term: 'State', definition: 'An object that determines how a component renders and behaves' },
        { term: 'Virtual DOM', definition: 'A programming concept where a virtual representation of a UI is kept in memory' },
      ],
    },
    'data structures': {
      title: 'Introduction to Data Structures',
      paragraphs: [
        'Data structures are specialized formats for organizing, processing, retrieving, and storing data. They provide a way to manage large amounts of data efficiently for uses such as large databases and internet indexing services. Different kinds of data structures are suited to different kinds of applications, and some are highly specialized to specific tasks.',
        'Arrays are a simple data structure that stores elements of the same type in contiguous memory locations. They provide O(1) access time to any element if the index is known. However, insertion and deletion operations can be costly as they may require shifting elements.',
        'Linked lists consist of nodes where each node contains data and a reference to the next node in the sequence. They allow for efficient insertion and deletion operations but have O(n) access time as you need to traverse the list from the beginning to find a specific element.',
        'Trees are hierarchical data structures with a root value and subtrees of children with a parent node. They are used for representing hierarchical relationships and for efficient searching and sorting. Common types include binary trees, binary search trees, AVL trees, and B-trees.',
      ],
      keyTerms: [
        { term: 'Array', definition: 'A collection of elements stored at contiguous memory locations' },
        { term: 'Linked List', definition: 'A linear data structure where elements are not stored at contiguous locations' },
        { term: 'Tree', definition: 'A hierarchical data structure with a root value and subtrees of children' },
        { term: 'Graph', definition: 'A non-linear data structure consisting of nodes and edges' },
      ],
    },
  };

  // Use the specified topic or default to machine learning
  const topicData = topics[topic.toLowerCase()] || topics['machine learning'];
  
  let result = '';
  
  // Add title if headings are included
  if (includeHeadings) {
    result += `# ${topicData.title}\n\n`;
  }
  
  // Add paragraphs
  const availableParagraphs = topicData.paragraphs;
  for (let i = 0; i < Math.min(paragraphs, availableParagraphs.length); i++) {
    if (includeHeadings && i > 0 && i % 2 === 0) {
      // Add subheading every 2 paragraphs
      result += `## Section ${Math.ceil(i/2)}\n\n`;
    }
    result += `${availableParagraphs[i]}\n\n`;
  }
  
  // Add key terms if requested
  if (includeKeyTerms) {
    result += '## Key Terms\n\n';
    topicData.keyTerms.forEach(({ term, definition }) => {
      result += `- **${term}**: ${definition}\n`;
    });
  }
  
  return result;
};

/**
 * Creates a mock book for testing
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.id - Book ID
 * @param {string} options.title - Book title
 * @param {string} options.author - Book author
 * @param {number} options.pages - Number of pages
 * @returns {Object} - Mock book object
 */
export const createMockBook = ({
  id = 1,
  title = 'Machine Learning Fundamentals',
  author = 'Alex Johnson',
  pages = 10,
} = {}) => {
  return {
    id,
    title,
    author,
    coverImage: 'https://via.placeholder.com/150x200?text=Book+Cover',
    totalPages: pages,
    currentPage: 1,
    lastRead: new Date().toISOString(),
    progress: 0,
    format: 'pdf',
    path: `/documents/book-${id}.pdf`,
  };
};

/**
 * Tests text summarization
 * 
 * @param {string} text - Text to summarize
 * @returns {Promise<Object>} - Test results
 */
export const testTextSummarization = async (text) => {
  const results = {
    success: false,
    summary: null,
    keyPoints: [],
    error: null,
    executionTime: 0,
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.summarizeText(text);
    results.success = true;
    results.summary = response.data.summary;
    results.keyPoints = response.data.keyPoints || [];
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests page summarization
 * 
 * @param {number} bookId - Book ID
 * @param {number} page - Page number
 * @returns {Promise<Object>} - Test results
 */
export const testPageSummarization = async (bookId, page) => {
  const results = {
    success: false,
    summary: null,
    keyPoints: [],
    error: null,
    executionTime: 0,
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.summarizePage({ bookId }, { page });
    results.success = true;
    results.summary = response.data.summary;
    results.keyPoints = response.data.keyPoints || [];
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests question answering
 * 
 * @param {string} question - Question to ask
 * @param {string} context - Context for the question
 * @returns {Promise<Object>} - Test results
 */
export const testQuestionAnswering = async (question, context) => {
  const results = {
    success: false,
    answer: null,
    confidence: 0,
    relatedQuestions: [],
    error: null,
    executionTime: 0,
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.askQuestion({ question }, { context });
    results.success = true;
    results.answer = response.data.answer;
    results.confidence = response.data.confidence || 0;
    results.relatedQuestions = response.data.relatedQuestions || [];
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests flashcard generation from text
 * 
 * @param {string} text - Text to generate flashcards from
 * @param {Object} options - Generation options
 * @returns {Promise<Object>} - Test results
 */
export const testFlashcardGeneration = async (text, options = {}) => {
  const results = {
    success: false,
    flashcards: [],
    error: null,
    executionTime: 0,
    qualityMetrics: {
      avgQuestionLength: 0,
      avgAnswerLength: 0,
      difficultyDistribution: {
        easy: 0,
        medium: 0,
        hard: 0,
      },
    },
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.generateFlashcards(text, options);
    results.success = true;
    results.flashcards = response.data.flashcards || [];
    
    // Calculate quality metrics
    if (results.flashcards.length > 0) {
      const questionLengths = results.flashcards.map(card => card.front.length);
      const answerLengths = results.flashcards.map(card => card.back.length);
      
      results.qualityMetrics.avgQuestionLength = questionLengths.reduce((sum, len) => sum + len, 0) / questionLengths.length;
      results.qualityMetrics.avgAnswerLength = answerLengths.reduce((sum, len) => sum + len, 0) / answerLengths.length;
      
      // Count difficulty distribution
      results.flashcards.forEach(card => {
        results.qualityMetrics.difficultyDistribution[card.difficulty] = 
          (results.qualityMetrics.difficultyDistribution[card.difficulty] || 0) + 1;
      });
    }
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests flashcard generation from a page
 * 
 * @param {number} bookId - Book ID
 * @param {number} page - Page number
 * @param {Object} options - Generation options
 * @returns {Promise<Object>} - Test results
 */
export const testFlashcardGenerationFromPage = async (bookId, page, options = {}) => {
  const results = {
    success: false,
    flashcards: [],
    error: null,
    executionTime: 0,
    qualityMetrics: {
      avgQuestionLength: 0,
      avgAnswerLength: 0,
      difficultyDistribution: {
        easy: 0,
        medium: 0,
        hard: 0,
      },
    },
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.generateFlashcardsFromPage({ bookId }, { page }, options);
    results.success = true;
    results.flashcards = response.data.flashcards || [];
    
    // Calculate quality metrics
    if (results.flashcards.length > 0) {
      const questionLengths = results.flashcards.map(card => card.front.length);
      const answerLengths = results.flashcards.map(card => card.back.length);
      
      results.qualityMetrics.avgQuestionLength = questionLengths.reduce((sum, len) => sum + len, 0) / questionLengths.length;
      results.qualityMetrics.avgAnswerLength = answerLengths.reduce((sum, len) => sum + len, 0) / answerLengths.length;
      
      // Count difficulty distribution
      results.flashcards.forEach(card => {
        results.qualityMetrics.difficultyDistribution[card.difficulty] = 
          (results.qualityMetrics.difficultyDistribution[card.difficulty] || 0) + 1;
      });
    }
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests knowledge graph generation
 * 
 * @param {Array<number>} noteIds - Array of note IDs
 * @returns {Promise<Object>} - Test results
 */
export const testKnowledgeGraphGeneration = async (noteIds) => {
  const results = {
    success: false,
    graph: null,
    nodes: 0,
    edges: 0,
    error: null,
    executionTime: 0,
  };
  
  const startTime = performance.now();
  
  try {
    const response = await api.ai.generateKnowledgeGraph({ noteIds });
    results.success = true;
    results.graph = response.data.graph;
    results.nodes = response.data.graph?.nodes?.length || 0;
    results.edges = response.data.graph?.edges?.length || 0;
    results.concepts = response.data.concepts || 0;
    results.relationships = response.data.relationships || 0;
  } catch (error) {
    results.success = false;
    results.error = error.message;
  }
  
  const endTime = performance.now();
  results.executionTime = endTime - startTime;
  
  return results;
};

/**
 * Tests all AI features with sample data
 * 
 * @returns {Promise<Object>} - Comprehensive test results
 */
export const testAllAIFeatures = async () => {
  const results = {
    summarization: {
      text: null,
      page: null,
    },
    questionAnswering: null,
    flashcardGeneration: {
      fromText: null,
      fromPage: null,
    },
    knowledgeGraph: null,
    overallSuccess: false,
    totalExecutionTime: 0,
  };
  
  const startTime = performance.now();
  
  // Test text summarization
  const sampleText = createMockText({ paragraphs: 4, includeHeadings: true });
  results.summarization.text = await testTextSummarization(sampleText);
  
  // Test page summarization
  results.summarization.page = await testPageSummarization(1, 1);
  
  // Test question answering
  results.questionAnswering = await testQuestionAnswering(
    'What are the main types of machine learning?',
    sampleText
  );
  
  // Test flashcard generation from text
  results.flashcardGeneration.fromText = await testFlashcardGeneration(
    sampleText,
    { count: 5 }
  );
  
  // Test flashcard generation from page
  results.flashcardGeneration.fromPage = await testFlashcardGenerationFromPage(
    1, 1, { count: 3 }
  );
  
  // Test knowledge graph generation
  results.knowledgeGraph = await testKnowledgeGraphGeneration([1, 2]);
  
  const endTime = performance.now();
  results.totalExecutionTime = endTime - startTime;
  
  // Calculate overall success
  const featureResults = [
    results.summarization.text.success,
    results.summarization.page.success,
    results.questionAnswering.success,
    results.flashcardGeneration.fromText.success,
    results.flashcardGeneration.fromPage.success,
    results.knowledgeGraph.success,
  ];
  
  const successCount = featureResults.filter(Boolean).length;
  results.overallSuccess = successCount === featureResults.length;
  results.successRate = (successCount / featureResults.length) * 100;
  
  return results;
};

export default {
  AIFeatureTypes,
  FlashcardDifficulty,
  createMockText,
  createMockBook,
  testTextSummarization,
  testPageSummarization,
  testQuestionAnswering,
  testFlashcardGeneration,
  testFlashcardGenerationFromPage,
  testKnowledgeGraphGeneration,
  testAllAIFeatures,
};