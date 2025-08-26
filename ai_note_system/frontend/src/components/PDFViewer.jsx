import { useState, useEffect, useRef, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Highlighter, 
  FileText, 
  MessageSquare, 
  Copy, 
  X,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';

// Set up PDF.js worker
// In a real app, you would need to set up the worker properly
// For example: pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function PDFViewer({
  url,
  currentPage,
  scale = 1.0,
  rotation = 0,
  onDocumentLoaded,
  onPageChange,
  onCreateFlashcard,
  onCreateNote,
  annotations = []
}) {
  const [numPages, setNumPages] = useState(null);
  const [pageWidth, setPageWidth] = useState(0);
  const [pageHeight, setPageHeight] = useState(0);
  const [isTextSelected, setIsTextSelected] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [selectionPosition, setSelectionPosition] = useState({ x: 0, y: 0 });
  const [showSelectionMenu, setShowSelectionMenu] = useState(false);
  const pageRef = useRef(null);
  const selectionMenuRef = useRef(null);

  // Handle document load success
  const onDocumentLoadSuccess = (document) => {
    setNumPages(document.numPages);
    if (onDocumentLoaded) {
      onDocumentLoaded(document);
    }
  };

  // Handle page render success
  const onPageRenderSuccess = (page) => {
    setPageWidth(page.width);
    setPageHeight(page.height);
  };

  // Handle text selection
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();
    const text = selection.toString().trim();
    
    if (text) {
      setSelectedText(text);
      setIsTextSelected(true);
      
      // Get selection position for the popup menu
      if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        if (pageRef.current) {
          const pageRect = pageRef.current.getBoundingClientRect();
          setSelectionPosition({
            x: rect.left - pageRect.left + rect.width / 2,
            y: rect.top - pageRect.top
          });
        }
      }
      
      setShowSelectionMenu(true);
    } else {
      setIsTextSelected(false);
      setShowSelectionMenu(false);
    }
  }, []);

  // Close selection menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectionMenuRef.current && !selectionMenuRef.current.contains(event.target)) {
        setShowSelectionMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Handle creating flashcard
  const handleCreateFlashcard = () => {
    if (onCreateFlashcard && selectedText) {
      onCreateFlashcard(selectedText);
      setShowSelectionMenu(false);
      window.getSelection().removeAllRanges();
    }
  };

  // Handle creating note
  const handleCreateNote = () => {
    if (onCreateNote && selectedText) {
      onCreateNote(selectedText);
      setShowSelectionMenu(false);
      window.getSelection().removeAllRanges();
    }
  };

  // Handle copying text
  const handleCopyText = () => {
    if (selectedText) {
      navigator.clipboard.writeText(selectedText);
      setShowSelectionMenu(false);
      window.getSelection().removeAllRanges();
    }
  };

  // Render annotations
  const renderAnnotations = () => {
    return annotations.map((annotation) => (
      <div
        key={annotation.id}
        className="absolute pointer-events-none"
        style={{
          left: `${annotation.position.x}px`,
          top: `${annotation.position.y}px`,
          width: `${annotation.position.width}px`,
          height: `${annotation.position.height}px`,
          backgroundColor: `${annotation.color}80`, // Add transparency
          border: `2px solid ${annotation.color}`,
          borderRadius: '2px',
          zIndex: 10
        }}
      />
    ));
  };

  return (
    <div 
      className="relative flex items-center justify-center h-full w-full overflow-auto"
      onMouseUp={handleTextSelection}
      ref={pageRef}
    >
      <Document
        file={url}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        }
        error={
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <FileText className="h-12 w-12 text-destructive mb-4" />
            <h3 className="text-lg font-medium">Error loading PDF</h3>
            <p className="text-muted-foreground mt-2">
              The PDF could not be loaded. Please check the URL and try again.
            </p>
          </div>
        }
      >
        <Page
          pageNumber={currentPage}
          scale={scale}
          rotate={rotation}
          onRenderSuccess={onPageRenderSuccess}
          loading={
            <div className="flex items-center justify-center h-[600px] w-[400px]">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          }
          className="shadow-lg"
        >
          {/* Render annotations */}
          {renderAnnotations()}
          
          {/* Text selection menu */}
          <AnimatePresence>
            {showSelectionMenu && (
              <motion.div
                ref={selectionMenuRef}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute bg-card border border-border rounded-md shadow-lg z-20 flex"
                style={{
                  left: `${selectionPosition.x}px`,
                  top: `${selectionPosition.y - 40}px`,
                  transform: 'translateX(-50%)'
                }}
              >
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="px-2 py-1 h-8"
                  onClick={handleCreateFlashcard}
                  title="Create Flashcard"
                >
                  <Zap className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="px-2 py-1 h-8"
                  onClick={handleCreateNote}
                  title="Add to Notes"
                >
                  <MessageSquare className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="px-2 py-1 h-8"
                  onClick={handleCopyText}
                  title="Copy Text"
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="px-2 py-1 h-8"
                  onClick={() => setShowSelectionMenu(false)}
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </Page>
      </Document>
    </div>
  );
}