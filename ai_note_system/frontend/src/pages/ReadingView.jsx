import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Bookmark, 
  Highlighter, 
  MessageSquare, 
  SplitSquareVertical, 
  Sparkles, 
  HelpCircle,
  Book,
  List,
  X,
  Plus,
  Save,
  Download,
  Share
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import PDFViewer from '@/components/PDFViewer';

export default function ReadingView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const sidebarRef = useRef(null);
  
  // State for PDF viewer
  const [pdfDocument, setPdfDocument] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [scale, setScale] = useState(1.0);
  const [rotation, setRotation] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  // State for split screen
  const [splitRatio, setSplitRatio] = useState(0.6); // 60% PDF, 40% notes
  const [isDragging, setIsDragging] = useState(false);
  
  // State for sidebar
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeSidebarTab, setActiveSidebarTab] = useState('toc'); // 'toc', 'bookmarks', 'annotations', 'ai'
  
  // State for notes
  const [notes, setNotes] = useState('');
  const [annotations, setAnnotations] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [tableOfContents, setTableOfContents] = useState([]);
  
  // State for AI features
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [pageSummary, setPageSummary] = useState('');
  const [isSummarizing, setIsSummarizing] = useState(false);
  
  // Mock book data (replace with API call)
  const [bookData, setBookData] = useState({
    id: id,
    title: 'Machine Learning Fundamentals',
    author: 'Jane Smith',
    coverImage: 'https://via.placeholder.com/150',
    pdfUrl: 'https://arxiv.org/pdf/1706.03762.pdf', // Example PDF URL
  });
  
  // Load PDF document
  useEffect(() => {
    // In a real app, fetch book data from API
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      
      // Mock table of contents
      setTableOfContents([
        { id: 1, title: 'Introduction', level: 1, page: 1 },
        { id: 2, title: 'Background', level: 1, page: 3 },
        { id: 3, title: 'Methodology', level: 1, page: 5 },
        { id: 4, title: 'Experimental Setup', level: 2, page: 7 },
        { id: 5, title: 'Results', level: 1, page: 10 },
        { id: 6, title: 'Discussion', level: 1, page: 15 },
        { id: 7, title: 'Conclusion', level: 1, page: 18 },
      ]);
      
      // Mock bookmarks
      setBookmarks([
        { id: 1, title: 'Important concept', page: 4 },
        { id: 2, title: 'Key formula', page: 8 },
        { id: 3, title: 'Review this section', page: 12 },
      ]);
      
      // Mock annotations
      setAnnotations([
        { id: 1, type: 'highlight', content: 'This is an important concept', color: '#FFEB3B', page: 4, position: { x: 100, y: 200, width: 300, height: 20 } },
        { id: 2, type: 'note', content: 'Remember this for the exam', color: '#4CAF50', page: 6, position: { x: 150, y: 300, width: 250, height: 20 } },
        { id: 3, type: 'highlight', content: 'Key formula', color: '#2196F3', page: 8, position: { x: 200, y: 400, width: 200, height: 30 } },
      ]);
      
      toast({
        title: 'PDF Loaded',
        description: 'The document has been loaded successfully',
      });
    }, 1500);
  }, [id, toast]);
  
  // Handle page navigation
  const goToPage = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };
  
  // Handle zoom
  const handleZoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.1, 2.0));
  };
  
  const handleZoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.1, 0.5));
  };
  
  // Handle rotation
  const handleRotate = () => {
    setRotation(prevRotation => (prevRotation + 90) % 360);
  };
  
  // Handle split screen resizing
  const handleMouseDown = (e) => {
    setIsDragging(true);
  };
  
  const handleMouseMove = (e) => {
    if (isDragging) {
      const containerWidth = e.currentTarget.clientWidth;
      const newRatio = e.clientX / containerWidth;
      setSplitRatio(Math.max(0.3, Math.min(0.7, newRatio)));
    }
  };
  
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  // Handle AI question
  const handleAskAI = () => {
    if (!aiQuestion.trim()) {
      toast({
        title: 'Empty Question',
        description: 'Please enter a question to ask',
        variant: 'destructive',
      });
      return;
    }
    
    setIsAiLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setAiResponse(`This is a simulated AI response to your question: "${aiQuestion}". In a real implementation, this would call an API to generate a contextual response based on the current page content.`);
      setIsAiLoading(false);
    }, 2000);
  };
  
  // Handle page summarization
  const handleSummarizePage = () => {
    setIsSummarizing(true);
    
    // Simulate API call
    setTimeout(() => {
      setPageSummary(`This is a simulated summary of page ${currentPage}. In a real implementation, this would extract the text from the current page and use an AI model to generate a concise summary of the key points.`);
      setIsSummarizing(false);
      
      // Switch to AI tab to show the summary
      setActiveSidebarTab('ai');
      
      toast({
        title: 'Page Summarized',
        description: 'Summary generated successfully',
      });
    }, 2000);
  };
  
  // Handle creating flashcard from selection
  const handleCreateFlashcard = (selectedText) => {
    toast({
      title: 'Flashcard Created',
      description: 'Flashcard created from selected text',
    });
  };
  
  // Handle creating note from selection
  const handleCreateNote = (selectedText) => {
    setNotes(prevNotes => prevNotes + `\n\n${selectedText}`);
    
    toast({
      title: 'Note Created',
      description: 'Note created from selected text',
    });
  };
  
  // Handle adding bookmark
  const handleAddBookmark = () => {
    const bookmarkTitle = prompt('Enter bookmark title:');
    
    if (bookmarkTitle) {
      const newBookmark = {
        id: Date.now(),
        title: bookmarkTitle,
        page: currentPage,
      };
      
      setBookmarks([...bookmarks, newBookmark]);
      
      toast({
        title: 'Bookmark Added',
        description: `Bookmark "${bookmarkTitle}" added for page ${currentPage}`,
      });
    }
  };
  
  // Handle saving notes
  const handleSaveNotes = () => {
    // In a real app, save notes to API
    toast({
      title: 'Notes Saved',
      description: 'Your notes have been saved successfully',
    });
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Button variant="outline" size="icon" onClick={() => navigate('/notes')}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-2xl font-bold ml-2">{bookData.title}</h1>
          <span className="text-muted-foreground ml-2">by {bookData.author}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleSaveNotes}>
            <Save className="mr-2 h-4 w-4" />
            Save Notes
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Share className="mr-2 h-4 w-4" />
            Share
          </Button>
        </div>
      </div>
      
      {/* Main Content */}
      <div 
        className="flex flex-1 border border-border rounded-lg overflow-hidden relative"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Sidebar */}
        {isSidebarOpen && (
          <motion.div 
            ref={sidebarRef}
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 250, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="border-r border-border bg-card h-full flex flex-col"
          >
            {/* Sidebar Header */}
            <div className="flex items-center justify-between p-3 border-b border-border">
              <div className="flex">
                <Button 
                  variant={activeSidebarTab === 'toc' ? 'default' : 'ghost'} 
                  size="sm"
                  onClick={() => setActiveSidebarTab('toc')}
                  className="px-2"
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button 
                  variant={activeSidebarTab === 'bookmarks' ? 'default' : 'ghost'} 
                  size="sm"
                  onClick={() => setActiveSidebarTab('bookmarks')}
                  className="px-2"
                >
                  <Bookmark className="h-4 w-4" />
                </Button>
                <Button 
                  variant={activeSidebarTab === 'annotations' ? 'default' : 'ghost'} 
                  size="sm"
                  onClick={() => setActiveSidebarTab('annotations')}
                  className="px-2"
                >
                  <Highlighter className="h-4 w-4" />
                </Button>
                <Button 
                  variant={activeSidebarTab === 'ai' ? 'default' : 'ghost'} 
                  size="sm"
                  onClick={() => setActiveSidebarTab('ai')}
                  className="px-2"
                >
                  <Sparkles className="h-4 w-4" />
                </Button>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setIsSidebarOpen(false)}
                className="px-2"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Sidebar Content */}
            <div className="flex-1 overflow-y-auto p-3">
              {activeSidebarTab === 'toc' && (
                <div>
                  <h3 className="font-medium mb-2">Table of Contents</h3>
                  <ul className="space-y-1">
                    {tableOfContents.map((item) => (
                      <li 
                        key={item.id} 
                        className="cursor-pointer hover:bg-secondary rounded px-2 py-1"
                        style={{ paddingLeft: `${(item.level - 1) * 12 + 8}px` }}
                        onClick={() => goToPage(item.page)}
                      >
                        <span className={currentPage === item.page ? 'font-medium text-primary' : ''}>
                          {item.title}
                        </span>
                        <span className="text-xs text-muted-foreground ml-2">
                          {item.page}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {activeSidebarTab === 'bookmarks' && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">Bookmarks</h3>
                    <Button variant="ghost" size="sm" onClick={handleAddBookmark}>
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {bookmarks.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No bookmarks yet</p>
                  ) : (
                    <ul className="space-y-1">
                      {bookmarks.map((bookmark) => (
                        <li 
                          key={bookmark.id} 
                          className="flex items-center justify-between cursor-pointer hover:bg-secondary rounded px-2 py-1"
                          onClick={() => goToPage(bookmark.page)}
                        >
                          <span className={currentPage === bookmark.page ? 'font-medium text-primary' : ''}>
                            {bookmark.title}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            p.{bookmark.page}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
              
              {activeSidebarTab === 'annotations' && (
                <div>
                  <h3 className="font-medium mb-2">Annotations</h3>
                  {annotations.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No annotations yet</p>
                  ) : (
                    <ul className="space-y-2">
                      {annotations.map((annotation) => (
                        <li 
                          key={annotation.id} 
                          className="border border-border rounded-md p-2 cursor-pointer hover:bg-secondary/50"
                          onClick={() => goToPage(annotation.page)}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: annotation.color }}
                            />
                            <span className="text-xs text-muted-foreground">
                              p.{annotation.page}
                            </span>
                          </div>
                          <p className="text-sm">{annotation.content}</p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
              
              {activeSidebarTab === 'ai' && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">Page Summary</h3>
                    {isSummarizing ? (
                      <div className="flex items-center justify-center p-4">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                      </div>
                    ) : pageSummary ? (
                      <div className="bg-secondary/50 rounded-md p-3 text-sm">
                        {pageSummary}
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center p-4 bg-secondary/30 rounded-md">
                        <Sparkles className="h-8 w-8 text-muted-foreground mb-2" />
                        <p className="text-sm text-center text-muted-foreground">
                          Click "Summarize Page" to generate a summary of the current page
                        </p>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-2">Ask AI</h3>
                    <div className="space-y-2">
                      <textarea
                        value={aiQuestion}
                        onChange={(e) => setAiQuestion(e.target.value)}
                        placeholder="Ask a question about this page..."
                        className="w-full p-2 text-sm rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                        rows={2}
                      />
                      <Button 
                        onClick={handleAskAI} 
                        disabled={isAiLoading || !aiQuestion.trim()}
                        className="w-full"
                        size="sm"
                      >
                        {isAiLoading ? 'Thinking...' : 'Ask AI'}
                      </Button>
                      
                      {aiResponse && (
                        <div className="bg-secondary/50 rounded-md p-3 text-sm mt-2">
                          {aiResponse}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
        
        {/* PDF Viewer */}
        <div 
          className="flex-1 overflow-hidden"
          style={{ width: `${splitRatio * 100}%` }}
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="h-full flex flex-col">
              {/* PDF Controls */}
              <div className="flex items-center justify-between p-2 border-b border-border bg-card">
                <div className="flex items-center">
                  {!isSidebarOpen && (
                    <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(true)}>
                      <List className="h-4 w-4" />
                    </Button>
                  )}
                  <Button variant="ghost" size="icon" onClick={() => goToPage(currentPage - 1)} disabled={currentPage <= 1}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="mx-2 text-sm">
                    Page {currentPage} of {totalPages || '?'}
                  </span>
                  <Button variant="ghost" size="icon" onClick={() => goToPage(currentPage + 1)} disabled={currentPage >= totalPages}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="flex items-center">
                  <Button variant="ghost" size="icon" onClick={handleZoomOut} disabled={scale <= 0.5}>
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <span className="mx-1 text-sm">{Math.round(scale * 100)}%</span>
                  <Button variant="ghost" size="icon" onClick={handleZoomIn} disabled={scale >= 2.0}>
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={handleRotate}>
                    <RotateCw className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={handleAddBookmark}>
                    <Bookmark className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={handleSummarizePage} disabled={isSummarizing}>
                    <Sparkles className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {/* PDF Content */}
              <div className="flex-1 overflow-auto bg-secondary/30 flex items-center justify-center">
                <PDFViewer
                  url={bookData.pdfUrl}
                  currentPage={currentPage}
                  scale={scale}
                  rotation={rotation}
                  onDocumentLoaded={(doc) => {
                    setPdfDocument(doc);
                    setTotalPages(doc.numPages);
                  }}
                  onPageChange={setCurrentPage}
                  onCreateFlashcard={handleCreateFlashcard}
                  onCreateNote={handleCreateNote}
                  annotations={annotations.filter(a => a.page === currentPage)}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Resize Handle */}
        <div 
          className="w-1 bg-border hover:bg-primary hover:w-2 transition-all cursor-col-resize z-10"
          onMouseDown={handleMouseDown}
        />
        
        {/* Notes Section */}
        <div 
          className="bg-card border-l border-border"
          style={{ width: `${(1 - splitRatio) * 100}%` }}
        >
          <div className="h-full flex flex-col">
            <div className="p-2 border-b border-border flex items-center justify-between">
              <h3 className="font-medium">Notes</h3>
              <Button variant="ghost" size="sm" onClick={handleSaveNotes}>
                <Save className="h-4 w-4" />
              </Button>
            </div>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Take notes here..."
              className="flex-1 p-4 bg-background w-full resize-none focus:outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
}