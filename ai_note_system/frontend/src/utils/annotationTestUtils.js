/**
 * Utility functions for testing annotation and highlighting functionality
 */

/**
 * Types of annotations supported by the system
 */
export const AnnotationTypes = {
  HIGHLIGHT: 'highlight',
  NOTE: 'note',
  UNDERLINE: 'underline',
  STRIKETHROUGH: 'strikethrough',
  BOOKMARK: 'bookmark',
  FLASHCARD: 'flashcard',
};

/**
 * Colors available for annotations
 */
export const AnnotationColors = {
  YELLOW: 'rgba(255, 255, 0, 0.3)',
  GREEN: 'rgba(0, 255, 0, 0.3)',
  BLUE: 'rgba(0, 0, 255, 0.3)',
  PINK: 'rgba(255, 0, 255, 0.3)',
  RED: 'rgba(255, 0, 0, 0.3)',
};

/**
 * Creates a mock text selection for testing
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.text - Selected text
 * @param {number} options.pageNumber - Page number where selection occurs
 * @param {Object} options.position - Position of the selection on the page
 * @param {Object} options.boundingRect - Bounding rectangle of the selection
 * @returns {Object} - Mock selection object
 */
export const createMockSelection = ({
  text = 'This is selected text',
  pageNumber = 1,
  position = { x: 100, y: 200 },
  boundingRect = { x: 100, y: 200, width: 300, height: 20 },
} = {}) => {
  return {
    text,
    pageNumber,
    position,
    boundingRect,
    rects: [boundingRect],
    toString: () => text,
    getRangeAt: () => ({
      getBoundingClientRect: () => boundingRect,
      getClientRects: () => [boundingRect],
    }),
  };
};

/**
 * Creates a mock annotation for testing
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.id - Annotation ID
 * @param {string} options.type - Type of annotation
 * @param {string} options.text - Text content of the annotation
 * @param {number} options.pageNumber - Page number where annotation occurs
 * @param {string} options.color - Color of the annotation
 * @param {Object} options.position - Position of the annotation on the page
 * @param {Object} options.boundingRect - Bounding rectangle of the annotation
 * @param {string} options.note - Optional note attached to the annotation
 * @param {Object} options.flashcardData - Optional flashcard data for flashcard annotations
 * @returns {Object} - Mock annotation object
 */
export const createMockAnnotation = ({
  id = `anno-${Date.now()}`,
  type = AnnotationTypes.HIGHLIGHT,
  text = 'This is annotated text',
  pageNumber = 1,
  color = AnnotationColors.YELLOW,
  position = { x: 100, y: 200 },
  boundingRect = { x: 100, y: 200, width: 300, height: 20 },
  note = '',
  flashcardData = null,
} = {}) => {
  return {
    id,
    type,
    text,
    pageNumber,
    color,
    position,
    boundingRect,
    rects: [boundingRect],
    note,
    flashcardData,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
};

/**
 * Simulates user highlighting text
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.selection - Text selection (use createMockSelection)
 * @param {string} options.type - Type of annotation to create
 * @param {string} options.color - Color of the annotation
 * @param {string} options.note - Optional note to attach
 * @returns {Object} - Created annotation
 */
export const simulateHighlightCreation = ({
  selection,
  type = AnnotationTypes.HIGHLIGHT,
  color = AnnotationColors.YELLOW,
  note = '',
} = {}) => {
  if (!selection) {
    throw new Error('Selection is required to create a highlight');
  }

  return createMockAnnotation({
    type,
    text: selection.text,
    pageNumber: selection.pageNumber,
    color,
    position: selection.position,
    boundingRect: selection.boundingRect,
    note,
  });
};

/**
 * Simulates creating a flashcard from a text selection
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.selection - Text selection (use createMockSelection)
 * @param {string} options.front - Front side of the flashcard (question)
 * @param {string} options.back - Back side of the flashcard (answer)
 * @param {string} options.color - Color of the highlight
 * @returns {Object} - Created annotation with flashcard data
 */
export const simulateFlashcardCreation = ({
  selection,
  front = '',
  back = '',
  color = AnnotationColors.GREEN,
} = {}) => {
  if (!selection) {
    throw new Error('Selection is required to create a flashcard');
  }

  // If front is not provided, use the selected text
  const frontText = front || selection.text;
  const backText = back || 'Answer for: ' + selection.text;

  return createMockAnnotation({
    type: AnnotationTypes.FLASHCARD,
    text: selection.text,
    pageNumber: selection.pageNumber,
    color,
    position: selection.position,
    boundingRect: selection.boundingRect,
    flashcardData: {
      front: frontText,
      back: backText,
      difficulty: 'medium',
      tags: [],
      nextReviewDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 1 day from now
    },
  });
};

/**
 * Tests annotation rendering
 * 
 * @param {Array} annotations - Array of annotations to test
 * @param {Function} renderFunction - Function that renders annotations
 * @returns {Object} - Test results
 */
export const testAnnotationRendering = (annotations, renderFunction) => {
  const results = {
    totalAnnotations: annotations.length,
    renderedAnnotations: 0,
    renderingErrors: [],
    annotationsByType: {},
    annotationsByPage: {},
  };

  // Count annotations by type
  annotations.forEach(anno => {
    results.annotationsByType[anno.type] = (results.annotationsByType[anno.type] || 0) + 1;
    results.annotationsByPage[anno.pageNumber] = (results.annotationsByPage[anno.pageNumber] || 0) + 1;
  });

  // Test rendering each annotation
  annotations.forEach(anno => {
    try {
      renderFunction(anno);
      results.renderedAnnotations++;
    } catch (error) {
      results.renderingErrors.push({
        annotation: anno,
        error: error.message,
      });
    }
  });

  return results;
};

/**
 * Tests annotation interaction (hover, click, edit, delete)
 * 
 * @param {Array} annotations - Array of annotations to test
 * @param {Object} handlers - Object containing interaction handler functions
 * @returns {Object} - Test results
 */
export const testAnnotationInteraction = (annotations, handlers) => {
  const {
    onHover,
    onClick,
    onEdit,
    onDelete,
  } = handlers;

  const results = {
    hoverTests: { success: 0, failure: 0, errors: [] },
    clickTests: { success: 0, failure: 0, errors: [] },
    editTests: { success: 0, failure: 0, errors: [] },
    deleteTests: { success: 0, failure: 0, errors: [] },
  };

  // Test hover interaction
  if (onHover) {
    annotations.forEach(anno => {
      try {
        const hoverResult = onHover(anno);
        if (hoverResult) {
          results.hoverTests.success++;
        } else {
          results.hoverTests.failure++;
        }
      } catch (error) {
        results.hoverTests.errors.push({
          annotation: anno,
          error: error.message,
        });
        results.hoverTests.failure++;
      }
    });
  }

  // Test click interaction
  if (onClick) {
    annotations.forEach(anno => {
      try {
        const clickResult = onClick(anno);
        if (clickResult) {
          results.clickTests.success++;
        } else {
          results.clickTests.failure++;
        }
      } catch (error) {
        results.clickTests.errors.push({
          annotation: anno,
          error: error.message,
        });
        results.clickTests.failure++;
      }
    });
  }

  // Test edit interaction
  if (onEdit) {
    annotations.forEach(anno => {
      try {
        const updatedAnno = { ...anno, note: 'Updated note for testing' };
        const editResult = onEdit(anno, updatedAnno);
        if (editResult) {
          results.editTests.success++;
        } else {
          results.editTests.failure++;
        }
      } catch (error) {
        results.editTests.errors.push({
          annotation: anno,
          error: error.message,
        });
        results.editTests.failure++;
      }
    });
  }

  // Test delete interaction
  if (onDelete) {
    annotations.forEach(anno => {
      try {
        const deleteResult = onDelete(anno);
        if (deleteResult) {
          results.deleteTests.success++;
        } else {
          results.deleteTests.failure++;
        }
      } catch (error) {
        results.deleteTests.errors.push({
          annotation: anno,
          error: error.message,
        });
        results.deleteTests.failure++;
      }
    });
  }

  return results;
};

/**
 * Tests text selection and highlighting
 * 
 * @param {Function} onSelectionChange - Function called when selection changes
 * @param {Function} onHighlightCreate - Function called to create a highlight
 * @returns {Object} - Test results
 */
export const testTextSelection = (onSelectionChange, onHighlightCreate) => {
  const results = {
    selectionTests: { success: 0, failure: 0, errors: [] },
    highlightTests: { success: 0, failure: 0, errors: [] },
  };

  // Test different selection scenarios
  const testSelections = [
    createMockSelection({ text: 'Short selection' }),
    createMockSelection({ 
      text: 'Long selection spanning multiple lines of text that might wrap around and cause rendering issues if not handled properly',
      boundingRect: { x: 100, y: 200, width: 500, height: 40 },
    }),
    createMockSelection({ 
      text: 'Selection with special characters: !@#$%^&*()',
      boundingRect: { x: 150, y: 300, width: 400, height: 20 },
    }),
  ];

  // Test selection change
  testSelections.forEach(selection => {
    try {
      const selectionResult = onSelectionChange(selection);
      if (selectionResult) {
        results.selectionTests.success++;
      } else {
        results.selectionTests.failure++;
      }
    } catch (error) {
      results.selectionTests.errors.push({
        selection,
        error: error.message,
      });
      results.selectionTests.failure++;
    }
  });

  // Test highlight creation
  if (onHighlightCreate) {
    const testColors = [
      AnnotationColors.YELLOW,
      AnnotationColors.GREEN,
      AnnotationColors.BLUE,
      AnnotationColors.PINK,
      AnnotationColors.RED,
    ];

    testSelections.forEach((selection, i) => {
      try {
        const color = testColors[i % testColors.length];
        const highlightResult = onHighlightCreate(selection, color);
        if (highlightResult) {
          results.highlightTests.success++;
        } else {
          results.highlightTests.failure++;
        }
      } catch (error) {
        results.highlightTests.errors.push({
          selection,
          error: error.message,
        });
        results.highlightTests.failure++;
      }
    });
  }

  return results;
};

/**
 * Tests flashcard creation from highlights
 * 
 * @param {Array} annotations - Array of annotations to test
 * @param {Function} createFlashcard - Function to create a flashcard from an annotation
 * @returns {Object} - Test results
 */
export const testFlashcardCreation = (annotations, createFlashcard) => {
  const results = {
    totalTests: annotations.length,
    success: 0,
    failure: 0,
    errors: [],
    createdFlashcards: [],
  };

  annotations.forEach(anno => {
    try {
      const flashcardData = {
        front: `Question about: ${anno.text}`,
        back: `Answer about: ${anno.text}`,
        difficulty: 'medium',
        tags: ['test'],
      };
      
      const flashcard = createFlashcard(anno, flashcardData);
      
      if (flashcard) {
        results.success++;
        results.createdFlashcards.push(flashcard);
      } else {
        results.failure++;
      }
    } catch (error) {
      results.errors.push({
        annotation: anno,
        error: error.message,
      });
      results.failure++;
    }
  });

  return results;
};

export default {
  AnnotationTypes,
  AnnotationColors,
  createMockSelection,
  createMockAnnotation,
  simulateHighlightCreation,
  simulateFlashcardCreation,
  testAnnotationRendering,
  testAnnotationInteraction,
  testTextSelection,
  testFlashcardCreation,
};