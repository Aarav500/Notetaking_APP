import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Mock data for initial visualizations
const initialVisualizations = [
  {
    id: 1,
    title: 'Machine Learning Concepts',
    type: 'mindmap',
    date: '2025-07-28',
    sourceNote: 'Machine Learning Fundamentals',
    sourceNoteId: 1,
    thumbnail: 'https://via.placeholder.com/400x250?text=Mind+Map',
    description: 'Mind map of key machine learning concepts and their relationships',
    data: {
      // This would contain the actual visualization data structure
      // For a mind map, it might be a tree structure with nodes and connections
      nodes: [
        { id: 'root', label: 'Machine Learning', x: 400, y: 250 },
        { id: 'supervised', label: 'Supervised Learning', x: 200, y: 150 },
        { id: 'unsupervised', label: 'Unsupervised Learning', x: 600, y: 150 },
        { id: 'reinforcement', label: 'Reinforcement Learning', x: 400, y: 400 },
        { id: 'classification', label: 'Classification', x: 100, y: 250 },
        { id: 'regression', label: 'Regression', x: 300, y: 250 },
        { id: 'clustering', label: 'Clustering', x: 500, y: 250 },
        { id: 'dim-reduction', label: 'Dimensionality Reduction', x: 700, y: 250 },
      ],
      edges: [
        { source: 'root', target: 'supervised' },
        { source: 'root', target: 'unsupervised' },
        { source: 'root', target: 'reinforcement' },
        { source: 'supervised', target: 'classification' },
        { source: 'supervised', target: 'regression' },
        { source: 'unsupervised', target: 'clustering' },
        { source: 'unsupervised', target: 'dim-reduction' },
      ]
    }
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
    data: {
      // For a flowchart, it might be a directed graph with nodes and edges
      nodes: [
        { id: 'input', label: 'Input Layer', type: 'input', x: 100, y: 250 },
        { id: 'hidden1', label: 'Hidden Layer 1', type: 'process', x: 250, y: 250 },
        { id: 'hidden2', label: 'Hidden Layer 2', type: 'process', x: 400, y: 250 },
        { id: 'output', label: 'Output Layer', type: 'output', x: 550, y: 250 },
        { id: 'activation1', label: 'Activation Function', type: 'process', x: 250, y: 350 },
        { id: 'activation2', label: 'Activation Function', type: 'process', x: 400, y: 350 },
        { id: 'activation3', label: 'Activation Function', type: 'process', x: 550, y: 350 },
      ],
      edges: [
        { source: 'input', target: 'hidden1', label: 'Weights' },
        { source: 'hidden1', target: 'hidden2', label: 'Weights' },
        { source: 'hidden2', target: 'output', label: 'Weights' },
        { source: 'hidden1', target: 'activation1' },
        { source: 'hidden2', target: 'activation2' },
        { source: 'output', target: 'activation3' },
        { source: 'activation1', target: 'hidden1', label: 'Output', style: 'dashed' },
        { source: 'activation2', target: 'hidden2', label: 'Output', style: 'dashed' },
        { source: 'activation3', target: 'output', label: 'Output', style: 'dashed' },
      ]
    }
  },
  {
    id: 3,
    title: 'Machine Learning Timeline',
    type: 'timeline',
    date: '2025-07-25',
    sourceNote: 'History of AI',
    sourceNoteId: 5,
    thumbnail: 'https://via.placeholder.com/400x250?text=Timeline',
    description: 'Timeline of major developments in machine learning',
    data: {
      // For a timeline, it might be an array of events with dates
      events: [
        { id: 1, date: '1943', title: 'McCulloch-Pitts Neuron', description: 'First mathematical model of a neural network' },
        { id: 2, date: '1957', title: 'Perceptron', description: 'Frank Rosenblatt creates the perceptron algorithm' },
        { id: 3, date: '1969', title: 'Limitations of Perceptrons', description: 'Minsky and Papert publish "Perceptrons"' },
        { id: 4, date: '1986', title: 'Backpropagation', description: 'Efficient backpropagation algorithm popularized' },
        { id: 5, date: '1997', title: 'LSTM', description: 'Long Short-Term Memory networks introduced' },
        { id: 6, date: '2006', title: 'Deep Learning', description: 'Hinton introduces deep belief networks' },
        { id: 7, date: '2012', title: 'AlexNet', description: 'Deep learning breakthrough in image recognition' },
        { id: 8, date: '2014', title: 'GANs', description: 'Generative Adversarial Networks introduced' },
        { id: 9, date: '2017', title: 'Transformer', description: 'Attention is All You Need paper published' },
        { id: 10, date: '2020', title: 'GPT-3', description: 'Large language models demonstrate remarkable capabilities' },
      ]
    }
  },
  {
    id: 4,
    title: 'AI Knowledge Graph',
    type: 'knowledge_graph',
    date: '2025-07-24',
    sourceNote: 'Artificial Intelligence Overview',
    sourceNoteId: 2,
    thumbnail: 'https://via.placeholder.com/400x250?text=Knowledge+Graph',
    description: 'Knowledge graph connecting AI concepts and applications',
    data: {
      // For a knowledge graph, it might be a complex graph with different types of nodes and relationships
      nodes: [
        { id: 'ai', label: 'Artificial Intelligence', type: 'concept' },
        { id: 'ml', label: 'Machine Learning', type: 'concept' },
        { id: 'dl', label: 'Deep Learning', type: 'concept' },
        { id: 'nlp', label: 'Natural Language Processing', type: 'field' },
        { id: 'cv', label: 'Computer Vision', type: 'field' },
        { id: 'rl', label: 'Reinforcement Learning', type: 'concept' },
        { id: 'nn', label: 'Neural Networks', type: 'concept' },
        { id: 'cnn', label: 'Convolutional Neural Networks', type: 'technique' },
        { id: 'rnn', label: 'Recurrent Neural Networks', type: 'technique' },
        { id: 'transformer', label: 'Transformer', type: 'technique' },
        { id: 'bert', label: 'BERT', type: 'model' },
        { id: 'gpt', label: 'GPT', type: 'model' },
        { id: 'resnet', label: 'ResNet', type: 'model' },
      ],
      relationships: [
        { source: 'ai', target: 'ml', label: 'includes' },
        { source: 'ml', target: 'dl', label: 'includes' },
        { source: 'ml', target: 'rl', label: 'includes' },
        { source: 'dl', target: 'nn', label: 'uses' },
        { source: 'nn', target: 'cnn', label: 'type_of' },
        { source: 'nn', target: 'rnn', label: 'type_of' },
        { source: 'nn', target: 'transformer', label: 'type_of' },
        { source: 'nlp', target: 'bert', label: 'uses' },
        { source: 'nlp', target: 'gpt', label: 'uses' },
        { source: 'cv', target: 'cnn', label: 'uses' },
        { source: 'cv', target: 'resnet', label: 'uses' },
        { source: 'transformer', target: 'bert', label: 'basis_for' },
        { source: 'transformer', target: 'gpt', label: 'basis_for' },
        { source: 'cnn', target: 'resnet', label: 'basis_for' },
      ]
    }
  },
  {
    id: 5,
    title: 'Data Science Workflow',
    type: 'flowchart',
    date: '2025-07-22',
    sourceNote: 'Data Science Methodology',
    sourceNoteId: 7,
    thumbnail: 'https://via.placeholder.com/400x250?text=Flowchart',
    description: 'Flowchart of the data science workflow from data collection to deployment',
    data: {
      nodes: [
        { id: 'collect', label: 'Data Collection', type: 'start', x: 100, y: 250 },
        { id: 'clean', label: 'Data Cleaning', type: 'process', x: 250, y: 250 },
        { id: 'explore', label: 'Exploratory Analysis', type: 'process', x: 400, y: 250 },
        { id: 'feature', label: 'Feature Engineering', type: 'process', x: 550, y: 250 },
        { id: 'model', label: 'Model Building', type: 'process', x: 700, y: 250 },
        { id: 'evaluate', label: 'Model Evaluation', type: 'process', x: 700, y: 400 },
        { id: 'deploy', label: 'Deployment', type: 'end', x: 550, y: 400 },
        { id: 'monitor', label: 'Monitoring', type: 'process', x: 400, y: 400 },
        { id: 'feedback', label: 'Feedback Loop', type: 'process', x: 250, y: 400 },
      ],
      edges: [
        { source: 'collect', target: 'clean' },
        { source: 'clean', target: 'explore' },
        { source: 'explore', target: 'feature' },
        { source: 'feature', target: 'model' },
        { source: 'model', target: 'evaluate' },
        { source: 'evaluate', target: 'deploy', label: 'If satisfactory' },
        { source: 'evaluate', target: 'feature', label: 'If not satisfactory', style: 'dashed' },
        { source: 'deploy', target: 'monitor' },
        { source: 'monitor', target: 'feedback' },
        { source: 'feedback', target: 'collect', style: 'dashed' },
      ]
    }
  },
  {
    id: 6,
    title: 'ML Algorithms Comparison',
    type: 'treegraph',
    date: '2025-07-20',
    sourceNote: 'Machine Learning Algorithms',
    sourceNoteId: 8,
    thumbnail: 'https://via.placeholder.com/400x250?text=Tree+Graph',
    description: 'Tree graph comparing different machine learning algorithms',
    data: {
      // For a tree graph, it might be a hierarchical structure
      root: {
        id: 'ml-algorithms',
        label: 'ML Algorithms',
        children: [
          {
            id: 'supervised',
            label: 'Supervised Learning',
            children: [
              {
                id: 'classification',
                label: 'Classification',
                children: [
                  { id: 'logistic-regression', label: 'Logistic Regression' },
                  { id: 'decision-tree', label: 'Decision Tree' },
                  { id: 'random-forest', label: 'Random Forest' },
                  { id: 'svm', label: 'Support Vector Machine' },
                  { id: 'knn', label: 'K-Nearest Neighbors' },
                ]
              },
              {
                id: 'regression',
                label: 'Regression',
                children: [
                  { id: 'linear-regression', label: 'Linear Regression' },
                  { id: 'polynomial-regression', label: 'Polynomial Regression' },
                  { id: 'ridge-regression', label: 'Ridge Regression' },
                  { id: 'lasso-regression', label: 'Lasso Regression' },
                ]
              }
            ]
          },
          {
            id: 'unsupervised',
            label: 'Unsupervised Learning',
            children: [
              {
                id: 'clustering',
                label: 'Clustering',
                children: [
                  { id: 'k-means', label: 'K-Means' },
                  { id: 'hierarchical', label: 'Hierarchical Clustering' },
                  { id: 'dbscan', label: 'DBSCAN' },
                ]
              },
              {
                id: 'dim-reduction',
                label: 'Dimensionality Reduction',
                children: [
                  { id: 'pca', label: 'Principal Component Analysis' },
                  { id: 't-sne', label: 't-SNE' },
                  { id: 'umap', label: 'UMAP' },
                ]
              }
            ]
          },
          {
            id: 'reinforcement',
            label: 'Reinforcement Learning',
            children: [
              { id: 'q-learning', label: 'Q-Learning' },
              { id: 'dqn', label: 'Deep Q-Network' },
              { id: 'policy-gradient', label: 'Policy Gradient' },
              { id: 'a3c', label: 'Asynchronous Advantage Actor-Critic' },
            ]
          }
        ]
      }
    }
  },
];

const useVisualizationsStore = create(
  persist(
    (set, get) => ({
      visualizations: initialVisualizations,
      activeVisualizationId: null,
      
      // Getters
      getActiveVisualization: () => {
        const { visualizations, activeVisualizationId } = get();
        return visualizations.find(viz => viz.id === activeVisualizationId) || null;
      },
      
      getVisualizationById: (id) => {
        const { visualizations } = get();
        return visualizations.find(viz => viz.id === id) || null;
      },
      
      getVisualizationsByNoteId: (noteId) => {
        const { visualizations } = get();
        return visualizations.filter(viz => viz.sourceNoteId === noteId);
      },
      
      getFilteredVisualizations: (searchTerm = '', type = 'all', noteId = null) => {
        const { visualizations } = get();
        return visualizations.filter(viz => {
          // Filter by search term
          const matchesSearch = searchTerm === '' || 
            viz.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
            viz.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            viz.sourceNote.toLowerCase().includes(searchTerm.toLowerCase());
          
          // Filter by type
          const matchesType = type === 'all' || viz.type === type;
          
          // Filter by source note
          const matchesNote = noteId === null || viz.sourceNoteId === noteId;
          
          return matchesSearch && matchesType && matchesNote;
        });
      },
      
      // Actions
      setActiveVisualization: (vizId) => set({ activeVisualizationId: vizId }),
      
      createVisualization: (vizData) => {
        const { visualizations } = get();
        const newVisualization = {
          id: Date.now(), // Simple ID generation
          date: new Date().toISOString().split('T')[0],
          ...vizData
        };
        
        set({ 
          visualizations: [newVisualization, ...visualizations],
          activeVisualizationId: newVisualization.id
        });
        
        return newVisualization;
      },
      
      updateVisualization: (id, updatedData) => {
        const { visualizations } = get();
        const updatedVisualizations = visualizations.map(viz => 
          viz.id === id ? { ...viz, ...updatedData } : viz
        );
        
        set({ visualizations: updatedVisualizations });
        return updatedVisualizations.find(viz => viz.id === id);
      },
      
      deleteVisualization: (id) => {
        const { visualizations, activeVisualizationId } = get();
        const updatedVisualizations = visualizations.filter(viz => viz.id !== id);
        
        // If the active visualization is being deleted, clear the active visualization
        const newActiveVisualizationId = activeVisualizationId === id ? null : activeVisualizationId;
        
        set({ 
          visualizations: updatedVisualizations,
          activeVisualizationId: newActiveVisualizationId
        });
      },
      
      // Bulk operations
      bulkDeleteVisualizations: (ids) => {
        const { visualizations, activeVisualizationId } = get();
        const updatedVisualizations = visualizations.filter(viz => !ids.includes(viz.id));
        
        // If the active visualization is being deleted, clear the active visualization
        const newActiveVisualizationId = ids.includes(activeVisualizationId) ? null : activeVisualizationId;
        
        set({ 
          visualizations: updatedVisualizations,
          activeVisualizationId: newActiveVisualizationId
        });
      },
      
      deleteVisualizationsByNoteId: (noteId) => {
        const { visualizations, activeVisualizationId } = get();
        const visualizationsToDelete = visualizations.filter(viz => viz.sourceNoteId === noteId);
        const idsToDelete = visualizationsToDelete.map(viz => viz.id);
        
        const updatedVisualizations = visualizations.filter(viz => viz.sourceNoteId !== noteId);
        
        // If the active visualization is being deleted, clear the active visualization
        const newActiveVisualizationId = idsToDelete.includes(activeVisualizationId) ? null : activeVisualizationId;
        
        set({ 
          visualizations: updatedVisualizations,
          activeVisualizationId: newActiveVisualizationId
        });
        
        return idsToDelete.length; // Return number of deleted visualizations
      },
      
      // Import/Export
      importVisualizations: (importedVisualizations) => {
        // Merge imported visualizations with existing visualizations, avoiding duplicates by ID
        const { visualizations } = get();
        const existingIds = new Set(visualizations.map(viz => viz.id));
        
        const newVisualizations = importedVisualizations.filter(viz => !existingIds.has(viz.id));
        const mergedVisualizations = [...visualizations, ...newVisualizations];
        
        set({ visualizations: mergedVisualizations });
        return newVisualizations.length; // Return number of imported visualizations
      },
      
      exportVisualizations: () => {
        // Return all visualizations for export
        return get().visualizations;
      },
      
      // Generate visualization from note
      generateVisualization: (noteId, type, title = null) => {
        // In a real app, this would call an API to generate the visualization
        // For now, we'll just create a placeholder
        
        // Get the note from the note store (in a real app)
        // const note = useNoteStore.getState().getNoteById(noteId);
        
        // Mock note data for demonstration
        const mockNoteData = {
          1: { title: 'Machine Learning Fundamentals', category: 'AI' },
          2: { title: 'React Hooks Deep Dive', category: 'Programming' },
          3: { title: 'Advanced Data Structures', category: 'Computer Science' },
        };
        
        const noteData = mockNoteData[noteId] || { title: 'Unknown Note', category: 'Uncategorized' };
        
        const vizTitle = title || `${type.charAt(0).toUpperCase() + type.slice(1)} of ${noteData.title}`;
        
        const newVisualization = {
          title: vizTitle,
          type: type,
          sourceNote: noteData.title,
          sourceNoteId: noteId,
          description: `Auto-generated ${type} for ${noteData.title}`,
          thumbnail: `https://via.placeholder.com/400x250?text=${type.replace('_', '+')}`,
          data: {}, // This would be generated by the backend in a real app
        };
        
        return get().createVisualization(newVisualization);
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({ visualizations: [], activeVisualizationId: null });
      }
    }),
    {
      name: 'visualizations-storage', // Name for localStorage
      partialize: (state) => ({ visualizations: state.visualizations }), // Only persist visualizations array
    }
  )
);

export default useVisualizationsStore;