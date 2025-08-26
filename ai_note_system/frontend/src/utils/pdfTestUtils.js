/**
 * Utility functions for testing PDF loading and rendering
 */

/**
 * Simulates loading a PDF document with specified characteristics
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.pageCount - Number of pages in the document
 * @param {boolean} options.hasText - Whether the document has selectable text
 * @param {boolean} options.hasImages - Whether the document has images
 * @param {boolean} options.hasAnnotations - Whether the document has annotations
 * @param {boolean} options.isProtected - Whether the document is password protected
 * @param {boolean} options.shouldFail - Whether the loading should fail
 * @param {string} options.errorType - Type of error if shouldFail is true
 * @returns {Promise} - Promise that resolves with the document or rejects with an error
 */
export const simulatePdfLoading = async ({
  pageCount = 10,
  hasText = true,
  hasImages = true,
  hasAnnotations = false,
  isProtected = false,
  shouldFail = false,
  errorType = 'generic',
} = {}) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Simulate loading failure if specified
  if (shouldFail) {
    const errors = {
      generic: new Error('Failed to load PDF'),
      network: new Error('Network error while loading PDF'),
      corrupt: new Error('PDF file is corrupted'),
      password: new Error('PDF is password protected'),
      unsupported: new Error('PDF format is not supported'),
    };
    
    throw errors[errorType] || errors.generic;
  }
  
  // Simulate password prompt if protected
  if (isProtected) {
    return {
      isProtected: true,
      unlock: async (password) => {
        if (password === 'correct') {
          return createMockPdfDocument(pageCount, hasText, hasImages, hasAnnotations);
        } else {
          throw new Error('Incorrect password');
        }
      }
    };
  }
  
  // Return mock PDF document
  return createMockPdfDocument(pageCount, hasText, hasImages, hasAnnotations);
};

/**
 * Creates a mock PDF document object
 * 
 * @param {number} pageCount - Number of pages
 * @param {boolean} hasText - Whether the document has text
 * @param {boolean} hasImages - Whether the document has images
 * @param {boolean} hasAnnotations - Whether the document has annotations
 * @returns {Object} - Mock PDF document
 */
const createMockPdfDocument = (pageCount, hasText, hasImages, hasAnnotations) => {
  // Create array of mock pages
  const pages = Array.from({ length: pageCount }, (_, i) => createMockPage(i + 1, hasText, hasImages));
  
  return {
    numPages: pageCount,
    fingerprint: `mock-pdf-${Date.now()}`,
    metadata: {
      title: 'Mock PDF Document',
      author: 'Test User',
      subject: 'Testing',
      keywords: 'test, mock, pdf',
      creationDate: new Date(),
      modificationDate: new Date(),
    },
    outline: [
      { title: 'Chapter 1', dest: [null, { name: 'XYZ' }, 0, 792, null], items: [] },
      { title: 'Chapter 2', dest: [null, { name: 'XYZ' }, 0, 792, null], items: [] },
    ],
    permissions: {
      canPrint: true,
      canModify: !isProtected,
      canCopy: !isProtected,
      canAnnotate: !isProtected,
    },
    getPage: (pageNumber) => {
      if (pageNumber < 1 || pageNumber > pageCount) {
        return Promise.reject(new Error(`Page ${pageNumber} does not exist`));
      }
      return Promise.resolve(pages[pageNumber - 1]);
    },
    getAnnotations: hasAnnotations ? 
      (pageNumber) => Promise.resolve(createMockAnnotations(pageNumber)) : 
      () => Promise.resolve([]),
    cleanup: () => Promise.resolve(),
  };
};

/**
 * Creates a mock PDF page
 * 
 * @param {number} pageNumber - Page number
 * @param {boolean} hasText - Whether the page has text
 * @param {boolean} hasImages - Whether the page has images
 * @returns {Object} - Mock PDF page
 */
const createMockPage = (pageNumber, hasText, hasImages) => {
  const width = 612; // Standard US Letter width in points
  const height = 792; // Standard US Letter height in points
  
  return {
    pageNumber,
    pageIndex: pageNumber - 1,
    view: [0, 0, width, height],
    getViewport: ({ scale = 1, rotation = 0 }) => ({
      width: width * scale,
      height: height * scale,
      viewBox: [0, 0, width, height],
      scale,
      rotation,
      transform: [scale, 0, 0, scale, 0, 0],
    }),
    render: ({ canvasContext, viewport }) => {
      // Simulate rendering to canvas
      canvasContext.fillStyle = '#FFFFFF';
      canvasContext.fillRect(0, 0, viewport.width, viewport.height);
      
      // Draw page border
      canvasContext.strokeStyle = '#CCCCCC';
      canvasContext.lineWidth = 1;
      canvasContext.strokeRect(1, 1, viewport.width - 2, viewport.height - 2);
      
      // Draw page number
      canvasContext.fillStyle = '#000000';
      canvasContext.font = '16px Arial';
      canvasContext.fillText(`Page ${pageNumber}`, viewport.width / 2 - 30, viewport.height - 20);
      
      // Draw mock content
      if (hasText) {
        canvasContext.font = '12px Arial';
        canvasContext.fillText(`This is mock text content for page ${pageNumber}`, 50, 50);
        canvasContext.fillText('Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 50, 70);
      }
      
      if (hasImages) {
        // Draw a mock image placeholder
        canvasContext.fillStyle = '#EEEEEE';
        canvasContext.fillRect(50, 100, 200, 150);
        canvasContext.strokeStyle = '#999999';
        canvasContext.strokeRect(50, 100, 200, 150);
        canvasContext.fillStyle = '#999999';
        canvasContext.font = '14px Arial';
        canvasContext.fillText('Mock Image', 120, 175);
      }
      
      return Promise.resolve();
    },
    getTextContent: hasText ? 
      () => Promise.resolve({
        items: [
          {
            str: `This is mock text content for page ${pageNumber}`,
            dir: 'ltr',
            transform: [12, 0, 0, 12, 50, 50],
            width: 300,
            height: 12,
          },
          {
            str: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            dir: 'ltr',
            transform: [12, 0, 0, 12, 50, 70],
            width: 400,
            height: 12,
          },
        ],
      }) : 
      () => Promise.resolve({ items: [] }),
  };
};

/**
 * Creates mock annotations for a page
 * 
 * @param {number} pageNumber - Page number
 * @returns {Array} - Array of mock annotations
 */
const createMockAnnotations = (pageNumber) => {
  return [
    {
      id: `anno-${pageNumber}-1`,
      type: 'highlight',
      rect: [50, 50, 350, 62],
      color: [1, 1, 0], // Yellow
      content: `Highlight annotation on page ${pageNumber}`,
      pageIndex: pageNumber - 1,
    },
    {
      id: `anno-${pageNumber}-2`,
      type: 'text',
      rect: [400, 100, 450, 150],
      color: [0, 0, 1], // Blue
      content: `Text note on page ${pageNumber}`,
      pageIndex: pageNumber - 1,
    },
  ];
};

/**
 * Tests PDF rendering performance
 * 
 * @param {Object} pdfDocument - PDF document to test
 * @returns {Object} - Performance metrics
 */
export const testPdfRenderingPerformance = async (pdfDocument) => {
  const metrics = {
    pageLoadTimes: [],
    averagePageLoadTime: 0,
    totalRenderTime: 0,
    memoryUsage: 0,
  };
  
  const startTime = performance.now();
  
  // Test rendering each page
  for (let i = 1; i <= pdfDocument.numPages; i++) {
    const pageStartTime = performance.now();
    const page = await pdfDocument.getPage(i);
    
    // Create a temporary canvas for rendering
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const viewport = page.getViewport({ scale: 1.0 });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    
    // Render the page
    await page.render({ canvasContext: context, viewport });
    
    const pageEndTime = performance.now();
    metrics.pageLoadTimes.push(pageEndTime - pageStartTime);
  }
  
  const endTime = performance.now();
  metrics.totalRenderTime = endTime - startTime;
  metrics.averagePageLoadTime = metrics.pageLoadTimes.reduce((sum, time) => sum + time, 0) / pdfDocument.numPages;
  
  // Estimate memory usage (this is just an approximation)
  metrics.memoryUsage = pdfDocument.numPages * (612 * 792 * 4) / (1024 * 1024); // MB
  
  return metrics;
};

/**
 * Tests text extraction from PDF
 * 
 * @param {Object} pdfDocument - PDF document to test
 * @returns {Object} - Text extraction results
 */
export const testPdfTextExtraction = async (pdfDocument) => {
  const results = {
    totalCharacters: 0,
    charactersPerPage: [],
    hasSearchableText: false,
    textExtractionTime: 0,
  };
  
  const startTime = performance.now();
  
  // Extract text from each page
  for (let i = 1; i <= pdfDocument.numPages; i++) {
    const page = await pdfDocument.getPage(i);
    const textContent = await page.getTextContent();
    
    const pageText = textContent.items.map(item => item.str).join(' ');
    results.charactersPerPage.push(pageText.length);
    results.totalCharacters += pageText.length;
  }
  
  const endTime = performance.now();
  results.textExtractionTime = endTime - startTime;
  results.hasSearchableText = results.totalCharacters > 0;
  
  return results;
};

/**
 * Tests annotation functionality
 * 
 * @param {Object} pdfDocument - PDF document to test
 * @returns {Object} - Annotation test results
 */
export const testPdfAnnotations = async (pdfDocument) => {
  const results = {
    totalAnnotations: 0,
    annotationsPerPage: [],
    annotationTypes: {},
    canAddAnnotations: pdfDocument.permissions?.canAnnotate || false,
  };
  
  // Get annotations for each page
  for (let i = 1; i <= pdfDocument.numPages; i++) {
    let pageAnnotations = [];
    
    try {
      pageAnnotations = await pdfDocument.getAnnotations(i);
    } catch (error) {
      console.error(`Error getting annotations for page ${i}:`, error);
    }
    
    results.annotationsPerPage.push(pageAnnotations.length);
    results.totalAnnotations += pageAnnotations.length;
    
    // Count annotation types
    pageAnnotations.forEach(anno => {
      results.annotationTypes[anno.type] = (results.annotationTypes[anno.type] || 0) + 1;
    });
  }
  
  return results;
};

export default {
  simulatePdfLoading,
  testPdfRenderingPerformance,
  testPdfTextExtraction,
  testPdfAnnotations,
};