import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Save, 
  Tag, 
  Calendar, 
  Folder, 
  Clock, 
  Star, 
  StarOff,
  Download,
  Share,
  Trash,
  FileText,
  BarChart2,
  HelpCircle,
  MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

// Mock data for a single note
const mockNotes = {
  1: { 
    id: 1, 
    title: 'Machine Learning Fundamentals', 
    content: `# Machine Learning Fundamentals

## Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data. Unlike traditional programming, where explicit instructions are provided, machine learning algorithms build models based on sample data to make predictions or decisions without being explicitly programmed to do so.

## Types of Machine Learning

### Supervised Learning

In supervised learning, the algorithm is trained on labeled data, meaning that each training example is paired with an output label. The goal is to learn a mapping from inputs to outputs.

Examples:
- Classification (predicting a label)
- Regression (predicting a continuous value)

### Unsupervised Learning

Unsupervised learning deals with unlabeled data. The algorithm tries to learn the inherent structure of the data without any explicit guidance.

Examples:
- Clustering
- Dimensionality reduction
- Association rule learning

### Reinforcement Learning

Reinforcement learning involves an agent that learns to make decisions by taking actions in an environment to maximize some notion of cumulative reward.

## Neural Networks

Neural networks are a set of algorithms inspired by the human brain, designed to recognize patterns. They interpret sensory data through a kind of machine perception, labeling or clustering raw input.

### Components of Neural Networks

1. **Input Layer**: Receives the initial data
2. **Hidden Layers**: Process the data through weighted connections
3. **Output Layer**: Produces the final result
4. **Activation Functions**: Introduce non-linearity into the network
5. **Weights and Biases**: Parameters that are adjusted during training

### Deep Learning

Deep learning refers to neural networks with many layers (deep neural networks). These networks can automatically learn hierarchical features from data.

## Common Algorithms

1. **Linear Regression**
2. **Logistic Regression**
3. **Decision Trees**
4. **Random Forests**
5. **Support Vector Machines (SVM)**
6. **K-Nearest Neighbors (KNN)**
7. **K-Means Clustering**
8. **Principal Component Analysis (PCA)**

## Evaluation Metrics

- **Accuracy**: Proportion of correct predictions
- **Precision**: Proportion of positive identifications that were actually correct
- **Recall**: Proportion of actual positives that were identified correctly
- **F1 Score**: Harmonic mean of precision and recall
- **ROC Curve**: Plot of true positive rate against false positive rate

## Challenges in Machine Learning

- **Overfitting**: Model performs well on training data but poorly on unseen data
- **Underfitting**: Model is too simple to capture the underlying pattern
- **Bias-Variance Tradeoff**: Finding the right balance between bias and variance
- **Feature Selection**: Choosing the most relevant features
- **Imbalanced Data**: Dealing with datasets where classes are not equally represented

## Applications

- **Computer Vision**: Image recognition, object detection
- **Natural Language Processing**: Text classification, sentiment analysis, machine translation
- **Recommendation Systems**: Product recommendations, content suggestions
- **Autonomous Vehicles**: Self-driving cars
- **Healthcare**: Disease diagnosis, drug discovery
- **Finance**: Fraud detection, algorithmic trading`,
    category: 'AI', 
    date: '2025-07-28', 
    lastEdited: '2025-07-29T14:30:00',
    tags: ['ML', 'AI', 'Neural Networks'],
    starred: true
  },
  2: { 
    id: 2, 
    title: 'React Hooks Deep Dive', 
    content: '# React Hooks Deep Dive\n\nDetailed content about React hooks...',
    category: 'Programming', 
    date: '2025-07-25', 
    lastEdited: '2025-07-26T10:15:00',
    tags: ['React', 'JavaScript', 'Hooks'],
    starred: false
  },
};

export default function NotePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [note, setNote] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // In a real app, this would be an API call
    const fetchNote = () => {
      const foundNote = mockNotes[id];
      
      if (foundNote) {
        setNote(foundNote);
        setEditedTitle(foundNote.title);
        setEditedContent(foundNote.content);
      } else {
        toast({
          title: 'Note Not Found',
          description: 'The requested note could not be found',
          variant: 'destructive',
        });
        navigate('/notes');
      }
    };
    
    fetchNote();
  }, [id, navigate, toast]);

  const handleSave = () => {
    setIsSaving(true);
    
    // Simulate API call
    setTimeout(() => {
      setNote({
        ...note,
        title: editedTitle,
        content: editedContent,
        lastEdited: new Date().toISOString(),
      });
      
      setIsSaving(false);
      setIsEditing(false);
      
      toast({
        title: 'Note Saved',
        description: 'Your changes have been saved successfully',
      });
    }, 1000);
  };

  const toggleStar = () => {
    setNote({
      ...note,
      starred: !note.starred,
    });
    
    toast({
      title: note.starred ? 'Removed from Starred' : 'Added to Starred',
      description: `"${note.title}" has been ${note.starred ? 'removed from' : 'added to'} your starred notes`,
    });
  };

  const handleDelete = () => {
    // Simulate API call
    setTimeout(() => {
      toast({
        title: 'Note Deleted',
        description: `"${note.title}" has been deleted`,
        variant: 'destructive',
      });
      
      navigate('/notes');
    }, 500);
  };

  const handleExport = () => {
    toast({
      title: 'Note Exported',
      description: 'Your note has been exported as Markdown',
    });
  };

  if (!note) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={() => navigate('/notes')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-3xl font-bold tracking-tight">
            {isEditing ? (
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="bg-transparent border-b border-border focus:outline-none focus:border-primary w-full"
              />
            ) : (
              note.title
            )}
          </h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleStar}
            className="ml-2"
          >
            {note.starred ? (
              <Star className="h-5 w-5 text-amber-500 fill-amber-500" />
            ) : (
              <StarOff className="h-5 w-5 text-muted-foreground" />
            )}
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <Button 
                variant="outline" 
                onClick={() => {
                  setEditedTitle(note.title);
                  setEditedContent(note.content);
                  setIsEditing(false);
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save'}
                {!isSaving && <Save className="ml-2 h-4 w-4" />}
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={handleExport}>
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Metadata */}
      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-1">
          <Calendar className="h-4 w-4" />
          <span>Created: {new Date(note.date).toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>Last edited: {new Date(note.lastEdited).toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <Folder className="h-4 w-4" />
          <span>{note.category}</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {note.tags.map((tag) => (
            <span
              key={tag}
              className="bg-secondary text-secondary-foreground text-xs px-2 py-1 rounded-full flex items-center"
            >
              <Tag className="h-3 w-3 mr-1" />
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="bg-card rounded-lg border border-border p-6">
        {isEditing ? (
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="w-full h-[60vh] bg-background p-4 rounded-md border border-input focus:outline-none focus:ring-2 focus:ring-ring font-mono text-sm"
          />
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="prose prose-sm md:prose-base dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ 
              __html: note.content
                .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
                .replace(/^##### (.*$)/gm, '<h5>$1</h5>')
                .replace(/^###### (.*$)/gm, '<h6>$1</h6>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/^- (.*$)/gm, '<li>$1</li>')
                .replace(/\n\n/g, '<br/><br/>')
            }}
          />
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <FileText className="mr-2 h-4 w-4" />
            Generate Summary
          </Button>
          <Button variant="outline" size="sm">
            <BarChart2 className="mr-2 h-4 w-4" />
            Visualize
          </Button>
          <Button variant="outline" size="sm">
            <HelpCircle className="mr-2 h-4 w-4" />
            Generate Questions
          </Button>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Share className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="destructive" size="sm" onClick={handleDelete}>
            <Trash className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}