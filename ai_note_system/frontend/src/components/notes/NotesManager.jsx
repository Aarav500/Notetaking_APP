import React, { useState, useEffect } from 'react';
import { Search, Tag, Plus, FileDown, Link2, BookOpen, X } from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '@/lib/utils';
import NoteLinks from './NoteLinks';
import FlashcardGenerator from './FlashcardGenerator';
import { exportAndDownloadNote } from '@/utils/exportUtils';

// Mock data for initial development
const MOCK_NOTES = [
  { 
    id: 1, 
    title: 'Introduction to Machine Learning', 
    content: 'Machine learning is a subset of artificial intelligence...',
    tags: ['ML', 'AI', 'Introduction'],
    createdAt: '2025-07-25T10:30:00Z',
    updatedAt: '2025-07-26T14:20:00Z'
  },
  { 
    id: 2, 
    title: 'Neural Networks Fundamentals', 
    content: 'Neural networks are computing systems inspired by biological neural networks...',
    tags: ['ML', 'Neural Networks', 'Deep Learning'],
    createdAt: '2025-07-26T09:15:00Z',
    updatedAt: '2025-07-26T09:15:00Z'
  },
  { 
    id: 3, 
    title: 'Data Preprocessing Techniques', 
    content: 'Data preprocessing is a crucial step in the machine learning pipeline...',
    tags: ['Data Science', 'ML', 'Preprocessing'],
    createdAt: '2025-07-27T11:45:00Z',
    updatedAt: '2025-07-28T16:30:00Z'
  },
];

const NotesManager = () => {
  const [notes, setNotes] = useState(MOCK_NOTES);
  const [filteredNotes, setFilteredNotes] = useState(MOCK_NOTES);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [activeNote, setActiveNote] = useState(null);
  const [showFlashcards, setShowFlashcards] = useState(false);

  // Extract all unique tags from notes
  useEffect(() => {
    const tags = new Set();
    notes.forEach(note => {
      note.tags.forEach(tag => tags.add(tag));
    });
    setAllTags(Array.from(tags));
  }, [notes]);

  // Filter notes based on search term and selected tags
  useEffect(() => {
    let filtered = notes;
    
    if (searchTerm) {
      filtered = filtered.filter(note => 
        note.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
        note.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedTags.length > 0) {
      filtered = filtered.filter(note => 
        selectedTags.every(tag => note.tags.includes(tag))
      );
    }
    
    setFilteredNotes(filtered);
  }, [notes, searchTerm, selectedTags]);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const toggleTag = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag) 
        : [...prev, tag]
    );
  };

  const handleNoteSelect = (note) => {
    setActiveNote(note);
  };

  const handleCreateNote = () => {
    // This would open a modal or navigate to create note page
    console.log('Create new note');
  };

  const handleExport = async (format) => {
    if (!activeNote) return;
    
    try {
      await exportAndDownloadNote(activeNote, format);
      // Could add a toast notification here to indicate successful export
      console.log(`Successfully exported note ${activeNote.id} as ${format}`);
    } catch (error) {
      console.error(`Error exporting note as ${format}:`, error);
      // Could add error handling/notification here
    }
  };

  const handleGenerateFlashcards = () => {
    if (!activeNote) return;
    setShowFlashcards(true);
  };

  const handleGenerateLinks = () => {
    if (!activeNote) return;
    console.log(`Generating AI links for note ${activeNote.id}`);
    // Implementation for AI-generated links
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-80 border-r p-4 flex flex-col h-full">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search notes..."
              className="pl-8 pr-4 py-2 w-full rounded-md border border-input bg-background"
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>
        </div>
        
        <div className="mb-4">
          <h3 className="text-sm font-medium mb-2 flex items-center">
            <Tag className="h-4 w-4 mr-1" />
            Tags
          </h3>
          <div className="flex flex-wrap gap-2">
            {allTags.map(tag => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={cn(
                  "px-2 py-1 text-xs rounded-full",
                  selectedTags.includes(tag)
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground"
                )}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex-1 overflow-auto">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-medium">Notes</h3>
            <Button variant="ghost" size="sm" onClick={handleCreateNote}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-2">
            {filteredNotes.map(note => (
              <div
                key={note.id}
                className={cn(
                  "p-3 rounded-md cursor-pointer",
                  activeNote?.id === note.id
                    ? "bg-primary/10 border border-primary/20"
                    : "hover:bg-secondary"
                )}
                onClick={() => handleNoteSelect(note)}
              >
                <h4 className="font-medium truncate">{note.title}</h4>
                <p className="text-sm text-muted-foreground truncate">
                  {note.content.substring(0, 60)}...
                </p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {note.tags.map(tag => (
                    <span
                      key={tag}
                      className="px-1.5 py-0.5 text-xs rounded-full bg-secondary text-secondary-foreground"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Updated {new Date(note.updatedAt).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 p-4 flex flex-col h-full">
        {activeNote ? (
          showFlashcards ? (
            <div className="flex flex-col h-full">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Flashcards: {activeNote.title}</h2>
                <Button variant="outline" size="sm" onClick={() => setShowFlashcards(false)}>
                  <X className="h-4 w-4 mr-1" />
                  Close Flashcards
                </Button>
              </div>
              <div className="flex-1">
                <FlashcardGenerator 
                  noteId={activeNote.id}
                  noteTitle={activeNote.title}
                  noteContent={activeNote.content}
                />
              </div>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">{activeNote.title}</h2>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={handleGenerateLinks}>
                    <Link2 className="h-4 w-4 mr-1" />
                    AI Links
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleGenerateFlashcards}>
                    <BookOpen className="h-4 w-4 mr-1" />
                    Flashcards
                  </Button>
                  <div className="relative group">
                    <Button variant="outline" size="sm">
                      <FileDown className="h-4 w-4 mr-1" />
                      Export
                    </Button>
                    <div className="absolute right-0 mt-1 w-32 bg-background border rounded-md shadow-md hidden group-hover:block z-10">
                      <button 
                        className="w-full text-left px-3 py-2 text-sm hover:bg-secondary"
                        onClick={() => handleExport('markdown')}
                      >
                        Markdown
                      </button>
                      <button 
                        className="w-full text-left px-3 py-2 text-sm hover:bg-secondary"
                        onClick={() => handleExport('anki')}
                      >
                        Anki
                      </button>
                      <button 
                        className="w-full text-left px-3 py-2 text-sm hover:bg-secondary"
                        onClick={() => handleExport('pdf')}
                      >
                        PDF
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2 mb-4">
                {activeNote.tags.map(tag => (
                  <div key={tag} className="flex items-center px-2 py-1 rounded-full bg-secondary text-secondary-foreground text-sm">
                    {tag}
                    <button className="ml-1">
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                <Button variant="ghost" size="sm" className="rounded-full">
                  <Plus className="h-3 w-3" />
                </Button>
              </div>
              
              <div className="flex-1 overflow-auto border rounded-md p-4">
                <p>{activeNote.content}</p>
              </div>
              
              <div className="mt-4">
                <NoteLinks 
                  noteId={activeNote.id} 
                  onLinkClick={(noteId) => {
                    const note = notes.find(n => n.id === noteId);
                    if (note) {
                      setActiveNote(note);
                    }
                  }} 
                />
              </div>
            </>
          )
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <h3 className="text-xl font-medium mb-2">No note selected</h3>
            <p className="mb-4">Select a note from the sidebar or create a new one</p>
            <Button onClick={handleCreateNote}>
              <Plus className="h-4 w-4 mr-1" />
              Create New Note
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotesManager;