import React, { useState } from 'react';
import { Link2, ExternalLink, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';

// Mock data for AI-generated links
const MOCK_LINKS = [
  {
    id: 1,
    title: 'Neural Networks Fundamentals',
    relevance: 0.92,
    reason: 'Both notes discuss fundamental concepts in machine learning and neural networks.',
    noteId: 2
  },
  {
    id: 2,
    title: 'Backpropagation Algorithm',
    relevance: 0.85,
    reason: 'Backpropagation is a key algorithm for training neural networks mentioned in both notes.',
    noteId: 4
  },
  {
    id: 3,
    title: 'Supervised Learning Methods',
    relevance: 0.78,
    reason: 'Both notes cover supervised learning approaches and techniques.',
    noteId: 7
  }
];

const NoteLinks = ({ noteId, onLinkClick }) => {
  const [links, setLinks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateLinks = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would be an API call
      // await api.post('/notes/generate-links', { noteId });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Use mock data for now
      setLinks(MOCK_LINKS);
    } catch (err) {
      console.error('Error generating links:', err);
      setError('Failed to generate links. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLinkClick = (linkNoteId) => {
    if (onLinkClick) {
      onLinkClick(linkNoteId);
    }
  };

  // Function to get color based on relevance score
  const getRelevanceColor = (score) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-orange-600';
  };

  return (
    <div className="border rounded-md p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-md font-medium flex items-center">
          <Link2 className="h-4 w-4 mr-2" />
          AI-Generated Links
        </h3>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={generateLinks}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-1" />
              Generate Links
            </>
          )}
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-3 rounded-md mb-4">
          {error}
        </div>
      )}

      {links.length > 0 ? (
        <div className="space-y-3">
          {links.map(link => (
            <div 
              key={link.id} 
              className="border rounded-md p-3 hover:bg-secondary/50 cursor-pointer"
              onClick={() => handleLinkClick(link.noteId)}
            >
              <div className="flex justify-between items-center mb-1">
                <h4 className="font-medium flex items-center">
                  <ExternalLink className="h-3 w-3 mr-1" />
                  {link.title}
                </h4>
                <span className={`text-xs font-medium ${getRelevanceColor(link.relevance)}`}>
                  {Math.round(link.relevance * 100)}% match
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{link.reason}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-muted-foreground">
          {isLoading ? (
            <p>Analyzing your notes and generating connections...</p>
          ) : (
            <p>Click "Generate Links" to find connections between this note and your other notes.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default NoteLinks;