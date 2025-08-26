import React, { useState } from 'react';
import { BookOpen, RefreshCw, Check, Settings, ChevronDown, Play, Edit } from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for question types
const QUESTION_TYPES = [
  { id: 'mcq', label: 'Multiple Choice', icon: '☑️' },
  { id: 'fillblank', label: 'Fill in the Blank', icon: '➖' },
  { id: 'shortanswer', label: 'Short Answer', icon: '✏️' },
  { id: 'truefalse', label: 'True/False', icon: '✓✗' },
  { id: 'matching', label: 'Matching', icon: '🔀' }
];

// Mock data for generated quiz questions
const MOCK_QUIZ_QUESTIONS = [
  {
    id: 1,
    type: 'mcq',
    question: 'Which of the following is NOT a type of machine learning?',
    options: [
      'Supervised Learning',
      'Unsupervised Learning',
      'Reinforcement Learning',
      'Prescriptive Learning'
    ],
    correctAnswer: 3,
    explanation: 'The three main types of machine learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning. Prescriptive Learning is not a standard type of machine learning.'
  },
  {
    id: 2,
    type: 'fillblank',
    question: 'In neural networks, the process of updating weights based on the gradient of the error function is called __________.',
    correctAnswer: 'backpropagation',
    explanation: 'Backpropagation is the algorithm used to calculate gradients and update weights in neural networks during training.'
  },
  {
    id: 3,
    type: 'shortanswer',
    question: 'What is overfitting in machine learning?',
    correctAnswer: 'When a model learns the training data too well, including noise and outliers, resulting in poor performance on new data.',
    explanation: 'Overfitting occurs when a model is too complex relative to the amount and noisiness of the training data, causing it to memorize the training data rather than learning general patterns.'
  },
  {
    id: 4,
    type: 'truefalse',
    question: 'Deep learning is a subset of machine learning.',
    correctAnswer: true,
    explanation: 'Deep learning is indeed a subset of machine learning that uses neural networks with many layers (deep neural networks).'
  },
  {
    id: 5,
    type: 'matching',
    question: 'Match the algorithm with its appropriate category:',
    items: [
      { item: 'K-Means', match: 'Clustering' },
      { item: 'Linear Regression', match: 'Regression' },
      { item: 'Random Forest', match: 'Classification' },
      { item: 'PCA', match: 'Dimensionality Reduction' }
    ],
    explanation: 'K-Means is a clustering algorithm, Linear Regression is used for regression tasks, Random Forest is primarily used for classification (though it can also be used for regression), and PCA (Principal Component Analysis) is used for dimensionality reduction.'
  }
];

const QuizModeGenerator = ({ notes }) => {
  const [selectedQuestionTypes, setSelectedQuestionTypes] = useState(['mcq', 'fillblank', 'shortanswer']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  
  // Options for quiz generation
  const [options, setOptions] = useState({
    questionCount: 5,
    includeExplanations: true,
    difficultyLevel: 'medium',
    timeLimit: 0 // 0 means no time limit
  });
  
  const handleOptionChange = (option, value) => {
    setOptions(prev => ({ ...prev, [option]: value }));
  };
  
  const toggleQuestionType = (typeId) => {
    setSelectedQuestionTypes(prev => 
      prev.includes(typeId)
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    );
  };
  
  const generateQuiz = async () => {
    setIsGenerating(true);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/practice/generate-quiz', { notes, questionTypes: selectedQuestionTypes, options });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Filter mock questions based on selected question types
      const filteredQuestions = MOCK_QUIZ_QUESTIONS.filter(q => 
        selectedQuestionTypes.includes(q.type)
      );
      
      // Use mock data for now
      setQuizQuestions(filteredQuestions);
      setIsGenerated(true);
      
      // Reset quiz state
      setQuizStarted(false);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setShowResults(false);
    } catch (error) {
      console.error('Error generating quiz:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const startQuiz = () => {
    setQuizStarted(true);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
  };
  
  const handleAnswer = (questionId, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };
  
  const goToNextQuestion = () => {
    if (currentQuestionIndex < quizQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      setShowResults(true);
    }
  };
  
  const goToPrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };
  
  const restartQuiz = () => {
    setQuizStarted(true);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
  };
  
  const calculateScore = () => {
    let correctCount = 0;
    
    quizQuestions.forEach(question => {
      const userAnswer = userAnswers[question.id];
      
      if (userAnswer !== undefined) {
        if (question.type === 'mcq' && userAnswer === question.correctAnswer) {
          correctCount++;
        } else if (question.type === 'fillblank' && 
                  userAnswer.toLowerCase() === question.correctAnswer.toLowerCase()) {
          correctCount++;
        } else if (question.type === 'truefalse' && userAnswer === question.correctAnswer) {
          correctCount++;
        } else if (question.type === 'matching') {
          // For matching, userAnswer would be an object with item ids as keys and match ids as values
          // This is simplified for the mock implementation
          correctCount++;
        } else if (question.type === 'shortanswer') {
          // For short answer, we would need more sophisticated checking in a real implementation
          // For now, just check if the answer contains key terms from the correct answer
          const keyTerms = question.correctAnswer.toLowerCase().split(' ');
          const containsKeyTerms = keyTerms.some(term => 
            term.length > 3 && userAnswer.toLowerCase().includes(term)
          );
          if (containsKeyTerms) correctCount++;
        }
      }
    });
    
    return {
      correct: correctCount,
      total: quizQuestions.length,
      percentage: Math.round((correctCount / quizQuestions.length) * 100)
    };
  };
  
  const renderQuestionPreview = (question) => {
    switch (question.type) {
      case 'mcq':
        return (
          <div className="mb-4">
            <p className="font-medium mb-2">{question.question}</p>
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <div key={index} className="flex items-center">
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full border mr-2 text-xs ${index === question.correctAnswer ? 'bg-green-100 border-green-500 text-green-700' : 'border-gray-300'}`}>
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span>{option}</span>
                  {index === question.correctAnswer && (
                    <span className="ml-2 text-green-600 text-sm">✓ Correct</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
        
      case 'fillblank':
        return (
          <div className="mb-4">
            <p className="font-medium mb-2">
              {question.question.replace('__________', 
                <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded border border-green-500">
                  {question.correctAnswer}
                </span>
              )}
            </p>
          </div>
        );
        
      case 'shortanswer':
        return (
          <div className="mb-4">
            <p className="font-medium mb-2">{question.question}</p>
            <div className="p-2 bg-gray-50 border rounded-md">
              <p className="text-sm italic">Sample answer: {question.correctAnswer}</p>
            </div>
          </div>
        );
        
      case 'truefalse':
        return (
          <div className="mb-4">
            <p className="font-medium mb-2">{question.question}</p>
            <div className="flex gap-4">
              <div className={`px-3 py-1 rounded-full border ${question.correctAnswer ? 'bg-green-100 border-green-500 text-green-700' : 'border-gray-300'}`}>
                True {question.correctAnswer && '✓'}
              </div>
              <div className={`px-3 py-1 rounded-full border ${!question.correctAnswer ? 'bg-green-100 border-green-500 text-green-700' : 'border-gray-300'}`}>
                False {!question.correctAnswer && '✓'}
              </div>
            </div>
          </div>
        );
        
      case 'matching':
        return (
          <div className="mb-4">
            <p className="font-medium mb-2">{question.question}</p>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-2">
                {question.items.map((item, index) => (
                  <div key={index} className="p-2 bg-gray-50 border rounded-md">
                    {item.item}
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                {question.items.map((item, index) => (
                  <div key={index} className="p-2 bg-green-50 border border-green-200 rounded-md">
                    {item.match}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
        
      default:
        return <p>Unsupported question type</p>;
    }
  };
  
  const renderQuizQuestion = (question) => {
    switch (question.type) {
      case 'mcq':
        return (
          <div>
            <p className="font-medium mb-4">{question.question}</p>
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <div 
                  key={index} 
                  className={`p-3 border rounded-md cursor-pointer hover:bg-muted/50 ${userAnswers[question.id] === index ? 'border-primary bg-primary/10' : ''}`}
                  onClick={() => handleAnswer(question.id, index)}
                >
                  <div className="flex items-center">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full border mr-2 text-xs">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span>{option}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
        
      case 'fillblank':
        return (
          <div>
            <p className="font-medium mb-4">
              {question.question.split('__________')[0]}
              <input 
                type="text" 
                className="mx-2 px-2 py-1 border-b-2 border-primary focus:outline-none focus:border-primary-dark"
                value={userAnswers[question.id] || ''}
                onChange={(e) => handleAnswer(question.id, e.target.value)}
                placeholder="Your answer"
              />
              {question.question.split('__________')[1]}
            </p>
          </div>
        );
        
      case 'shortanswer':
        return (
          <div>
            <p className="font-medium mb-4">{question.question}</p>
            <textarea 
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
              rows={4}
              value={userAnswers[question.id] || ''}
              onChange={(e) => handleAnswer(question.id, e.target.value)}
              placeholder="Type your answer here..."
            />
          </div>
        );
        
      case 'truefalse':
        return (
          <div>
            <p className="font-medium mb-4">{question.question}</p>
            <div className="flex gap-4">
              <div 
                className={`px-4 py-2 rounded-md border cursor-pointer hover:bg-muted/50 ${userAnswers[question.id] === true ? 'border-primary bg-primary/10' : ''}`}
                onClick={() => handleAnswer(question.id, true)}
              >
                True
              </div>
              <div 
                className={`px-4 py-2 rounded-md border cursor-pointer hover:bg-muted/50 ${userAnswers[question.id] === false ? 'border-primary bg-primary/10' : ''}`}
                onClick={() => handleAnswer(question.id, false)}
              >
                False
              </div>
            </div>
          </div>
        );
        
      case 'matching':
        // This would be more complex in a real implementation with drag and drop
        return (
          <div>
            <p className="font-medium mb-4">{question.question}</p>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                {question.items.map((item, index) => (
                  <div key={index} className="p-2 bg-gray-50 border rounded-md">
                    {item.item}
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                {question.items.map((item, index) => (
                  <div key={index} className="p-2 bg-gray-50 border rounded-md">
                    {item.match}
                  </div>
                ))}
              </div>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              Note: In a real implementation, this would be a drag-and-drop interface.
            </p>
          </div>
        );
        
      default:
        return <p>Unsupported question type</p>;
    }
  };
  
  const renderQuizResults = () => {
    const score = calculateScore();
    
    return (
      <div className="flex flex-col items-center">
        <h3 className="text-2xl font-bold mb-4">Quiz Results</h3>
        
        <div className="w-32 h-32 rounded-full border-8 border-primary flex items-center justify-center mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold">{score.percentage}%</div>
            <div className="text-sm text-muted-foreground">
              {score.correct}/{score.total}
            </div>
          </div>
        </div>
        
        <div className="mb-6 text-center">
          <p className="mb-2">
            {score.percentage >= 80 ? 'Great job! You have a strong understanding of this material.' :
             score.percentage >= 60 ? 'Good work! You\'re on the right track.' :
             'Keep practicing! Review the material and try again.'}
          </p>
        </div>
        
        <div className="flex gap-4">
          <Button variant="outline" onClick={restartQuiz}>
            Try Again
          </Button>
          <Button onClick={() => setQuizStarted(false)}>
            Review Questions
          </Button>
        </div>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col h-full">
      {!isGenerated ? (
        <>
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Convert Notes to Quiz</h2>
            <p className="text-muted-foreground">
              Generate interactive quizzes from your notes with different question types.
            </p>
          </div>
          
          <div className="mb-6">
            <h3 className="text-md font-medium mb-3">Select Question Types</h3>
            <div className="flex flex-wrap gap-3">
              {QUESTION_TYPES.map(type => (
                <div
                  key={type.id}
                  className={`px-3 py-2 rounded-md border cursor-pointer ${
                    selectedQuestionTypes.includes(type.id)
                      ? 'border-primary bg-primary/10'
                      : 'border-input hover:bg-muted/50'
                  }`}
                  onClick={() => toggleQuestionType(type.id)}
                >
                  <div className="flex items-center">
                    <span className="mr-2">{type.icon}</span>
                    <span>{type.label}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex justify-between items-center mb-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              disabled={isGenerating}
            >
              <Settings className="h-4 w-4 mr-1" />
              Quiz Options
              <ChevronDown className="h-4 w-4 ml-1" />
            </Button>
            
            <Button
              onClick={generateQuiz}
              disabled={isGenerating || selectedQuestionTypes.length === 0}
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <BookOpen className="h-4 w-4 mr-1" />
                  Generate Quiz
                </>
              )}
            </Button>
          </div>
          
          {showSettings && (
            <div className="mb-6 p-4 border rounded-md bg-muted/20">
              <h3 className="font-medium mb-3">Quiz Options</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="questionCount" className="block text-sm mb-1">Number of questions</label>
                  <input
                    type="number"
                    id="questionCount"
                    min="1"
                    max="20"
                    value={options.questionCount}
                    onChange={(e) => handleOptionChange('questionCount', parseInt(e.target.value))}
                    className="w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  />
                </div>
                
                <div>
                  <label htmlFor="difficultyLevel" className="block text-sm mb-1">Difficulty level</label>
                  <select
                    id="difficultyLevel"
                    value={options.difficultyLevel}
                    onChange={(e) => handleOptionChange('difficultyLevel', e.target.value)}
                    className="w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="timeLimit" className="block text-sm mb-1">Time limit (minutes, 0 for no limit)</label>
                  <input
                    type="number"
                    id="timeLimit"
                    min="0"
                    max="60"
                    value={options.timeLimit}
                    onChange={(e) => handleOptionChange('timeLimit', parseInt(e.target.value))}
                    className="w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="includeExplanations"
                    checked={options.includeExplanations}
                    onChange={(e) => handleOptionChange('includeExplanations', e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="includeExplanations" className="text-sm">Include explanations</label>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 border-2 border-dashed rounded-md">
            <BookOpen className="h-12 w-12 mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No quiz generated yet</h3>
            <p className="text-muted-foreground mb-4 max-w-md">
              Select question types and options, then click "Generate Quiz" to create an interactive quiz from your notes.
            </p>
            {notes.length > 0 && (
              <div className="text-sm text-muted-foreground">
                <p className="font-medium mb-1">Selected notes:</p>
                <ul className="list-disc list-inside">
                  {notes.map(note => (
                    <li key={note.id}>{note.title}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </>
      ) : quizStarted ? (
        showResults ? (
          renderQuizResults()
        ) : (
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-6">
              <div>
                <span className="text-sm text-muted-foreground">Question {currentQuestionIndex + 1} of {quizQuestions.length}</span>
              </div>
              <Button variant="outline" size="sm" onClick={() => setQuizStarted(false)}>
                Exit Quiz
              </Button>
            </div>
            
            <div className="flex-1 mb-6">
              {renderQuizQuestion(quizQuestions[currentQuestionIndex])}
            </div>
            
            <div className="flex justify-between">
              <Button 
                variant="outline" 
                onClick={goToPrevQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              <Button 
                onClick={goToNextQuestion}
              >
                {currentQuestionIndex === quizQuestions.length - 1 ? 'Finish' : 'Next'}
              </Button>
            </div>
          </div>
        )
      ) : (
        <div className="flex flex-col h-full">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Quiz Preview</h2>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsGenerated(false)}>
                <Edit className="h-4 w-4 mr-1" />
                Edit Quiz
              </Button>
              <Button onClick={startQuiz}>
                <Play className="h-4 w-4 mr-1" />
                Start Quiz
              </Button>
            </div>
          </div>
          
          <div className="flex-1 overflow-auto">
            <div className="border rounded-md p-4 mb-4">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="font-medium">Quiz Details</h3>
                </div>
                <div className="text-sm text-muted-foreground">
                  {quizQuestions.length} questions
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Question Types: </span>
                  {selectedQuestionTypes.map(type => 
                    QUESTION_TYPES.find(t => t.id === type)?.label
                  ).join(', ')}
                </div>
                <div>
                  <span className="font-medium">Difficulty: </span>
                  {options.difficultyLevel.charAt(0).toUpperCase() + options.difficultyLevel.slice(1)}
                </div>
                <div>
                  <span className="font-medium">Time Limit: </span>
                  {options.timeLimit > 0 ? `${options.timeLimit} minutes` : 'No time limit'}
                </div>
                <div>
                  <span className="font-medium">Explanations: </span>
                  {options.includeExplanations ? 'Included' : 'Not included'}
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              {quizQuestions.map((question, index) => (
                <div key={question.id} className="border rounded-md p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium">Question {index + 1}</h3>
                    <div className="text-xs px-2 py-0.5 bg-muted rounded-full">
                      {QUESTION_TYPES.find(t => t.id === question.type)?.label}
                    </div>
                  </div>
                  
                  {renderQuestionPreview(question)}
                  
                  {options.includeExplanations && (
                    <div className="mt-2 p-2 bg-muted/30 rounded-md">
                      <p className="text-sm font-medium">Explanation:</p>
                      <p className="text-sm">{question.explanation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizModeGenerator;