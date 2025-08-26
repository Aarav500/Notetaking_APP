import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Share2, 
  Download, 
  Maximize2, 
  Filter, 
  Plus, 
  FileText, 
  GitBranch, 
  Network, 
  Clock, 
  BarChart2, 
  CloudLightning,
  Search,
  ChevronRight,
  ChevronDown,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

// Mock data for visualizations
const mockVisualizations = [
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
  {
    id: 3,
    title: 'Machine Learning Timeline',
    type: 'timeline',
    date: '2025-07-25',
    sourceNote: 'History of AI',
    sourceNoteId: 5,
    thumbnail: 'https://via.placeholder.com/400x250?text=Timeline',
    description: 'Timeline of major developments in machine learning'
  },
  {
    id: 4,
    title: 'AI Knowledge Graph',
    type: 'knowledge_graph',
    date: '2025-07-24',
    sourceNote: 'Artificial Intelligence Overview',
    sourceNoteId: 2,
    thumbnail: 'https://via.placeholder.com/400x250?text=Knowledge+Graph',
    description: 'Knowledge graph connecting AI concepts and applications'
  },
  {
    id: 5,
    title: 'Data Science Workflow',
    type: 'flowchart',
    date: '2025-07-22',
    sourceNote: 'Data Science Methodology',
    sourceNoteId: 7,
    thumbnail: 'https://via.placeholder.com/400x250?text=Flowchart',
    description: 'Flowchart of the data science workflow from data collection to deployment'
  },
  {
    id: 6,
    title: 'ML Algorithms Comparison',
    type: 'treegraph',
    date: '2025-07-20',
    sourceNote: 'Machine Learning Algorithms',
    sourceNoteId: 8,
    thumbnail: 'https://via.placeholder.com/400x250?text=Tree+Graph',
    description: 'Tree graph comparing different machine learning algorithms'
  },
];

// Visualization types
const visualizationTypes = [
  { id: 'all', label: 'All Types' },
  { id: 'mindmap', label: 'Mind Maps', icon: Share2 },
  { id: 'flowchart', label: 'Flowcharts', icon: GitBranch },
  { id: 'timeline', label: 'Timelines', icon: Clock },
  { id: 'knowledge_graph', label: 'Knowledge Graphs', icon: Network },
  { id: 'treegraph', label: 'Tree Graphs', icon: GitBranch },
  { id: 'wordcloud', label: 'Word Clouds', icon: CloudLightning },
];

export default function Visualizations() {
  const { toast } = useToast();
  const [selectedType, setSelectedType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'
  const [selectedVisualization, setSelectedVisualization] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Filter and sort visualizations
  const filteredVisualizations = mockVisualizations
    .filter(viz => {
      const matchesSearch = viz.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                           viz.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           viz.sourceNote.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = selectedType === 'all' || viz.type === selectedType;
      
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      const dateA = new Date(a.date);
      const dateB = new Date(b.date);
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });

  const handleCreateVisualization = () => {
    toast({
      title: 'Create Visualization',
      description: 'Select a note to create a new visualization',
    });
  };

  const handleViewVisualization = (visualization) => {
    setSelectedVisualization(visualization);
    setIsModalOpen(true);
  };

  const handleDownload = (id) => {
    toast({
      title: 'Visualization Downloaded',
      description: 'The visualization has been downloaded as PNG',
    });
  };

  const handleShare = (id) => {
    toast({
      title: 'Share Link Copied',
      description: 'A shareable link has been copied to your clipboard',
    });
  };

  const handleDelete = (id) => {
    toast({
      title: 'Visualization Deleted',
      description: 'The visualization has been deleted',
      variant: 'destructive',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Visualizations</h1>
        <Button onClick={handleCreateVisualization}>
          <Plus className="mr-2 h-4 w-4" />
          Create Visualization
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search visualizations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-md border border-input bg-background pl-10 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <div className="relative">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="appearance-none rounded-md border border-input bg-background px-3 py-2 pr-8 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {visualizationTypes.map(type => (
                <option key={type.id} value={type.id}>{type.label}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>
          
          <Button
            variant="outline"
            size="icon"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            title={`Sort by date ${sortOrder === 'asc' ? 'newest first' : 'oldest first'}`}
          >
            {sortOrder === 'asc' ? (
              <Clock className="h-4 w-4" />
            ) : (
              <Clock className="h-4 w-4 rotate-180" />
            )}
          </Button>
        </div>
      </div>

      {/* Visualization Types */}
      <div className="flex flex-wrap gap-2">
        {visualizationTypes.map((type) => (
          <Button
            key={type.id}
            variant={selectedType === type.id ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedType(type.id)}
            className="flex items-center"
          >
            {type.icon && <type.icon className="mr-2 h-4 w-4" />}
            {type.label}
          </Button>
        ))}
      </div>

      {/* Visualizations Grid */}
      {filteredVisualizations.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-12 text-center"
        >
          <BarChart2 className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No visualizations found</h3>
          <p className="text-muted-foreground mt-1">
            {searchTerm || selectedType !== 'all' 
              ? 'Try a different search term or filter' 
              : 'Create your first visualization to get started'}
          </p>
          <Button onClick={handleCreateVisualization} className="mt-4">
            <Plus className="mr-2 h-4 w-4" />
            Create Visualization
          </Button>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVisualizations.map((visualization, index) => (
            <motion.div
              key={visualization.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-card rounded-lg border border-border overflow-hidden hover:shadow-md transition-shadow"
            >
              <div 
                className="h-48 bg-muted cursor-pointer relative group"
                onClick={() => handleViewVisualization(visualization)}
              >
                <img 
                  src={visualization.thumbnail} 
                  alt={visualization.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Button variant="secondary">
                    <Maximize2 className="mr-2 h-4 w-4" />
                    View Full Size
                  </Button>
                </div>
              </div>
              
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">{visualization.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {new Date(visualization.date).toLocaleDateString()} • 
                      {visualizationTypes.find(t => t.id === visualization.type)?.label}
                    </p>
                  </div>
                  
                  <div className="flex">
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDownload(visualization.id)}
                      title="Download"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleShare(visualization.id)}
                      title="Share"
                    >
                      <Share2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <p className="text-sm mt-2 line-clamp-2">{visualization.description}</p>
                
                <div className="mt-3 flex items-center text-sm">
                  <FileText className="h-4 w-4 mr-1 text-muted-foreground" />
                  <span className="text-muted-foreground">Source: </span>
                  <a 
                    href={`/notes/${visualization.sourceNoteId}`}
                    className="ml-1 text-primary hover:underline"
                  >
                    {visualization.sourceNote}
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Visualization Modal */}
      {isModalOpen && selectedVisualization && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card border border-border rounded-lg shadow-lg w-full max-w-5xl max-h-[90vh] flex flex-col"
          >
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h2 className="text-xl font-semibold">{selectedVisualization.title}</h2>
              <Button 
                variant="ghost" 
                size="icon"
                onClick={() => setIsModalOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="flex-1 overflow-auto p-4">
              <div className="bg-muted rounded-lg h-[60vh] flex items-center justify-center">
                <img 
                  src={selectedVisualization.thumbnail} 
                  alt={selectedVisualization.title}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
              
              <div className="mt-4">
                <h3 className="font-medium">Description</h3>
                <p className="text-muted-foreground mt-1">{selectedVisualization.description}</p>
              </div>
              
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium">Type</h3>
                  <p className="text-muted-foreground mt-1">
                    {visualizationTypes.find(t => t.id === selectedVisualization.type)?.label}
                  </p>
                </div>
                <div>
                  <h3 className="font-medium">Created</h3>
                  <p className="text-muted-foreground mt-1">
                    {new Date(selectedVisualization.date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <h3 className="font-medium">Source Note</h3>
                  <a 
                    href={`/notes/${selectedVisualization.sourceNoteId}`}
                    className="text-primary hover:underline mt-1 block"
                  >
                    {selectedVisualization.sourceNote}
                  </a>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 border-t border-border">
              <Button 
                variant="destructive"
                onClick={() => {
                  handleDelete(selectedVisualization.id);
                  setIsModalOpen(false);
                }}
              >
                Delete
              </Button>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline"
                  onClick={() => handleShare(selectedVisualization.id)}
                >
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </Button>
                <Button 
                  onClick={() => handleDownload(selectedVisualization.id)}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}