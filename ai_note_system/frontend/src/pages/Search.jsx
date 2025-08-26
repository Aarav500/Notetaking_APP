import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search as SearchIcon, 
  FileText, 
  BarChart2, 
  Tag, 
  Calendar, 
  Clock, 
  Filter, 
  X, 
  ChevronRight,
  Bookmark,
  Star,
  MessageSquare,
  Lightbulb,
  Zap,
  Layers
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'react-router-dom';

// Mock data for search results
const mockResults = {
  notes: [
    { 
      id: 1, 
      title: 'Machine Learning Fundamentals', 
      excerpt: 'An overview of machine learning concepts including supervised and unsupervised learning, neural networks, and deep learning architectures.',
      category: 'AI', 
      date: '2025-07-28', 
      tags: ['ML', 'AI', 'Neural Networks'],
      starred: true
    },
    { 
      id: 2, 
      title: 'React Hooks Deep Dive', 
      excerpt: 'Exploring React hooks including useState, useEffect, useContext, useReducer, and creating custom hooks for reusable logic.',
      category: 'Programming', 
      date: '2025-07-25', 
      tags: ['React', 'JavaScript', 'Hooks'],
      starred: false
    },
    { 
      id: 3, 
      title: 'Advanced Data Structures', 
      excerpt: 'Comprehensive notes on advanced data structures including trees, graphs, heaps, and their implementation and applications.',
      category: 'Computer Science', 
      date: '2025-07-22', 
      tags: ['Algorithms', 'Data Structures'],
      starred: false
    },
  ],
  visualizations: [
    {
      id: 1,
      title: 'Machine Learning Concepts',
      type: 'mindmap',
      date: '2025-07-28',
      sourceNote: 'Machine Learning Fundamentals',
      sourceNoteId: 1,
      thumbnail: 'https://via.placeholder.com/400x250?text=Mind+Map',
      description: 'Mind map of key machine learning concepts and their relationships'
    },
    {
      id: 2,
      title: 'Neural Network Architecture',
      type: 'flowchart',
      date: '2025-07-26',
      sourceNote: 'Deep Learning Architectures',
      sourceNoteId: 3,
      thumbnail: 'https://via.placeholder.com/400x250?text=Flowchart',
      description: 'Flowchart showing the architecture of a neural network'
    },
  ],
  questions: [
    {
      id: 1,
      question: 'What is the difference between supervised and unsupervised learning?',
      answer: 'Supervised learning uses labeled data for training, while unsupervised learning works with unlabeled data to find patterns.',
      sourceNote: 'Machine Learning Fundamentals',
      sourceNoteId: 1,
      date: '2025-07-28',
    },
    {
      id: 2,
      question: 'Explain the concept of backpropagation in neural networks.',
      answer: 'Backpropagation is an algorithm used to train neural networks by calculating gradients of the loss function with respect to the weights, propagating errors backward through the network.',
      sourceNote: 'Deep Learning Architectures',
      sourceNoteId: 3,
      date: '2025-07-26',
    },
  ],
  glossary: [
    {
      id: 1,
      term: 'Neural Network',
      definition: 'A computational model inspired by the structure and function of the human brain, consisting of interconnected nodes (neurons) organized in layers.',
      sourceNote: 'Machine Learning Fundamentals',
      sourceNoteId: 1,
      date: '2025-07-28',
    },
    {
      id: 2,
      term: 'React Hook',
      definition: 'Functions that let you "hook into" React state and lifecycle features from function components.',
      sourceNote: 'React Hooks Deep Dive',
      sourceNoteId: 2,
      date: '2025-07-25',
    },
  ],
};

// Categories for filtering
const categories = [
  'All',
  'AI',
  'Programming',
  'Computer Science',
  'Physics',
  'Software Engineering'
];

// Content types for filtering
const contentTypes = [
  { id: 'all', label: 'All Content', icon: Layers },
  { id: 'notes', label: 'Notes', icon: FileText },
  { id: 'visualizations', label: 'Visualizations', icon: BarChart2 },
  { id: 'questions', label: 'Questions', icon: MessageSquare },
  { id: 'glossary', label: 'Glossary', icon: Bookmark },
];

export default function Search() {
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedContentType, setSelectedContentType] = useState('all');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [recentSearches, setRecentSearches] = useState([
    'machine learning', 
    'neural networks', 
    'react hooks'
  ]);

  // Handle search submission
  const handleSearch = (e) => {
    e?.preventDefault();
    
    if (!searchTerm.trim()) {
      toast({
        title: 'Empty Search',
        description: 'Please enter a search term',
        variant: 'destructive',
      });
      return;
    }
    
    setIsSearching(true);
    
    // Simulate API call
    setTimeout(() => {
      setSearchResults(mockResults);
      setIsSearching(false);
      
      // Add to recent searches if not already there
      if (!recentSearches.includes(searchTerm.toLowerCase())) {
        setRecentSearches([searchTerm.toLowerCase(), ...recentSearches].slice(0, 5));
      }
    }, 1000);
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setSearchResults(null);
  };

  // Clear recent searches
  const clearRecentSearches = () => {
    setRecentSearches([]);
    toast({
      title: 'Recent Searches Cleared',
      description: 'Your search history has been cleared',
    });
  };

  // Use recent search
  const useRecentSearch = (term) => {
    setSearchTerm(term);
    // Trigger search immediately
    setTimeout(() => handleSearch(), 0);
  };

  // Filter results by category and content type
  const getFilteredResults = () => {
    if (!searchResults) return null;
    
    const results = {};
    
    // Filter by content type
    Object.keys(searchResults).forEach(type => {
      if (selectedContentType === 'all' || selectedContentType === type) {
        // Filter by category
        results[type] = searchResults[type].filter(item => 
          selectedCategory === 'All' || 
          (item.category === selectedCategory) || 
          (type === 'visualizations' && item.sourceNote.includes(selectedCategory))
        );
      }
    });
    
    return results;
  };

  // Get total result count
  const getTotalResultCount = (results) => {
    if (!results) return 0;
    return Object.values(results).reduce((total, items) => total + items.length, 0);
  };

  // Filtered results
  const filteredResults = getFilteredResults();
  const totalResultCount = filteredResults ? getTotalResultCount(filteredResults) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-4">Search</h1>
        
        {/* Search Form */}
        <form onSubmit={handleSearch} className="relative">
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search notes, visualizations, questions, and more..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-md border border-input bg-background pl-10 pr-10 py-3 text-base ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={clearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
          <Button 
            type="submit" 
            className="absolute right-0 top-0 h-full rounded-l-none"
            disabled={isSearching}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </Button>
        </form>
      </div>

      {/* Recent Searches */}
      {!searchResults && recentSearches.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card rounded-lg border border-border p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Searches</h2>
            <Button variant="ghost" size="sm" onClick={clearRecentSearches}>
              Clear History
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((term, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => useRecentSearch(term)}
                className="flex items-center"
              >
                <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
                {term}
              </Button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Search Results */}
      {isSearching && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-12"
        >
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-muted-foreground">Searching for "{searchTerm}"...</p>
        </motion.div>
      )}

      {searchResults && !isSearching && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Filters */}
          <div className="bg-card rounded-lg border border-border p-4">
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5 text-muted-foreground" />
                <span className="font-medium">Filters:</span>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {/* Content Type Filter */}
                <div className="flex flex-wrap gap-2">
                  {contentTypes.map((type) => (
                    <Button
                      key={type.id}
                      variant={selectedContentType === type.id ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedContentType(type.id)}
                      className="flex items-center"
                    >
                      <type.icon className="mr-2 h-4 w-4" />
                      {type.label}
                    </Button>
                  ))}
                </div>
                
                {/* Category Filter */}
                <div className="relative">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="appearance-none rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    {categories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          {/* Results Summary */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              {totalResultCount} {totalResultCount === 1 ? 'result' : 'results'} for "{searchTerm}"
            </h2>
          </div>
          
          {totalResultCount === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-12 text-center"
            >
              <SearchIcon className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">No results found</h3>
              <p className="text-muted-foreground mt-1 max-w-md">
                We couldn't find any matches for "{searchTerm}" with your current filters. 
                Try adjusting your filters or using different search terms.
              </p>
            </motion.div>
          ) : (
            <div className="space-y-8">
              {/* Notes Results */}
              {filteredResults.notes && filteredResults.notes.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Notes ({filteredResults.notes.length})</h3>
                  </div>
                  
                  <div className="space-y-4">
                    {filteredResults.notes.map((note, index) => (
                      <motion.div
                        key={note.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <Link 
                                to={`/notes/${note.id}`}
                                className="text-lg font-semibold hover:underline"
                              >
                                {note.title}
                              </Link>
                              {note.starred && (
                                <Star className="h-4 w-4 text-amber-500 fill-amber-500" />
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {note.category} • {new Date(note.date).toLocaleDateString()}
                            </p>
                            <p className="mt-2 text-sm line-clamp-2">{note.excerpt}</p>
                          </div>
                          
                          <Button variant="ghost" size="icon" asChild>
                            <Link to={`/notes/${note.id}`}>
                              <ChevronRight className="h-5 w-5" />
                            </Link>
                          </Button>
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mt-3">
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
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Visualizations Results */}
              {filteredResults.visualizations && filteredResults.visualizations.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <BarChart2 className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Visualizations ({filteredResults.visualizations.length})</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filteredResults.visualizations.map((viz, index) => (
                      <motion.div
                        key={viz.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="bg-card rounded-lg border border-border overflow-hidden hover:shadow-md transition-shadow"
                      >
                        <div className="h-40 bg-muted">
                          <img 
                            src={viz.thumbnail} 
                            alt={viz.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        
                        <div className="p-4">
                          <Link 
                            to={`/visualizations/${viz.id}`}
                            className="font-semibold hover:underline"
                          >
                            {viz.title}
                          </Link>
                          <p className="text-sm text-muted-foreground mt-1">
                            {new Date(viz.date).toLocaleDateString()}
                          </p>
                          <p className="text-sm mt-2 line-clamp-2">{viz.description}</p>
                          
                          <div className="mt-3 flex items-center text-sm">
                            <FileText className="h-4 w-4 mr-1 text-muted-foreground" />
                            <span className="text-muted-foreground">Source: </span>
                            <Link 
                              to={`/notes/${viz.sourceNoteId}`}
                              className="ml-1 text-primary hover:underline"
                            >
                              {viz.sourceNote}
                            </Link>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Questions Results */}
              {filteredResults.questions && filteredResults.questions.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Questions ({filteredResults.questions.length})</h3>
                  </div>
                  
                  <div className="space-y-4">
                    {filteredResults.questions.map((question, index) => (
                      <motion.div
                        key={question.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow"
                      >
                        <h4 className="font-semibold">{question.question}</h4>
                        <p className="text-sm mt-2">{question.answer}</p>
                        
                        <div className="mt-3 flex items-center text-sm">
                          <FileText className="h-4 w-4 mr-1 text-muted-foreground" />
                          <span className="text-muted-foreground">Source: </span>
                          <Link 
                            to={`/notes/${question.sourceNoteId}`}
                            className="ml-1 text-primary hover:underline"
                          >
                            {question.sourceNote}
                          </Link>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Glossary Results */}
              {filteredResults.glossary && filteredResults.glossary.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Bookmark className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold">Glossary Terms ({filteredResults.glossary.length})</h3>
                  </div>
                  
                  <div className="space-y-4">
                    {filteredResults.glossary.map((term, index) => (
                      <motion.div
                        key={term.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow"
                      >
                        <h4 className="font-semibold">{term.term}</h4>
                        <p className="text-sm mt-2">{term.definition}</p>
                        
                        <div className="mt-3 flex items-center text-sm">
                          <FileText className="h-4 w-4 mr-1 text-muted-foreground" />
                          <span className="text-muted-foreground">Source: </span>
                          <Link 
                            to={`/notes/${term.sourceNoteId}`}
                            className="ml-1 text-primary hover:underline"
                          >
                            {term.sourceNote}
                          </Link>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      )}

      {/* Search Tips */}
      {!searchResults && !isSearching && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card rounded-lg border border-border p-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="h-5 w-5 text-amber-500" />
            <h2 className="text-xl font-semibold">Search Tips</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h3 className="font-medium flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Search across all content
              </h3>
              <p className="text-sm text-muted-foreground">
                Find notes, visualizations, questions, and glossary terms all at once.
              </p>
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Use specific keywords
              </h3>
              <p className="text-sm text-muted-foreground">
                More specific search terms will yield more relevant results.
              </p>
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Filter by content type
              </h3>
              <p className="text-sm text-muted-foreground">
                Narrow down results to specific content types like notes or visualizations.
              </p>
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Filter by category
              </h3>
              <p className="text-sm text-muted-foreground">
                Find content related to specific categories like AI or Programming.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}