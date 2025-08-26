/**
 * Utility functions for exporting notes to different formats
 */

/**
 * Export a note to Markdown format
 * @param {Object} note - The note to export
 * @returns {string} - The note in Markdown format
 */
export const exportToMarkdown = (note) => {
  if (!note) return '';
  
  // Create the markdown content
  let markdown = `# ${note.title}\n\n`;
  
  // Add tags if they exist
  if (note.tags && note.tags.length > 0) {
    markdown += 'Tags: ' + note.tags.map(tag => `#${tag}`).join(', ') + '\n\n';
  }
  
  // Add creation and update dates
  if (note.createdAt) {
    markdown += `Created: ${new Date(note.createdAt).toLocaleString()}\n`;
  }
  if (note.updatedAt) {
    markdown += `Updated: ${new Date(note.updatedAt).toLocaleString()}\n`;
  }
  
  markdown += '\n---\n\n';
  
  // Add the note content
  markdown += note.content;
  
  return markdown;
};

/**
 * Export a note to Anki format (simplified version)
 * @param {Object} note - The note to export
 * @returns {Object} - The note in a format ready for Anki export
 */
export const exportToAnki = (note) => {
  if (!note) return null;
  
  // In a real implementation, this would generate a proper Anki package
  // For now, we'll just return a structured object that could be used to create an Anki package
  
  // Generate simple Q&A pairs from the note content
  // This is a very simplified approach - in a real app, you would use NLP or LLMs to generate better flashcards
  const sentences = note.content.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  const flashcards = sentences.map((sentence, index) => {
    // Very simple approach: use the first half as question, second half as answer
    const midpoint = Math.floor(sentence.length / 2);
    const question = sentence.substring(0, midpoint) + '...';
    const answer = sentence;
    
    return {
      id: `${note.id}-${index}`,
      question,
      answer,
      tags: note.tags || []
    };
  });
  
  return {
    deckName: `${note.title}`,
    flashcards,
    metadata: {
      source: 'AI Note System',
      created: new Date().toISOString(),
      noteId: note.id,
      tags: note.tags || []
    }
  };
};

/**
 * Export a note to PDF format
 * @param {Object} note - The note to export
 * @returns {Promise<Blob>} - A promise that resolves to a PDF blob
 */
export const exportToPDF = async (note) => {
  if (!note) return null;
  
  // In a real implementation, this would generate a proper PDF
  // For now, we'll just return a mock implementation
  
  // Convert the note to HTML
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${note.title}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .tags { color: #666; margin-bottom: 20px; }
        .content { line-height: 1.6; }
        .metadata { color: #888; font-size: 0.8em; margin-top: 40px; }
      </style>
    </head>
    <body>
      <h1>${note.title}</h1>
      <div class="tags">Tags: ${(note.tags || []).join(', ')}</div>
      <div class="content">${note.content.replace(/\n/g, '<br>')}</div>
      <div class="metadata">
        Created: ${new Date(note.createdAt || Date.now()).toLocaleString()}<br>
        Last updated: ${new Date(note.updatedAt || Date.now()).toLocaleString()}
      </div>
    </body>
    </html>
  `;
  
  // In a real app, you would use a library like jsPDF or html2pdf to convert HTML to PDF
  // For this mock implementation, we'll just return the HTML as a blob
  const blob = new Blob([html], { type: 'text/html' });
  return blob;
};

/**
 * Download content as a file
 * @param {string|Blob} content - The content to download
 * @param {string} filename - The filename to use
 * @param {string} type - The MIME type of the content
 */
export const downloadFile = (content, filename, type = 'text/plain') => {
  const blob = content instanceof Blob ? content : new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  
  // Clean up
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
};

/**
 * Export a note to the specified format and download it
 * @param {Object} note - The note to export
 * @param {string} format - The format to export to ('markdown', 'anki', or 'pdf')
 */
export const exportAndDownloadNote = async (note, format) => {
  if (!note) return;
  
  try {
    switch (format.toLowerCase()) {
      case 'markdown': {
        const markdown = exportToMarkdown(note);
        downloadFile(markdown, `${note.title}.md`, 'text/markdown');
        return true;
      }
      
      case 'anki': {
        const ankiData = exportToAnki(note);
        // In a real app, you would convert ankiData to a proper .apkg file
        // For now, we'll just download it as JSON
        downloadFile(
          JSON.stringify(ankiData, null, 2),
          `${note.title}.json`,
          'application/json'
        );
        return true;
      }
      
      case 'pdf': {
        const pdfBlob = await exportToPDF(note);
        downloadFile(pdfBlob, `${note.title}.html`, 'text/html');
        return true;
      }
      
      default:
        console.error(`Unsupported export format: ${format}`);
        return false;
    }
  } catch (error) {
    console.error(`Error exporting note to ${format}:`, error);
    return false;
  }
};