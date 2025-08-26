import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@radix-ui/react-tabs';
import { BookOpen, Code, BrainCircuit, Lightbulb, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import JupyterNotebookGenerator from './JupyterNotebookGenerator';
import QuizModeGenerator from './QuizModeGenerator';
import AdaptiveQuizGenerator from './AdaptiveQuizGenerator';

const PracticeGenerator = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('jupyter');
  
  // Mock data for selected notes/topics
  const [selectedNotes, setSelectedNotes] = useState([
    {
      id: 1,
      title: 'Introduction to Machine Learning',
      content: 'Machine learning is a subset of artificial intelligence...',
      tags: ['ML', 'AI', 'Introduction'],
    },
    {
      id: 2,
      title: 'Neural Networks Fundamentals',
      content: 'Neural networks are computing systems inspired by biological neural networks...',
      tags: ['ML', 'Neural Networks', 'Deep Learning'],
    }
  ]);
  
  // Mock data for weak areas
  const [weakAreas, setWeakAreas] = useState([
    { id: 1, topic: 'Backpropagation', confidence: 0.3 },
    { id: 2, topic: 'Activation Functions', confidence: 0.4 },
    { id: 3, topic: 'Gradient Descent', confidence: 0.5 }
  ]);
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Practice Generator</h1>
        </div>
        <div className="text-sm text-muted-foreground">
          {selectedNotes.length} notes selected
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid grid-cols-3 mb-6">
          <TabsTrigger value="jupyter" className="flex items-center justify-center py-2">
            <Code className="h-4 w-4 mr-2" />
            Jupyter Notebook
          </TabsTrigger>
          <TabsTrigger value="quiz" className="flex items-center justify-center py-2">
            <BookOpen className="h-4 w-4 mr-2" />
            Quiz Mode
          </TabsTrigger>
          <TabsTrigger value="adaptive" className="flex items-center justify-center py-2">
            <BrainCircuit className="h-4 w-4 mr-2" />
            Adaptive Quiz
          </TabsTrigger>
        </TabsList>
        
        <div className="flex-1 overflow-auto">
          <TabsContent value="jupyter" className="h-full">
            <JupyterNotebookGenerator notes={selectedNotes} />
          </TabsContent>
          
          <TabsContent value="quiz" className="h-full">
            <QuizModeGenerator notes={selectedNotes} />
          </TabsContent>
          
          <TabsContent value="adaptive" className="h-full">
            <AdaptiveQuizGenerator notes={selectedNotes} weakAreas={weakAreas} />
          </TabsContent>
        </div>
      </Tabs>
      
      <div className="mt-6 p-4 border rounded-md bg-muted/20">
        <div className="flex items-start">
          <Lightbulb className="h-5 w-5 mr-2 text-yellow-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium mb-1">Practice Tips</h3>
            <p className="text-sm text-muted-foreground">
              {activeTab === 'jupyter' && 
                "Jupyter Notebooks are perfect for hands-on practice with code. They combine explanations with executable code blocks."}
              {activeTab === 'quiz' && 
                "Quiz Mode helps reinforce your knowledge through active recall. It converts your notes into interactive questions."}
              {activeTab === 'adaptive' && 
                "Adaptive Quizzes focus on your weak areas, helping you improve where you need it most."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PracticeGenerator;