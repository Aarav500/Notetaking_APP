import { useState, useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  FileText, 
  PenTool, 
  BarChart2, 
  Search, 
  Settings, 
  Menu, 
  X, 
  Moon, 
  Sun, 
  LogOut,
  BookOpen
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useTheme } from '@/components/theme-provider';
import { useToast } from '@/hooks/use-toast';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/notes', label: 'Notes', icon: FileText },
  { path: '/notes', label: 'Reading', icon: BookOpen },
  { path: '/process', label: 'Process Input', icon: PenTool },
  { path: '/visualizations', label: 'Visualizations', icon: BarChart2 },
  { path: '/search', label: 'Search', icon: Search },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function MainLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { theme, setTheme, themes } = useTheme();
  const { toast } = useToast();
  const location = useLocation();

  // Close sidebar on mobile by default
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Close sidebar on route change on mobile
  useEffect(() => {
    if (window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  }, [location.pathname]);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    toast({
      title: `Theme Changed`,
      description: `Switched to ${newTheme} mode`,
      duration: 2000,
    });
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogout = () => {
    toast({
      title: 'Logged Out',
      description: 'You have been logged out successfully',
      variant: 'destructive',
    });
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border md:relative"
          >
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h1 className="text-xl font-bold">Pansophy</h1>
                <Button variant="ghost" size="icon" onClick={toggleSidebar} className="md:hidden">
                  <X className="h-5 w-5" />
                </Button>
              </div>
              
              <nav className="flex-1 overflow-y-auto p-2">
                <ul className="space-y-1">
                  {navItems.map((item) => (
                    <li key={item.path}>
                      <NavLink
                        to={item.path}
                        className={({ isActive }) =>
                          `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                            isActive
                              ? 'bg-primary text-primary-foreground'
                              : 'text-foreground hover:bg-secondary'
                          }`
                        }
                      >
                        <item.icon className="h-5 w-5" />
                        <span>{item.label}</span>
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </nav>
              
              <div className="p-4 border-t border-border">
                <div className="flex items-center justify-between">
                  <Button variant="ghost" size="icon" onClick={toggleTheme}>
                    {theme === 'dark' ? (
                      <Sun className="h-5 w-5" />
                    ) : (
                      <Moon className="h-5 w-5" />
                    )}
                  </Button>
                  <Button variant="ghost" size="icon" onClick={handleLogout}>
                    <LogOut className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex flex-col flex-1 w-full overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-border bg-card flex items-center justify-between px-4">
          <Button variant="ghost" size="icon" onClick={toggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>
          <div className="text-lg font-semibold">
            {navItems.find((item) => item.path === location.pathname)?.label || 'AI Note System'}
          </div>
          <div className="w-10" /> {/* Spacer for alignment */}
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}