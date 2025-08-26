import React, { useState } from 'react';
import { Code, Download, RefreshCw, Check, Settings, ChevronDown } from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for programming languages and frameworks
const PROGRAMMING_LANGUAGES = ['Python', 'R', 'Julia'];
const FRAMEWORKS = {
  'Python': ['None', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy'],
  'R': ['None', 'Tidyverse', 'ggplot2', 'caret'],
  'Julia': ['None', 'Flux.jl', 'MLJ.jl']
};

// Mock Jupyter notebook cell content
const MOCK_NOTEBOOK_CELLS = [
  {
    type: 'markdown',
    content: '# Introduction to Machine Learning\n\nMachine learning is a subset of artificial intelligence that focuses on developing systems that learn from data.'
  },
  {
    type: 'code',
    content: '# Import necessary libraries\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n# Set up plotting\nplt.style.use("seaborn-whitegrid")\nplt.rc("figure", figsize=(10, 6))\nplt.rc("axes", grid=True)'
  },
  {
    type: 'markdown',
    content: '## Key Concepts in Machine Learning\n\n1. **Supervised Learning**: Learning from labeled data\n2. **Unsupervised Learning**: Finding patterns in unlabeled data\n3. **Reinforcement Learning**: Learning through interaction with an environment'
  },
  {
    type: 'code',
    content: '# Example of a simple machine learning model\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.datasets import make_classification\n\n# Generate a synthetic dataset\nX, y = make_classification(n_samples=1000, n_features=20, n_informative=10, random_state=42)\n\n# Create and train a model\nmodel = RandomForestClassifier(n_estimators=100, random_state=42)\nmodel.fit(X, y)\n\n# Print model accuracy\nprint(f"Model accuracy: {model.score(X, y):.2f}")'
  },
  {
    type: 'markdown',
    content: '## Neural Networks Fundamentals\n\nNeural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes (neurons).'
  },
  {
    type: 'code',
    content: '# Example of a simple neural network using TensorFlow/Keras\nimport tensorflow as tf\nfrom tensorflow.keras.models import Sequential\nfrom tensorflow.keras.layers import Dense\n\n# Create a simple neural network\nmodel = Sequential([\n    Dense(64, activation="relu", input_shape=(20,)),\n    Dense(32, activation="relu"),\n    Dense(1, activation="sigmoid")\n])\n\n# Compile the model\nmodel.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])\n\n# Print model summary\nmodel.summary()'
  }
];

const JupyterNotebookGenerator = ({ notes }) => {
  const [language, setLanguage] = useState('Python');
  const [framework, setFramework] = useState('None');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [notebookCells, setNotebookCells] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  
  // Options for notebook generation
  const [options, setOptions] = useState({
    includeExamples: true,
    includeExercises: true,
    includeVisualization: true,
    difficultyLevel: 'intermediate'
  });
  
  const handleOptionChange = (option, value) => {
    setOptions(prev => ({ ...prev, [option]: value }));
  };
  
  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    setFramework(FRAMEWORKS[newLanguage][0]);
  };
  
  const handleFrameworkChange = (e) => {
    setFramework(e.target.value);
  };
  
  const generateNotebook = async () => {
    setIsGenerating(true);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/practice/generate-notebook', { notes, language, framework, options });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Use mock data for now
      setNotebookCells(MOCK_NOTEBOOK_CELLS);
      setIsGenerated(true);
    } catch (error) {
      console.error('Error generating notebook:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const downloadNotebook = () => {
    // In a real implementation, this would create and download a .ipynb file
    // For now, we'll just create a JSON representation of the notebook
    
    const notebook = {
      metadata: {
        kernelspec: {
          display_name: language,
          language: language.toLowerCase(),
          name: language.toLowerCase()
        },
        language_info: {
          name: language.toLowerCase(),
          version: language === 'Python' ? '3.8.10' : (language === 'R' ? '4.1.0' : '1.6.0')
        }
      },
      nbformat: 4,
      nbformat_minor: 5,
      cells: notebookCells.map(cell => ({
        cell_type: cell.type,
        metadata: {},
        source: cell.content.split('\n'),
        execution_count: cell.type === 'code' ? 1 : null,
        outputs: cell.type === 'code' ? [] : undefined
      }))
    };
    
    const blob = new Blob([JSON.stringify(notebook, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${notes[0]?.title || 'notebook'}.ipynb`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);
  };
  
  const renderNotebookPreview = () => {
    return (
      <div className="border rounded-md overflow-hidden">
        {notebookCells.map((cell, index) => (
          <div key={index} className={`p-4 ${index % 2 === 0 ? 'bg-muted/30' : 'bg-background'}`}>
            <div className="flex items-center text-xs text-muted-foreground mb-1">
              {cell.type === 'code' ? (
                <div className="flex items-center">
                  <Code className="h-3 w-3 mr-1" />
                  <span>Code Cell</span>
                </div>
              ) : (
                <div className="flex items-center">
                  <span>Markdown Cell</span>
                </div>
              )}
            </div>
            <div className={`font-mono text-sm ${cell.type === 'code' ? 'bg-muted p-2 rounded' : ''}`}>
              <pre className="whitespace-pre-wrap">{cell.content}</pre>
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Convert Theory to Jupyter Notebook</h2>
        <p className="text-muted-foreground">
          Generate interactive Jupyter notebooks from your notes with explanations and executable code.
        </p>
      </div>
      
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">Programming Language</label>
          <select 
            value={language}
            onChange={handleLanguageChange}
            className="w-40 rounded-md border border-input bg-background px-3 py-2 text-sm"
            disabled={isGenerating}
          >
            {PROGRAMMING_LANGUAGES.map(lang => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Framework</label>
          <select 
            value={framework}
            onChange={handleFrameworkChange}
            className="w-40 rounded-md border border-input bg-background px-3 py-2 text-sm"
            disabled={isGenerating}
          >
            {FRAMEWORKS[language].map(fw => (
              <option key={fw} value={fw}>{fw}</option>
            ))}
          </select>
        </div>
        
        <div className="ml-auto">
          <label className="block text-sm font-medium mb-1 opacity-0">Actions</label>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
              disabled={isGenerating}
            >
              <Settings className="h-4 w-4 mr-1" />
              Options
              <ChevronDown className="h-4 w-4 ml-1" />
            </Button>
            
            <Button
              onClick={generateNotebook}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Code className="h-4 w-4 mr-1" />
                  Generate Notebook
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
      
      {showSettings && (
        <div className="mb-6 p-4 border rounded-md bg-muted/20">
          <h3 className="font-medium mb-3">Notebook Options</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeExamples"
                checked={options.includeExamples}
                onChange={(e) => handleOptionChange('includeExamples', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeExamples" className="text-sm">Include code examples</label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeExercises"
                checked={options.includeExercises}
                onChange={(e) => handleOptionChange('includeExercises', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeExercises" className="text-sm">Include practice exercises</label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeVisualization"
                checked={options.includeVisualization}
                onChange={(e) => handleOptionChange('includeVisualization', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeVisualization" className="text-sm">Include data visualizations</label>
            </div>
            
            <div>
              <label htmlFor="difficultyLevel" className="block text-sm mb-1">Difficulty level</label>
              <select
                id="difficultyLevel"
                value={options.difficultyLevel}
                onChange={(e) => handleOptionChange('difficultyLevel', e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
        </div>
      )}
      
      <div className="flex-1 overflow-auto">
        {isGenerated ? (
          <>
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center text-green-600">
                <Check className="h-4 w-4 mr-1" />
                <span className="text-sm font-medium">Notebook generated successfully</span>
              </div>
              <Button variant="outline" size="sm" onClick={downloadNotebook}>
                <Download className="h-4 w-4 mr-1" />
                Download .ipynb
              </Button>
            </div>
            {renderNotebookPreview()}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center p-8 border-2 border-dashed rounded-md">
            <Code className="h-12 w-12 mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No notebook generated yet</h3>
            <p className="text-muted-foreground mb-4 max-w-md">
              Select your programming language and framework, then click "Generate Notebook" to create a Jupyter notebook from your notes.
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
        )}
      </div>
    </div>
  );
};

export default JupyterNotebookGenerator;