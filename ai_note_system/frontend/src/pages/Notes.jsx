import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Search, 
  Plus, 
  Filter, 
  SortAsc, 
  SortDesc, 
  Tag, 
  Folder, 
  Calendar, 
  FileText,
  MoreHorizontal,
  Trash,
  Edit,
  Copy,
  Star,
  StarOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

// Mock data for notes
const mockNotes = [
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
  { 
    id: 4, 
    title: 'Quantum Computing Basics', 
    excerpt: 'Introduction to quantum computing concepts, qubits, quantum gates, and quantum algorithms like Shor\'s and Grover\'s.',
    category: 'Physics', 
    date: '2025-07-20', 
    tags: ['Quantum', 'Computing', 'Physics'],
    starred: true
  },
  { 
    id: 5, 
    title: 'System Design Patterns', 
    excerpt: 'Notes on common system design patterns, scalability considerations, and distributed systems architecture.',
    category: 'Software Engineering', 
    date: '2025-07-18', 
    tags: ['System Design', 'Architecture', 'Scalability'],
    starred: false
  },
];

// Categories for filtering
const categories = [
  'All',
  'AI',
  'Programming',
  'Computer Science',
  'Physics',
  'Software Engineering'
];

export default function Notes() {
  const { toast } = useToast();
  const [notes, setNotes] = useState(mockNotes);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'
  const [isLoading, setIsLoading] = useState(false);

  // Filter and sort notes
  const filteredNotes = notes
    .filter(note => {
      const matchesSearch = note.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                           note.excerpt.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           note.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'All' || note.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      const dateA = new Date(a.date);
      const dateB = new Date(b.date);
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });

  const handleCreateNote = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: 'Note Created',
        description: 'New blank note has been created',
      });
    }, 1000);
  };

  const toggleStar = (id) => {
    setNotes(notes.map(note => 
      note.id === id ? { ...note, starred: !note.starred } : note
    ));
    
    const note = notes.find(note => note.id === id);
    toast({
      title: note.starred ? 'Removed from Starred' : 'Added to Starred',
      description: `"${note.title}" has been ${note.starred ? 'removed from' : 'added to'} your starred notes`,
    });
  };

  const handleDelete = (id) => {
    const noteToDelete = notes.find(note => note.id === id);
    
    setNotes(notes.filter(note => note.id !== id));
    
    toast({
      title: 'Note Deleted',
      description: `"${noteToDelete.title}" has been deleted`,
      variant: 'destructive',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Notes</h1>
        <Button onClick={handleCreateNote} disabled={isLoading}>
          <Plus className="mr-2 h-4 w-4" />
          New Note
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search notes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="appearance-none rounded-md border border-input bg-background px-3 py-2 pr-8 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            <Folder className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>
          
          <Button
            variant="outline"
            size="icon"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            title={`Sort by date ${sortOrder === 'asc' ? 'newest first' : 'oldest first'}`}
          >
            {sortOrder === 'asc' ? (
              <SortAsc className="h-4 w-4" />
            ) : (
              <SortDesc className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Notes List */}
      {filteredNotes.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-12 text-center"
        >
          <FileText className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No notes found</h3>
          <p className="text-muted-foreground mt-1">
            {searchTerm ? 'Try a different search term or filter' : 'Create your first note to get started'}
          </p>
        </motion.div>
      ) : (
        <div className="grid gap-4">
          {filteredNotes.map((note, index) => (
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
                      className="text-xl font-semibold hover:underline"
                    >
                      {note.title}
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => toggleStar(note.id)}
                    >
                      {note.starred ? (
                        <Star className="h-4 w-4 text-amber-500 fill-amber-500" />
                      ) : (
                        <StarOff className="h-4 w-4 text-muted-foreground" />
                      )}
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {note.category} • {new Date(note.date).toLocaleDateString()}
                  </p>
                  <p className="mt-2 text-sm line-clamp-2">{note.excerpt}</p>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" asChild>
                    <Link to={`/notes/${note.id}`}>
                      <Edit className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon"
                    onClick={() => {
                      toast({
                        title: 'Note Duplicated',
                        description: `A copy of "${note.title}" has been created`,
                      });
                    }}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon"
                    onClick={() => handleDelete(note.id)}
                  >
                    <Trash className="h-4 w-4" />
                  </Button>
                </div>
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
      )}
    </div>
  );
}