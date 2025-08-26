import React, { useState } from 'react';
import { BookOpen, RefreshCw, ChevronLeft, ChevronRight, Download, Shuffle } from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for generated flashcards
const MOCK_FLASHCARDS = [
  {
    id: 1,
    front: 'What is machine learning?',
    back: 'Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.'
  },
  {
    id: 2,
    front: 'What are the main types of machine learning?',
    back: 'The main types of machine learning are supervised learning, unsupervised learning, semi-supervised learning, and reinforcement learning.'
  },
  {
    id: 3,
    front: 'What is a neural network?',
    back: 'A neural network is a computing system inspired by biological neural networks that consists of interconnected nodes (neurons) organized in layers to process information and learn patterns.'
  },
  {
    id: 4,
    front: 'What is backpropagation?',
    back: 'Backpropagation is an algorithm used to train neural networks by calculating gradients of the loss function with respect to the weights, propagating errors backward through the network to update weights.'
  },
  {
    id: 5,
    front: 'What is overfitting?',
    back: 'Overfitting occurs when a model learns the training data too well, including its noise and outliers, resulting in poor performance on new, unseen data.'
  }
];

const FlashcardGenerator = ({ noteId, noteTitle, noteContent }) => {
  const [flashcards, setFlashcards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isViewMode, setIsViewMode] = useState(false);

  const generateFlashcards = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/notes/generate-flashcards', { noteId });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Use mock data for now
      setFlashcards(MOCK_FLASHCARDS);
      setIsViewMode(true);
      setCurrentCardIndex(0);
      setIsFlipped(false);
    } catch (err) {
      console.error('Error generating flashcards:', err);
      setError('Failed to generate flashcards. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextCard = () => {
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(prev => prev + 1);
      setIsFlipped(false);
    }
  };

  const handlePrevCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(prev => prev - 1);
      setIsFlipped(false);
    }
  };

  const handleFlipCard = () => {
    setIsFlipped(prev => !prev);
  };

  const handleShuffle = () => {
    const shuffled = [...flashcards].sort(() => Math.random() - 0.5);
    setFlashcards(shuffled);
    setCurrentCardIndex(0);
    setIsFlipped(false);
  };

  const handleExportAnki = () => {
    console.log('Exporting flashcards to Anki format');
    // Implementation for exporting to Anki
  };

  const handleBackToGenerator = () => {
    setIsViewMode(false);
  };

  const renderGeneratorView = () => (
    <div className="border rounded-md p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-md font-medium flex items-center">
          <BookOpen className="h-4 w-4 mr-2" />
          Flashcard Generator
        </h3>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={generateFlashcards}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <BookOpen className="h-4 w-4 mr-1" />
              Generate Flashcards
            </>
          )}
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-3 rounded-md mb-4">
          {error}
        </div>
      )}

      <div className="text-center py-6 text-muted-foreground">
        {isLoading ? (
          <p>Analyzing your note and generating flashcards...</p>
        ) : (
          <>
            <p className="mb-2">Generate AI-powered flashcards from your note content.</p>
            <p className="text-sm">The system will create question-answer pairs based on key concepts in your note.</p>
          </>
        )}
      </div>
    </div>
  );

  const renderFlashcardView = () => {
    const currentCard = flashcards[currentCardIndex];
    
    return (
      <div className="border rounded-md p-4">
        <div className="flex justify-between items-center mb-4">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleBackToGenerator}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <div className="text-sm text-muted-foreground">
            Card {currentCardIndex + 1} of {flashcards.length}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleShuffle}
            >
              <Shuffle className="h-4 w-4 mr-1" />
              Shuffle
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleExportAnki}
            >
              <Download className="h-4 w-4 mr-1" />
              Export to Anki
            </Button>
          </div>
        </div>

        <div 
          className="border rounded-md p-6 min-h-[200px] flex items-center justify-center cursor-pointer mb-4 transition-all duration-300 transform"
          onClick={handleFlipCard}
          style={{
            perspective: '1000px',
            transformStyle: 'preserve-3d',
            transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
          }}
        >
          <div className="text-center">
            {isFlipped ? (
              <div className="transform rotate-y-180">
                <p>{currentCard.back}</p>
                <p className="text-xs text-muted-foreground mt-4">Click to see question</p>
              </div>
            ) : (
              <div>
                <p className="font-medium text-lg">{currentCard.front}</p>
                <p className="text-xs text-muted-foreground mt-4">Click to see answer</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-between">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handlePrevCard}
            disabled={currentCardIndex === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleNextCard}
            disabled={currentCardIndex === flashcards.length - 1}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    );
  };

  return isViewMode && flashcards.length > 0 ? renderFlashcardView() : renderGeneratorView();
};

export default FlashcardGenerator;