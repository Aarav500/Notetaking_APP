import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Moon, 
  Sun, 
  Bell, 
  BellOff, 
  Save, 
  User, 
  Lock, 
  LogOut, 
  Trash2, 
  Download, 
  Upload, 
  Globe, 
  Palette, 
  Monitor, 
  Laptop, 
  Smartphone, 
  Check,
  X,
  HelpCircle,
  FileText,
  Mail,
  MessageSquare,
  Github,
  Twitter,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useTheme } from '@/components/theme-provider';

// Mock user data
const mockUser = {
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatar: 'https://via.placeholder.com/150',
  joinDate: '2025-01-15',
};

export default function Settings() {
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  
  // Settings state
  const [activeTab, setActiveTab] = useState('appearance');
  const [isLoading, setIsLoading] = useState(false);
  
  // Appearance settings
  const [selectedTheme, setSelectedTheme] = useState(theme);
  const [fontSize, setFontSize] = useState('medium');
  const [codeBlockTheme, setCodeBlockTheme] = useState('github');
  
  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [reminderNotifications, setReminderNotifications] = useState(true);
  const [updateNotifications, setUpdateNotifications] = useState(true);
  
  // Account settings
  const [name, setName] = useState(mockUser.name);
  const [email, setEmail] = useState(mockUser.email);
  
  // Privacy settings
  const [shareUsageData, setShareUsageData] = useState(false);
  const [storeSearchHistory, setStoreSearchHistory] = useState(true);
  
  // Data settings
  const [autoBackup, setAutoBackup] = useState(true);
  const [backupFrequency, setBackupFrequency] = useState('weekly');
  
  // Handle save settings
  const handleSaveSettings = () => {
    setIsLoading(true);
    
    // Apply theme change immediately
    if (selectedTheme !== theme) {
      setTheme(selectedTheme);
    }
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      
      toast({
        title: 'Settings Saved',
        description: 'Your settings have been updated successfully',
      });
    }, 1000);
  };
  
  // Handle account deletion
  const handleDeleteAccount = () => {
    toast({
      title: 'Account Deletion',
      description: 'This feature is not available in the demo',
      variant: 'destructive',
    });
  };
  
  // Handle logout
  const handleLogout = () => {
    toast({
      title: 'Logged Out',
      description: 'You have been logged out successfully',
    });
  };
  
  // Handle data export
  const handleExportData = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      
      toast({
        title: 'Data Exported',
        description: 'Your data has been exported successfully',
      });
    }, 1500);
  };
  
  // Handle data import
  const handleImportData = () => {
    toast({
      title: 'Data Import',
      description: 'Please select a file to import',
    });
  };
  
  // Settings tabs
  const tabs = [
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'account', label: 'Account', icon: User },
    { id: 'privacy', label: 'Privacy', icon: Lock },
    { id: 'data', label: 'Data Management', icon: FileText },
    { id: 'help', label: 'Help & Support', icon: HelpCircle },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <Button onClick={handleSaveSettings} disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Settings'}
          {!isLoading && <Save className="ml-2 h-4 w-4" />}
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Settings Navigation */}
        <div className="md:w-64 flex-shrink-0">
          <div className="bg-card rounded-lg border border-border overflow-hidden">
            <nav className="flex flex-col">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-secondary'
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <tab.icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="flex-1">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="bg-card rounded-lg border border-border p-6"
          >
            {/* Appearance Settings */}
            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Appearance Settings</h2>
                
                {/* Theme Selection */}
                <div className="space-y-3">
                  <h3 className="font-medium">Theme</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div
                      className={`border rounded-lg p-4 flex flex-col items-center gap-2 cursor-pointer transition-colors ${
                        selectedTheme === 'light'
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => setSelectedTheme('light')}
                    >
                      <div className="bg-white border border-gray-200 rounded-full p-2">
                        <Sun className="h-5 w-5 text-amber-500" />
                      </div>
                      <span>Light</span>
                    </div>
                    
                    <div
                      className={`border rounded-lg p-4 flex flex-col items-center gap-2 cursor-pointer transition-colors ${
                        selectedTheme === 'dark'
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => setSelectedTheme('dark')}
                    >
                      <div className="bg-gray-900 border border-gray-700 rounded-full p-2">
                        <Moon className="h-5 w-5 text-indigo-400" />
                      </div>
                      <span>Dark</span>
                    </div>
                    
                    <div
                      className={`border rounded-lg p-4 flex flex-col items-center gap-2 cursor-pointer transition-colors ${
                        selectedTheme === 'system'
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                      onClick={() => setSelectedTheme('system')}
                    >
                      <div className="bg-gradient-to-r from-white to-gray-900 border border-gray-300 rounded-full p-2">
                        <Monitor className="h-5 w-5" />
                      </div>
                      <span>System</span>
                    </div>
                  </div>
                </div>
                
                {/* Font Size */}
                <div className="space-y-3">
                  <h3 className="font-medium">Font Size</h3>
                  <div className="flex items-center gap-4">
                    <select
                      value={fontSize}
                      onChange={(e) => setFontSize(e.target.value)}
                      className="rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="small">Small</option>
                      <option value="medium">Medium</option>
                      <option value="large">Large</option>
                    </select>
                    <div className="text-sm text-muted-foreground">
                      Adjust the font size for better readability
                    </div>
                  </div>
                </div>
                
                {/* Code Block Theme */}
                <div className="space-y-3">
                  <h3 className="font-medium">Code Block Theme</h3>
                  <div className="flex items-center gap-4">
                    <select
                      value={codeBlockTheme}
                      onChange={(e) => setCodeBlockTheme(e.target.value)}
                      className="rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <option value="github">GitHub</option>
                      <option value="vscode">VS Code</option>
                      <option value="dracula">Dracula</option>
                      <option value="monokai">Monokai</option>
                    </select>
                    <div className="text-sm text-muted-foreground">
                      Choose a syntax highlighting theme for code blocks
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Notification Settings */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Notification Settings</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Email Notifications</h3>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications about important updates via email
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        emailNotifications ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setEmailNotifications(!emailNotifications)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          emailNotifications ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Reminder Notifications</h3>
                      <p className="text-sm text-muted-foreground">
                        Receive reminders for scheduled study sessions
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        reminderNotifications ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setReminderNotifications(!reminderNotifications)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          reminderNotifications ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Update Notifications</h3>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications about new features and updates
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        updateNotifications ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setUpdateNotifications(!updateNotifications)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          updateNotifications ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h3 className="font-medium mb-3">Notification Channels</h3>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="channel-email"
                        checked={true}
                        className="rounded border-input h-4 w-4"
                        readOnly
                      />
                      <label htmlFor="channel-email" className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Email
                      </label>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="channel-browser"
                        checked={true}
                        className="rounded border-input h-4 w-4"
                        readOnly
                      />
                      <label htmlFor="channel-browser" className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Browser
                      </label>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="channel-desktop"
                        checked={false}
                        className="rounded border-input h-4 w-4"
                        readOnly
                      />
                      <label htmlFor="channel-desktop" className="flex items-center gap-2">
                        <Monitor className="h-4 w-4" />
                        Desktop
                      </label>
                      <span className="text-xs bg-secondary text-secondary-foreground px-2 py-0.5 rounded">Coming Soon</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Account Settings */}
            {activeTab === 'account' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Account Settings</h2>
                
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full overflow-hidden bg-muted">
                    <img
                      src={mockUser.avatar}
                      alt="Profile"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  <div>
                    <h3 className="font-medium">{mockUser.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      Member since {new Date(mockUser.joinDate).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <Button variant="outline" size="sm" className="ml-auto">
                    Change Avatar
                  </Button>
                </div>
                
                <div className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <label htmlFor="name" className="text-sm font-medium">
                      Full Name
                    </label>
                    <input
                      id="name"
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-medium">
                      Email Address
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    />
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border space-y-4">
                  <Button variant="outline" onClick={() => toast({ title: 'Password Change', description: 'Password change functionality is not available in the demo' })}>
                    Change Password
                  </Button>
                  
                  <div className="flex items-center justify-between">
                    <Button variant="outline" onClick={handleLogout}>
                      <LogOut className="mr-2 h-4 w-4" />
                      Log Out
                    </Button>
                    
                    <Button variant="destructive" onClick={handleDeleteAccount}>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Account
                    </Button>
                  </div>
                </div>
              </div>
            )}
            
            {/* Privacy Settings */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Privacy Settings</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Share Usage Data</h3>
                      <p className="text-sm text-muted-foreground">
                        Help us improve by sharing anonymous usage data
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        shareUsageData ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setShareUsageData(!shareUsageData)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          shareUsageData ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Store Search History</h3>
                      <p className="text-sm text-muted-foreground">
                        Save your search history for quick access
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        storeSearchHistory ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setStoreSearchHistory(!storeSearchHistory)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          storeSearchHistory ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h3 className="font-medium mb-3">Data Privacy</h3>
                  
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Your data is stored locally on your device. You can export or delete your data at any time.
                    </p>
                    
                    <div className="flex gap-4">
                      <Button variant="outline" onClick={() => toast({ title: 'Privacy Policy', description: 'Privacy policy would open in a new tab' })}>
                        View Privacy Policy
                      </Button>
                      
                      <Button variant="outline" onClick={() => toast({ title: 'Clear Data', description: 'This would clear all your local data' })}>
                        Clear All Data
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Data Management */}
            {activeTab === 'data' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Data Management</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Automatic Backups</h3>
                      <p className="text-sm text-muted-foreground">
                        Automatically backup your data to prevent loss
                      </p>
                    </div>
                    <button
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${
                        autoBackup ? 'bg-primary' : 'bg-muted'
                      }`}
                      onClick={() => setAutoBackup(!autoBackup)}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white transition-transform ${
                          autoBackup ? 'translate-x-6' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                  
                  {autoBackup && (
                    <div className="ml-6 space-y-2">
                      <label htmlFor="backup-frequency" className="text-sm font-medium">
                        Backup Frequency
                      </label>
                      <select
                        id="backup-frequency"
                        value={backupFrequency}
                        onChange={(e) => setBackupFrequency(e.target.value)}
                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>
                  )}
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h3 className="font-medium mb-3">Manual Data Management</h3>
                  
                  <div className="space-y-4">
                    <div className="flex flex-col sm:flex-row gap-4">
                      <Button onClick={handleExportData} className="flex-1">
                        <Download className="mr-2 h-4 w-4" />
                        Export All Data
                      </Button>
                      
                      <Button onClick={handleImportData} variant="outline" className="flex-1">
                        <Upload className="mr-2 h-4 w-4" />
                        Import Data
                      </Button>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">
                      Export your data as a JSON file that you can import later or on another device.
                    </p>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h3 className="font-medium mb-3">Storage Usage</h3>
                  
                  <div className="space-y-3">
                    <div className="w-full bg-secondary rounded-full h-2.5">
                      <div className="bg-primary h-2.5 rounded-full w-[45%]"></div>
                    </div>
                    
                    <div className="flex justify-between text-sm">
                      <span>45 MB used</span>
                      <span>100 MB total</span>
                    </div>
                    
                    <Button variant="outline" size="sm" onClick={() => toast({ title: 'Storage Management', description: 'This would open storage management options' })}>
                      Manage Storage
                    </Button>
                  </div>
                </div>
              </div>
            )}
            
            {/* Help & Support */}
            {activeTab === 'help' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Help & Support</h2>
                
                <div className="space-y-4">
                  <div className="bg-secondary/50 rounded-lg p-4">
                    <h3 className="font-medium flex items-center gap-2">
                      <HelpCircle className="h-5 w-5 text-primary" />
                      Need Help?
                    </h3>
                    <p className="text-sm text-muted-foreground mt-2">
                      If you have any questions or need assistance, check out our documentation or contact support.
                    </p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        Documentation
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Contact Support
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <h3 className="font-medium">Frequently Asked Questions</h3>
                    
                    <div className="space-y-3">
                      <div className="border border-border rounded-lg p-4">
                        <h4 className="font-medium">How do I export my notes?</h4>
                        <p className="text-sm text-muted-foreground mt-2">
                          You can export your notes by going to the Data Management tab and clicking on "Export All Data" or by selecting individual notes and using the export option.
                        </p>
                      </div>
                      
                      <div className="border border-border rounded-lg p-4">
                        <h4 className="font-medium">Can I use the app offline?</h4>
                        <p className="text-sm text-muted-foreground mt-2">
                          Yes, the app works offline and will sync your changes when you're back online.
                        </p>
                      </div>
                      
                      <div className="border border-border rounded-lg p-4">
                        <h4 className="font-medium">How do I create visualizations from my notes?</h4>
                        <p className="text-sm text-muted-foreground mt-2">
                          Open a note and click on the "Visualize" button to generate different types of visualizations based on your note content.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <h3 className="font-medium mb-3">About</h3>
                  
                  <div className="space-y-2">
                    <p className="text-sm">
                      <span className="font-semibold">Pansophy</span> - AI Note System
                    </p>
                    <p className="text-sm text-muted-foreground">Version 0.1.0</p>
                    
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Github className="h-4 w-4" />
                        GitHub
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Twitter className="h-4 w-4" />
                        Twitter
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}