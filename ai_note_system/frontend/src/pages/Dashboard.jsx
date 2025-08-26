import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  PenTool, 
  BarChart2, 
  Clock, 
  BookOpen, 
  Brain, 
  Zap, 
  Plus,
  ChevronRight,
  Flame,
  FolderOpen,
  Calendar,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import KnowledgeGraphPreview from '@/components/KnowledgeGraphPreview';

// Mock data for recent notes
const recentNotes = [
  { id: 1, title: 'Machine Learning Fundamentals', category: 'AI', date: '2025-07-28', tags: ['ML', 'AI', 'Neural Networks'] },
  { id: 2, title: 'React Hooks Deep Dive', category: 'Programming', date: '2025-07-25', tags: ['React', 'JavaScript', 'Hooks'] },
  { id: 3, title: 'Advanced Data Structures', category: 'Computer Science', date: '2025-07-22', tags: ['Algorithms', 'Data Structures'] },
];

// Mock data for quick stats
const quickStats = [
  { label: 'Total Notes', value: 42, icon: FileText },
  { label: 'Visualizations', value: 15, icon: BarChart2 },
  { label: 'Study Hours', value: '28h', icon: Clock },
  { label: 'Knowledge Topics', value: 8, icon: Brain },
  { label: 'XP Points', value: 1250, icon: Zap },
  { label: 'Flashcard Streak', value: '7 days', icon: Flame },
  { label: 'Active Projects', value: 3, icon: FolderOpen },
];

// Feature cards
const featureCards = [
  { 
    title: 'Process New Input', 
    description: 'Add new notes from text, PDF, image, or voice', 
    icon: PenTool,
    color: 'bg-blue-500/10 text-blue-500',
    link: '/process'
  },
  { 
    title: 'Study Materials', 
    description: 'Review your notes and generated study materials', 
    icon: BookOpen,
    color: 'bg-purple-500/10 text-purple-500',
    link: '/notes'
  },
  { 
    title: 'Quick Recall', 
    description: 'Test your knowledge with generated questions', 
    icon: Zap,
    color: 'bg-amber-500/10 text-amber-500',
    link: '/notes'
  },
];

export default function Dashboard() {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Button onClick={handleCreateNote} disabled={isLoading}>
          <Plus className="mr-2 h-4 w-4" />
          New Note
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-card rounded-lg border border-border p-4 flex items-center gap-4"
          >
            <div className="bg-primary/10 p-3 rounded-full">
              <stat.icon className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-bold">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {featureCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 + index * 0.1 }}
            className="bg-card rounded-lg border border-border p-6 hover:shadow-md transition-shadow"
          >
            <div className={`${card.color} p-3 rounded-full w-fit mb-4`}>
              <card.icon className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold mb-2">{card.title}</h3>
            <p className="text-muted-foreground mb-4">{card.description}</p>
            <Button variant="outline" asChild>
              <a href={card.link} className="flex items-center">
                Get Started <ChevronRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
          </motion.div>
        ))}
      </div>

      {/* Knowledge Graph and Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Knowledge Graph */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <KnowledgeGraphPreview className="h-[350px]" />
        </motion.div>
        
        {/* Activity Heatmap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-card rounded-lg border border-border overflow-hidden"
        >
          <div className="p-3 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              <h3 className="font-medium">Activity Heatmap</h3>
            </div>
            <Button variant="ghost" size="sm" className="h-8 px-2">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="p-4 flex flex-col items-center justify-center h-[302px]">
            <div className="grid grid-cols-7 gap-1">
              {Array.from({ length: 7 * 10 }).map((_, i) => {
                // Generate random activity level (0-4)
                const activityLevel = Math.floor(Math.random() * 5);
                const bgColorClass = activityLevel === 0 
                  ? 'bg-muted' 
                  : activityLevel === 1 
                    ? 'bg-emerald-200 dark:bg-emerald-900/30' 
                    : activityLevel === 2 
                      ? 'bg-emerald-300 dark:bg-emerald-800/50' 
                      : activityLevel === 3 
                        ? 'bg-emerald-400 dark:bg-emerald-700/70' 
                        : 'bg-emerald-500 dark:bg-emerald-600';
                
                return (
                  <div 
                    key={i} 
                    className={`w-6 h-6 rounded-sm ${bgColorClass} cursor-pointer transition-colors hover:opacity-80`}
                    title={`${activityLevel} activities on July ${i % 30 + 1}, 2025`}
                  />
                );
              })}
            </div>
            <div className="flex items-center gap-2 mt-4">
              <span className="text-xs text-muted-foreground">Less</span>
              <div className="flex gap-1">
                <div className="w-3 h-3 rounded-sm bg-muted" />
                <div className="w-3 h-3 rounded-sm bg-emerald-200 dark:bg-emerald-900/30" />
                <div className="w-3 h-3 rounded-sm bg-emerald-300 dark:bg-emerald-800/50" />
                <div className="w-3 h-3 rounded-sm bg-emerald-400 dark:bg-emerald-700/70" />
                <div className="w-3 h-3 rounded-sm bg-emerald-500 dark:bg-emerald-600" />
              </div>
              <span className="text-xs text-muted-foreground">More</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Notes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Notes</h2>
          <Button variant="ghost" asChild>
            <a href="/notes">View All</a>
          </Button>
        </div>
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="divide-y divide-border">
            {recentNotes.map((note, index) => (
              <motion.div
                key={note.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <a href={`/notes/${note.id}`} className="text-lg font-medium hover:underline">
                      {note.title}
                    </a>
                    <p className="text-sm text-muted-foreground">
                      {note.category} • {new Date(note.date).toLocaleDateString()}
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" asChild>
                    <a href={`/notes/${note.id}`}>
                      <ChevronRight className="h-5 w-5" />
                    </a>
                  </Button>
                </div>
                <div className="flex gap-2 mt-2">
                  {note.tags.map((tag) => (
                    <span
                      key={tag}
                      className="bg-secondary text-secondary-foreground text-xs px-2 py-1 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}