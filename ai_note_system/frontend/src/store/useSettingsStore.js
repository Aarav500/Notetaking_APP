import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Default settings
const defaultSettings = {
  // Appearance settings
  theme: 'system', // 'light', 'dark', or 'system'
  fontSize: 'medium', // 'small', 'medium', or 'large'
  codeBlockTheme: 'github', // 'github', 'vscode', 'dracula', 'monokai'
  
  // Notification settings
  emailNotifications: true,
  reminderNotifications: true,
  updateNotifications: true,
  notificationChannels: {
    email: true,
    browser: true,
    desktop: false,
  },
  
  // Privacy settings
  shareUsageData: false,
  storeSearchHistory: true,
  
  // Data management settings
  autoBackup: true,
  backupFrequency: 'weekly', // 'daily', 'weekly', 'monthly'
  
  // Editor settings
  autoSave: true,
  autoSaveInterval: 30, // seconds
  spellCheck: true,
  
  // Visualization settings
  defaultVisualizationType: 'mindmap', // 'mindmap', 'flowchart', 'timeline', 'knowledge_graph', 'treegraph'
  visualizationColors: 'default', // 'default', 'pastel', 'vibrant', 'monochrome'
  
  // Search settings
  searchResultsPerPage: 10,
  includeContentInSearch: true,
  includeTagsInSearch: true,
};

// Mock user data
const mockUser = {
  id: 'user-1',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatar: 'https://via.placeholder.com/150',
  joinDate: '2025-01-15',
  role: 'user', // 'user', 'admin'
  isAuthenticated: true,
};

const useSettingsStore = create(
  persist(
    (set, get) => ({
      // User state
      user: mockUser,
      isAuthenticated: true, // For demo purposes, set to true
      
      // Settings state
      settings: defaultSettings,
      
      // User actions
      login: (credentials) => {
        // In a real app, this would call an API to authenticate
        // For now, we'll just simulate a successful login
        
        set({ 
          user: mockUser,
          isAuthenticated: true 
        });
        
        return true; // Login success
      },
      
      logout: () => {
        set({ 
          user: { ...mockUser, isAuthenticated: false },
          isAuthenticated: false 
        });
      },
      
      register: (userData) => {
        // In a real app, this would call an API to register a new user
        // For now, we'll just simulate a successful registration
        
        const newUser = {
          id: `user-${Date.now()}`,
          name: userData.name,
          email: userData.email,
          avatar: 'https://via.placeholder.com/150',
          joinDate: new Date().toISOString().split('T')[0],
          role: 'user',
          isAuthenticated: true,
        };
        
        set({ 
          user: newUser,
          isAuthenticated: true 
        });
        
        return true; // Registration success
      },
      
      updateUserProfile: (updatedData) => {
        const { user } = get();
        
        set({ 
          user: { 
            ...user, 
            ...updatedData 
          } 
        });
        
        return true; // Update success
      },
      
      // Settings actions
      updateSettings: (updatedSettings) => {
        const { settings } = get();
        
        set({ 
          settings: { 
            ...settings, 
            ...updatedSettings 
          } 
        });
        
        return true; // Update success
      },
      
      resetSettings: () => {
        set({ settings: defaultSettings });
        return true; // Reset success
      },
      
      // Theme settings
      setTheme: (theme) => {
        const { settings } = get();
        
        // Apply theme to document
        const root = window.document.documentElement;
        root.classList.remove('light', 'dark');
        
        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
          root.classList.add(systemTheme);
        } else {
          root.classList.add(theme);
        }
        
        set({ 
          settings: { 
            ...settings, 
            theme 
          } 
        });
        
        return theme;
      },
      
      // Font size settings
      setFontSize: (fontSize) => {
        const { settings } = get();
        
        // Apply font size to document
        const root = window.document.documentElement;
        root.classList.remove('text-sm', 'text-base', 'text-lg');
        
        switch (fontSize) {
          case 'small':
            root.classList.add('text-sm');
            break;
          case 'medium':
            root.classList.add('text-base');
            break;
          case 'large':
            root.classList.add('text-lg');
            break;
          default:
            root.classList.add('text-base');
        }
        
        set({ 
          settings: { 
            ...settings, 
            fontSize 
          } 
        });
        
        return fontSize;
      },
      
      // Toggle settings
      toggleSetting: (settingKey) => {
        const { settings } = get();
        
        if (settingKey in settings) {
          const updatedSettings = { 
            ...settings, 
            [settingKey]: !settings[settingKey] 
          };
          
          set({ settings: updatedSettings });
          return updatedSettings[settingKey];
        }
        
        return null; // Setting not found
      },
      
      // Notification channel settings
      toggleNotificationChannel: (channel) => {
        const { settings } = get();
        
        if (channel in settings.notificationChannels) {
          const updatedChannels = { 
            ...settings.notificationChannels, 
            [channel]: !settings.notificationChannels[channel] 
          };
          
          set({ 
            settings: { 
              ...settings, 
              notificationChannels: updatedChannels 
            } 
          });
          
          return updatedChannels[channel];
        }
        
        return null; // Channel not found
      },
      
      // Export settings
      exportSettings: () => {
        return get().settings;
      },
      
      // Import settings
      importSettings: (importedSettings) => {
        // Validate imported settings
        const validSettings = {};
        
        // Only import keys that exist in defaultSettings
        Object.keys(defaultSettings).forEach(key => {
          if (key in importedSettings) {
            validSettings[key] = importedSettings[key];
          }
        });
        
        const { settings } = get();
        
        set({ 
          settings: { 
            ...settings, 
            ...validSettings 
          } 
        });
        
        return true; // Import success
      },
      
      // Reset store (for testing)
      resetStore: () => {
        set({ 
          user: { ...mockUser, isAuthenticated: false },
          isAuthenticated: false,
          settings: defaultSettings
        });
      }
    }),
    {
      name: 'settings-storage', // Name for localStorage
      partialize: (state) => ({ 
        settings: state.settings,
        isAuthenticated: state.isAuthenticated,
        // Don't store sensitive user data in localStorage
        user: state.isAuthenticated ? {
          id: state.user.id,
          name: state.user.name,
          email: state.user.email,
          avatar: state.user.avatar,
          role: state.user.role,
          isAuthenticated: state.user.isAuthenticated,
        } : null,
      }),
    }
  )
);

// Initialize theme based on stored settings
const initializeTheme = () => {
  const { settings } = useSettingsStore.getState();
  const theme = settings.theme;
  
  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');
  
  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
    root.classList.add(systemTheme);
  } else {
    root.classList.add(theme);
  }
};

// Initialize font size based on stored settings
const initializeFontSize = () => {
  const { settings } = useSettingsStore.getState();
  const fontSize = settings.fontSize;
  
  const root = window.document.documentElement;
  root.classList.remove('text-sm', 'text-base', 'text-lg');
  
  switch (fontSize) {
    case 'small':
      root.classList.add('text-sm');
      break;
    case 'medium':
      root.classList.add('text-base');
      break;
    case 'large':
      root.classList.add('text-lg');
      break;
    default:
      root.classList.add('text-base');
  }
};

// Initialize settings when the module is imported
if (typeof window !== 'undefined') {
  initializeTheme();
  initializeFontSize();
}

export default useSettingsStore;